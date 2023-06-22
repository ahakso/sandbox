from __future__ import annotations

import os
import pdb
import re
from datetime import timezone

import numpy as np
import pandas as pd

import requests
from dateutil import parser, tz

API_TRAIN_TIME_COLS = [
    "AimedArrivalTime",
    "ExpectedArrivalTime",
    "AimedDepartureTime",
    "ExpectedDepartureTime",
]
MY_TRAIN_TIME_COLS = [
    "scheduled_arrival",
    "expected_arrival",
    "scheduled_departure",
    "expected_departure",
]

CALTRAIN_OPERATOR_ID = "CT"
RWC_CALTRAIN_STOP_ID = "redwood_city"
TWENTY_SECOND_CALTRAIN_STOP_ID = "22nd_street"
SF_CALTRAIN_STOP_ID = "san_francisco"

ID2NAME = {
    "san_francisco": "San Francisco Caltrain Station",
    "22nd_street": "22nd Street Caltrain Station",
    "redwood_city": "Redwood City Caltrain Station",
}

MAP_TO_AVAILABLE_STATION = {
    "22nd Street Caltrain Station": "22nd Street Caltrain Station",
    "San Francisco Caltrain Station": "22nd Street Caltrain Station",
    "Redwood City Caltrain Station": "Redwood City Caltrain Station",
    "San Francisco Caltrain Station": "San Francisco Caltrain Station",
}


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
        self.my_departure_station_id, self.my_destination_station_id = ["redwood_city", "san_francisco"][:: 1 if (self.direction == "north") else -1]

        # 22nd Street Caltrain Station

        self.real_time_response = None
        self.departures_response = None
        self._trains_with_departure_stop = self.departures_response_to_next_trains_stopping_at_station(self.my_departure_station_id)
        self._trains_with_destination_stop = self.departures_response_to_next_trains_stopping_at_station(self.my_destination_station_id)

    def next_train_options(self):
        return (
            pd.merge(
                self.departures_response_to_next_trains_stopping_at_station(self.my_departure_station_id).rename(
                    columns={
                        "stop_name": "departure_stop",
                        "time_late": "late_departing",
                    }
                ),
                self.departures_response_to_next_trains_stopping_at_station(self.my_destination_station_id).rename(
                    columns={
                        "stop_name": "arrival_stop",
                        "time_late": "late_arriving",
                        "scheduled_departure": "scheduled_arrival",
                    }
                ),
                on="vehicle_id",
            )
            .loc[:, lambda df: [x for x in df.columns if "expected" not in x]]
            .assign(travel_time=lambda df: df.scheduled_arrival - df.scheduled_departure)[
                ["departure_stop", "arrival_stop", "scheduled_departure", "late_departing", "scheduled_arrival", "late_arriving", "travel_time"]
            ]
            .pipe(format_for_display)
        )

    @property
    def trains_with_departure_stop(self):
        if self._trains_with_departure_stop is None:
            self._trains_with_departure_stop = self.departures_response_to_next_trains_stopping_at_station(self.my_departure_station_id)
        return self._trains_with_departure_stop

    @property
    def trains_with_destination_stop(self):
        if self._trains_with_destination_stop is None:
            self._trains_with_destination_stop = self.departures_response_to_next_trains_stopping_at_station(self.my_destination_station_id)
        return self._trains_with_destination_stop

    def get_trains_one_direction_from_departures_response(self, stop_id: str = RWC_CALTRAIN_STOP_ID) -> list[dict]:
        if self.departures_response is None:
            self.fetch_data()
        destinations = {"San Francisco Caltrain Station", "San Francisco"} if self.direction == "north" else {"Gilroy", "San Jose Diridon", "Tamien"}
        return [x for x in self.departures_response[stop_id]["ServiceDelivery"]["StopMonitoringDelivery"]["MonitoredStopVisit"] if x["MonitoredVehicleJourney"]["DestinationName"] in destinations]

    def fetch_data(self) -> RwcSfTrains:
        """hits the api to get departure schedule, predictions"""
        stops_to_request = [RWC_CALTRAIN_STOP_ID, SF_CALTRAIN_STOP_ID, TWENTY_SECOND_CALTRAIN_STOP_ID]
        departure_prediction_request = {stop_id: f"http://api.511.org/transit/StopMonitoring?api_key={self.api_key}&agency=CT&stop={stop_id}" for stop_id in stops_to_request}
        self.departures_response = {stop_id: self.request_to_dict(departure_prediction_request[stop_id]) for stop_id in stops_to_request}

        self.real_time_response = self.request_to_dict(f"http://api.511.org/transit/VehicleMonitoring?api_key={self.api_key}&agency={CALTRAIN_OPERATOR_ID}")
        return self

    def all_rwc_train_stops(self):
        if self.departures_response is None:
            self.fetch_data()
        missing_train_ids = set([x for x in self.trains_with_departure_stop.vehicle_id if x not in self.get_vehicle_onward_stops().vehicle_id.values])
        if missing_train_ids:
            print(f"train{'s' if len(missing_train_ids) >1 else ''} {missing_train_ids} not in the realtime response :thunk:")
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
                trip_duration_from_origin=lambda df: (df.expected_departure_onward_stop - df.expected_departure)
                if "expected_departure" in df.columns
                else (df.expected_arrival_onward_stop - df.expected_arrival)
            )
            .pipe(format_for_display)
        )

    def get_next_sf_trips_from_rwc(self):
        return (
            self.all_rwc_train_stops()
            .data.loc[
                lambda df: df["stop name onward stop"].apply(lambda x: x in ["San Francisco Caltrain Station", np.nan])
                if self.direction == "north"
                else df["stop name onward stop"].apply(lambda x: x in ["Redwood City Caltrain Station", np.nan]),
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
                pd.DataFrame([x["MonitoredVehicleJourney"]["MonitoredCall"] | {"VehicleRef": x["MonitoredVehicleJourney"]["FramedVehicleJourneyRef"]["DatedVehicleJourneyRef"]} for x in trains])
            ),
            MY_TRAIN_TIME_COLS,
        )
        if stop_name == ("San Francisco Caltrain Station") and not predicted_stops.stop_name.str.contains("San Francisco Caltrain Station").any():
            predicted_stops = self.estimate_sf_stop_from_22nd_st_stop(predicted_stops).loc[lambda df: df.stop_name == "San Francisco Caltrain Station"]
        return predicted_stops

    def assign_time_late(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[["stop_name", "vehicle_id", "scheduled_departure", "expected_departure"]].assign(time_late=lambda df: df.expected_departure - df.scheduled_departure)

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
        station_departures_filtered = station_departures.loc[lambda df: df.stop_name == MAP_TO_AVAILABLE_STATION[ID2NAME[stop_id]]]

        # return station_departures, all_trains_one_direction
        station_departures_filtered = convert_time_str_to_local_tz_timestamp(
            station_departures_filtered,
            time_cols=MY_TRAIN_TIME_COLS if np.any(["_" in x for x in station_departures.columns]) else API_TRAIN_TIME_COLS,
        )
        return self.assign_time_late(station_departures_filtered)

    def get_vehicle_onward_stops(self) -> pd.DataFrame:
        """
        Returns a df with cols ['stop_name', 'scheduled_arrival', 'expected_arrival', 'vehicle_id'] for all active trains

        adjusts time by 6 minutes if ending is sf, because it doesn't return San Francisco Caltrain Station data
        """
        #  list of all currently traveling caltrain vehicles
        vehicle_activity = self.real_time_response["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"]["VehicleActivity"]

        # filter to trains stopping in RWC
        rwc_stopping_vehicle_activity = [
            x for x in vehicle_activity if x["MonitoredVehicleJourney"]["FramedVehicleJourneyRef"]["DatedVehicleJourneyRef"] in self.trains_with_departure_stop.vehicle_id.values
        ]

        # concatenate a list of dfs describing coming stops for every train that stops in RWC
        next_stops_for_rwc_stopping_trains = pd.concat([one_vehicle_activity_to_stops_with_vehicle_id(one_vehicle_dict) for one_vehicle_dict in rwc_stopping_vehicle_activity])[
            ["StopPointName", "AimedDepartureTime", "ExpectedDepartureTime", "vehicle_id"]
        ]

        next_stops_for_rwc_stopping_trains = convert_time_str_to_local_tz_timestamp(next_stops_for_rwc_stopping_trains, ["AimedDepartureTime", "ExpectedDepartureTime"])
        munged = replace_colnames(next_stops_for_rwc_stopping_trains)
        if self.direction == "north":
            return self.estimate_sf_stop_from_22nd_st_stop(munged)
        else:
            return munged

    def estimate_sf_stop_from_22nd_st_stop(self, df: pd.DataFrame) -> pd.DataFrame:
        """Must include columns scheduled_arrival and expected_arrival"""
        sign = 1 if self.direction == "north" else -1
        if "vehicle_id" not in df.columns:
            df = df.assign(vehicle_id=1)
            cols_to_drop = ["vehicle_id"]
        else:
            cols_to_drop = []

        return (
            df.groupby("vehicle_id", group_keys=False)
            .apply(
                lambda df: pd.concat(
                    [
                        df,
                        df.loc[lambda df: df.stop_name == "22nd Street Caltrain Station", :]
                        .replace("22nd Street Caltrain Station", "San Francisco Caltrain Station")
                        .assign(
                            scheduled_departure=lambda df: df["scheduled_departure"] + (sign * pd.Timedelta("6 minutes")),
                            expected_departure=lambda df: df["expected_departure"] + (sign * pd.Timedelta("6 minutes")),
                        ),
                    ],
                    axis=0,
                )
            )
            .drop(columns=cols_to_drop)
        )

        # **{k: lambda df: df[k] + ((sign * pd.Timedelta("6 minutes"))) for k in df.columns if re.search("scheduled|expected", k)},


def convert_time_str_to_local_tz_timestamp(df: pd.DataFrame, time_cols: list[str]) -> pd.DataFrame:
    time_cols = [x for x in time_cols if x not in df.select_dtypes("datetime64[ns]").columns]
    df.loc[:, time_cols] = df.loc[:, time_cols].applymap(iso_to_timestamp)
    return df


def iso_to_timestamp(isodt_str: str) -> pd.Timestamp:
    if not isinstance(isodt_str, str):
        return isodt_str
    isodt = parser.parse(isodt_str)
    return pd.Timestamp(isodt.replace(tzinfo=timezone.utc).astimezone(tz=tz.gettz("America/Los_Angeles"))).tz_convert(tz=tz.gettz("America/Los_Angeles"))


def one_vehicle_activity_to_stops_with_vehicle_id(one_vehicle_dict: dict) -> pd.DataFrame:
    """push vehicle id down into list of stop data dicts"""
    vehicle_id = one_vehicle_dict["MonitoredVehicleJourney"]["FramedVehicleJourneyRef"]["DatedVehicleJourneyRef"]
    stop_data = one_vehicle_dict["MonitoredVehicleJourney"]["OnwardCalls"]["OnwardCall"]
    return pd.DataFrame([stop | {"vehicle_id": vehicle_id} for stop in stop_data])


def format_for_display(df):
    def time_delta_to_minutes(x: pd.Timedelta) -> callable:
        return f"{(x.seconds/60):.0f} minutes" if x.days == 0 else f"-{((-x).seconds/60):.0f} minutes"

    return df.rename(columns={k: k.replace("_", " ") for k in df.columns}).pipe(
        lambda df: df.style.format(
            {k: lambda x: x.strftime("%H:%M") if not pd.isna(x) else "-" for k in df.columns if "scheduled" in k or "expected" in k}
            | {"minutes late": "{:0.1f}"}
            | {k: time_delta_to_minutes for k in df.columns if (re.search("duration|travel|late", k))}
        )
    )


def replace_colnames(df):
    return df.rename(
        columns={
            "AimedDepartureTime": "scheduled_departure",
            "ExpectedDepartureTime": "expected_departure",
            "AimedArrivalTime": "scheduled_arrival",
            "ExpectedArrivalTime": "expected_arrival",
            "VehicleRef": "vehicle_id",
            "StopPointName": "stop_name",
        }
    )
