from __future__ import annotations

import os
import pdb

import numpy as np

import pandas as pd
import requests

from labtools.util.ipython import copy_environment_to_ipython

from constants import (
    API_TRAIN_TIME_COLS,
    CALTRAIN_OPERATOR_ID,
    DESTINATION_NAMES,
    GM,
    ID2NAME,
    MAP_TO_AVAILABLE_STATION,
    MINUTES_FROM_PRE_SF_STOP_NORTHWARD,
    MINUTES_FROM_PRE_SF_STOP_SOUTHWARD,
    MY_TRAIN_TIME_COLS,
    RWC_CALTRAIN_STOP_ID,
    SF_CALTRAIN_STOP_ID,
    TWENTY_SECOND_CALTRAIN_STOP_ID,
)
from util import (
    convert_time_str_to_local_tz_timestamp,
    format_for_display,
    one_vehicle_activity_to_stops_with_vehicle_id,
    replace_colnames,
)


class RwcSfTrains:
    def __init__(self, direction: str, api_key: str = os.environ["CALTRAIN_API_KEY"]):
        """
        Produce a dataframe giving upcoming trains with rwc stops that go between rwc & sf with
            `get_next_sf_trips_from_rwc` method

        code flow:
        1. Get live data from the 511 api
        2. Filter the departures response to trains that stop at RWC via departures_response_to_next_trains_stopping_at_rwc
        3.

        api docs:
        https://511.org/sites/default/files/2022-11/511%20SF%20Bay%20Open%20Data%20Specification%20-%20Transit.pdf
        """
        self.direction = direction
        self.api_key = api_key
        self.my_departure_station_name, self.my_destination_station_name = [
            "Redwood City Caltrain Station",
            "San Francisco Caltrain Station",
        ][:: 1 if (self.direction == "north") else -1]
        self.my_departure_station_id, self.my_destination_station_id = ["redwood_city", "san_francisco"][
            :: 1 if (self.direction == "north") else -1
        ]

        # 22nd Street Caltrain Station

        self.real_time_response = None
        self.departures_response = None
        self._trains_with_departure_stop = self.departures_response_to_next_trains_stopping_at_station(
            self.my_departure_station_id
        )
        self._trains_with_destination_stop = self.departures_response_to_next_trains_stopping_at_station(
            self.my_destination_station_id
        )

    def _get_sf_arrival_from_last_north_stop_with_live(self, arrival_df: pd.DataFrame) -> pd.DataFrame:
        """
        gets SF arrival estimate from northernmost stop. Requires live map, which is broken after switch to electric
        trains. Can't remember why live was used, but maybe it can look further into the future than the alternative
        method
        """
        while not len(arrival_df):
            arrival_df = self.estimate_sf_stop_from_last_north_stop(
                self.departures_response_to_next_trains_stopping_at_station("22nd_street"), include_last_stop=False
            ).rename(
                columns={
                    "stop_name": "arrival_stop",
                    "time_late": "late_arriving",
                    "scheduled_departure": "scheduled_arrival",
                }
            )
        return arrival_df

    def _get_sf_arrival_from_last_north_stop_with_departures(self, arrival_df: pd.DataFrame):
        for station_name, time_to_sf in MINUTES_FROM_PRE_SF_STOP_NORTHWARD.items():
            candidate_station_id = {v: k for k, v in ID2NAME.items()}.get(station_name)
            if candidate_station_id is None:
                continue
            arrival_df = self.departures_response_to_next_trains_stopping_at_station(candidate_station_id).rename(
                columns={
                    "stop_name": "arrival_stop",
                    "time_late": "late_arriving",
                    "scheduled_departure": "scheduled_arrival",
                }
            )
            matching_stops = (arrival_df.arrival_stop == station_name) | (
                arrival_df.arrival_stop == station_name + " Northbound" if self.direction == "north" else " Southbound"
            )
            if matching_stops.any():
                arrival_df.loc[
                    lambda df: matching_stops,
                    :,
                ] = arrival_df.loc[lambda df: matching_stops, :].assign(
                    scheduled_arrival=lambda df: df.scheduled_arrival + pd.Timedelta(time_to_sf * 60, "s"),
                    expected_departure=lambda df: df.expected_departure + pd.Timedelta(time_to_sf * 60, "s"),
                )
                return arrival_df
        if arrival_df is None or arrival_df.empty:
            raise ValueError("failed get estimate sf arrival from last north stop with departures")

    def next_train_options(self) -> pd.io.formats.style.Styler:
        departure_df = self.departures_response_to_next_trains_stopping_at_station(self.my_departure_station_id).rename(
            columns={
                "stop_name": "departure_stop",
                "time_late": "late_departing",
            }
        )
        arrival_df = self.departures_response_to_next_trains_stopping_at_station(self.my_destination_station_id).rename(
            columns={
                "stop_name": "arrival_stop",
                "time_late": "late_arriving",
                "scheduled_departure": "scheduled_arrival",
            }
        )
        if self.my_destination_station_id == "san_francisco" and arrival_df.empty:
            try:
                arrival_df = self._get_sf_arrival_from_last_north_stop_with_live(arrival_df.copy())
            except (KeyError, ValueError):
                arrival_df = self._get_sf_arrival_from_last_north_stop_with_departures(arrival_df.copy())
        return (
            pd.merge(
                departure_df,
                arrival_df,
                on="vehicle_id",
            )
            .loc[:, lambda df: [x for x in df.columns if "expected" not in x]]
            .assign(
                scheduled_departure=lambda df: pd.to_datetime(df.scheduled_departure),
                scheduled_arrival=lambda df: pd.to_datetime(df.scheduled_arrival),
                travel_time=lambda df: df.scheduled_arrival - df.scheduled_departure,
            )[
                [
                    "departure_stop",
                    "arrival_stop",
                    "scheduled_departure",
                    "late_departing",
                    "scheduled_arrival",
                    "late_arriving",
                    "travel_time",
                ]
            ]
            .pipe(format_for_display)
        )

    @property
    def trains_with_departure_stop(self):
        if self._trains_with_departure_stop is None:
            self._trains_with_departure_stop = self.departures_response_to_next_trains_stopping_at_station(
                self.my_departure_station_id
            )
        return self._trains_with_departure_stop

    @property
    def trains_with_destination_stop(self):
        if self._trains_with_destination_stop is None:
            self._trains_with_destination_stop = self.departures_response_to_next_trains_stopping_at_station(
                self.my_destination_station_id
            )
        return self._trains_with_destination_stop

    def get_trains_one_direction_from_departures_response(self, stop_id: str = RWC_CALTRAIN_STOP_ID) -> list[dict]:
        if self.departures_response is None:
            self.fetch_data()
        destinations = DESTINATION_NAMES[self.direction]
        filtered_departures_response = [
            x
            for x in self.departures_response[stop_id]["ServiceDelivery"]["StopMonitoringDelivery"][
                "MonitoredStopVisit"
            ]
            if x["MonitoredVehicleJourney"]["DestinationName"] in destinations
        ]
        if not filtered_departures_response:
            returned_destination_stations = set(
                [
                    x["MonitoredVehicleJourney"]["DestinationName"]
                    for x in self.departures_response[stop_id]["ServiceDelivery"]["StopMonitoringDelivery"][
                        "MonitoredStopVisit"
                    ]
                ]
            )
            msg = f"No trains are going to destinations with names {destinations}\n"
            if returned_destination_stations:
                msg += "Response stations include only" + str(returned_destination_stations)
            else:
                msg += "No destination stations returned; names have changed multiple times in the past, api may have changed specs as well."
            raise RuntimeError(msg)
        else:
            return filtered_departures_response

    def fetch_data(self) -> RwcSfTrains:
        """hits the api to get departure schedule, predictions"""
        stops_to_request = [RWC_CALTRAIN_STOP_ID, SF_CALTRAIN_STOP_ID, TWENTY_SECOND_CALTRAIN_STOP_ID]
        departure_prediction_request = {
            stop_id: f"http://api.511.org/transit/StopMonitoring?api_key={self.api_key}&agency=CT&stop={stop_id}"
            for stop_id in stops_to_request
        }
        self.departures_response = {
            stop_id: self.request_to_dict(departure_prediction_request[stop_id]) for stop_id in stops_to_request
        }

        self.real_time_response = self.request_to_dict(
            f"http://api.511.org/transit/VehicleMonitoring?api_key={self.api_key}&agency={CALTRAIN_OPERATOR_ID}"
        )
        return self

    def all_rwc_trains_and_onward_stops(self):
        if self.departures_response is None:
            self.fetch_data()
        missing_train_ids = set(
            [
                x
                for x in self.trains_with_departure_stop.vehicle_id
                if x not in self.get_vehicle_onward_stops().vehicle_id.values
            ]
        )
        if missing_train_ids:
            print(
                f"train{'s' if len(missing_train_ids) >1 else ''} {missing_train_ids} not in the realtime response :thunk:"
            )
        return (
            self.trains_with_departure_stop.merge(
                self.get_vehicle_onward_stops().rename(
                    columns={
                        "expected_departure": "expected_departure_onward_stop",
                        "scheduled_departure": "scheduled_departure_onward_stop",
                        "stop_name": "stop_name_onward_stop",
                    }
                ),
                on="vehicle_id",
                how="left",
            )
            .drop(columns=["vehicle_id"])
            .assign(
                trip_duration_from_origin=lambda df: (
                    (df.expected_departure_onward_stop - df.expected_departure)
                    if "expected_departure" in df.columns
                    else (df.expected_arrival_onward_stop - df.expected_arrival)
                )
            )
            .pipe(format_for_display)
        )

    def get_next_sf_trips_from_rwc(self):
        return (
            self.all_rwc_trains_and_onward_stops()
            .data.loc[
                lambda df: (
                    df["stop name onward stop"].apply(lambda x: x in ["San Francisco Caltrain Station", np.nan])
                    if self.direction == "north"
                    else df["stop name onward stop"].apply(lambda x: x in ["Redwood City Caltrain Station", np.nan])
                ),
                :,
            ]
            .pipe(format_for_display)
        )

    @classmethod
    def request_to_dict(self, request) -> None:
        response = requests.get(request)
        response.encoding = "utf-8-sig"
        return response.json()

    def convert_predicted_stops_json_to_df(self, trains, stop_name: str) -> pd.DataFrame:
        predicted_stops = convert_time_str_to_local_tz_timestamp(
            replace_colnames(
                pd.DataFrame(
                    [
                        x["MonitoredVehicleJourney"]["MonitoredCall"]
                        | {
                            "VehicleRef": x["MonitoredVehicleJourney"]["FramedVehicleJourneyRef"][
                                "DatedVehicleJourneyRef"
                            ]
                        }
                        for x in trains
                    ]
                )
            ),
            MY_TRAIN_TIME_COLS,
        )
        if (
            "San Francisco Caltrain Station" in stop_name
            and not predicted_stops.stop_name.str.contains("San Francisco Caltrain Station").any()
        ):
            predicted_stops = self.estimate_sf_stop_from_last_north_stop(predicted_stops).loc[
                lambda df: "San Francisco Caltrain Station" in df.stop_name
            ]
        return predicted_stops

    def assign_time_late(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[["stop_name", "vehicle_id", "scheduled_departure", "expected_departure"]].assign(
            time_late=lambda df: df.expected_departure - df.scheduled_departure
        )

    def departures_response_to_next_trains_stopping_at_station(self, stop_id: str = None) -> None:
        """
        Assigns result to _trains_with_departure_stop attr

        steps:
        1. start w/ departures response
        2. reduce to trains going north or south
        3. reduce to trains with specific stop
        """
        # only if stopping at rwc and going <north|south>
        all_trains_one_direction = self.get_trains_one_direction_from_departures_response(stop_id)
        station_departures = self.convert_predicted_stops_json_to_df(
            all_trains_one_direction,
            ID2NAME[stop_id],
        )
        # Filter to trains stopping at station
        station_departures_filtered = station_departures.loc[
            lambda df: df.stop_name
            == (
                MAP_TO_AVAILABLE_STATION[ID2NAME[stop_id]]
                + (" Northbound" if self.direction == "north" else " Southbound")
            )
        ].copy()

        # return station_departures, all_trains_one_direction
        station_departures_filtered = convert_time_str_to_local_tz_timestamp(
            station_departures_filtered,
            time_cols=(
                MY_TRAIN_TIME_COLS if np.any(["_" in x for x in station_departures.columns]) else API_TRAIN_TIME_COLS
            ),
        )
        return self.assign_time_late(station_departures_filtered)

    def get_vehicle_onward_stops(self) -> pd.DataFrame:
        """
        Returns a df with cols ['stop_name', 'scheduled_arrival', 'expected_arrival', 'vehicle_id'] for all active trains

        adjusts time by 6 minutes if ending is sf, because it doesn't return San Francisco Caltrain Station data
        """
        #  list of all currently traveling caltrain vehicles
        try:
            vehicle_activity = self.real_time_response["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][
                "VehicleActivity"
            ]
        except KeyError as e:
            e.penultimate_data = self.real_time_response["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"]
            e.add_note(f"got only:\n\n{e.penultimate_data}\n\nThis penultimate response is in e.penultimate_data")
            raise KeyError(
                "511.org api did not return live tracking for onward stops  in the vehicle monitoring delivery response,"
            ) from e

        # filter to trains stopping in RWC
        rwc_stopping_vehicle_activity = [
            x
            for x in vehicle_activity
            if x["MonitoredVehicleJourney"]["FramedVehicleJourneyRef"]["DatedVehicleJourneyRef"]
            in self.trains_with_departure_stop.vehicle_id.values
        ]
        if not rwc_stopping_vehicle_activity:
            msg = (
                "No intersection between trains stopping at the departure station and those in the real time data.\n"
                + f"trains of interest: {self.trains_with_departure_stop.vehicle_id.unique()}\n"
                + f"Trains in live data: {[x['MonitoredVehicleJourney']['FramedVehicleJourneyRef']['DatedVehicleJourneyRef'] for x in vehicle_activity]}"
            )
            raise ValueError(msg)

        # concatenate a list of dfs describing coming stops for every train that stops in RWC
        next_stops_for_rwc_stopping_trains = pd.concat(
            [
                one_vehicle_activity_to_stops_with_vehicle_id(one_vehicle_dict)
                for one_vehicle_dict in rwc_stopping_vehicle_activity
            ]
        )[["StopPointName", "AimedDepartureTime", "ExpectedDepartureTime", "vehicle_id", "line_type"]]

        next_stops_for_rwc_stopping_trains = convert_time_str_to_local_tz_timestamp(
            next_stops_for_rwc_stopping_trains, ["AimedDepartureTime", "ExpectedDepartureTime"]
        )
        munged = replace_colnames(next_stops_for_rwc_stopping_trains)
        if self.direction == "north":
            return self.estimate_sf_stop_from_last_north_stop(munged)
        else:
            return munged

    def estimate_sf_stop_from_last_north_stop(self, df: pd.DataFrame, include_last_stop: bool = True) -> pd.DataFrame:
        return df.groupby("vehicle_id", as_index=False).apply(
            self.estimate_sf_stop_from_last_north_stop_one_train, include_last_stop
        )

    def estimate_sf_stop_from_last_north_stop_one_train(self, df: pd.DataFrame, include_last_stop=True) -> pd.DataFrame:

        if (df.stop_name == "San Francisco Caltrain Station").any():
            return df
        else:
            row_to_mutate = df.loc[
                lambda df: df.scheduled_departure
                == df.scheduled_departure.agg("min" if (self.direction == "south") else "max"),
                :,
            ]
            stop_time_map = (
                MINUTES_FROM_PRE_SF_STOP_NORTHWARD if self.direction == "north" else MINUTES_FROM_PRE_SF_STOP_SOUTHWARD
            )
            last_stop_name = row_to_mutate.stop_name.values[0]
            minutes_offset = stop_time_map[last_stop_name]
            return (
                df.pipe(
                    lambda df: pd.concat(
                        [
                            (df if include_last_stop else pd.DataFrame([])),
                            row_to_mutate.replace(
                                last_stop_name,
                                "San Francisco Caltrain Station",
                            ).assign(
                                scheduled_departure=lambda df: df["scheduled_departure"]
                                + (pd.Timedelta(f"{minutes_offset} minutes")),
                                expected_departure=lambda df: df["expected_departure"]
                                + (pd.Timedelta(f"{minutes_offset} minutes")),
                            ),
                        ],
                        axis=0,
                    )
                )
                .sort_values("scheduled_departure")
                .loc[lambda df: (df["arrival_stop"] == "San Francisco Caltrain Station") | include_last_stop, :]
            )

    # def estimate_sf_stop_from_22nd_st_stop(self, df: pd.DataFrame, include_22nd=True) -> pd.DataFrame:
    #     """Must include columns scheduled_arrival and expected_arrival"""
    #     sign = 1 if self.direction == "north" else -1
    #     if "vehicle_id" not in df.columns:
    #         df = df.assign(vehicle_id=1)
    #         cols_to_drop = ["vehicle_id"]
    #     else:
    #         cols_to_drop = []

    #     return (
    #         df.groupby("vehicle_id", group_keys=False)
    #         .apply(
    #             lambda df: pd.concat(
    #                 [
    #                     (df if include_22nd else pd.DataFrame([])),
    #                     df.loc[lambda df: df.stop_name == "22nd Street Caltrain Station", :]
    #                     .replace("22nd Street Caltrain Station", "San Francisco Caltrain Station")
    #                     .assign(
    #                         scheduled_departure=lambda df: df["scheduled_departure"] + (sign * pd.Timedelta("6 minutes")),
    #                         expected_departure=lambda df: df["expected_departure"] + (sign * pd.Timedelta("6 minutes")),
    #                     ),
    #                 ],
    #                 axis=0,
    #             )
    #         )
    #         .drop(columns=cols_to_drop)
    #     )

    def send_next_options_to_inbox(self) -> None:
        params = {
            "to": "alex.hakso@gmail.com",
            "sender": "alex.hakso@gmail.com",
            "subject": "caltrain status",
            "msg_html": self.next_train_options().to_html(index=False),
            "msg_plain": str(self.next_train_options().data),
            "signature": True,  # use my account signature
        }
        GM.send_message(**params)
