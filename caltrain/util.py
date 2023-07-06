from __future__ import annotations

import pdb
import re
from datetime import timezone

import pandas as pd

from dateutil import parser, tz

from .constants import GM


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
    line_type = one_vehicle_dict["MonitoredVehicleJourney"]["PublishedLineName"]
    stop_data = one_vehicle_dict["MonitoredVehicleJourney"]["OnwardCalls"]["OnwardCall"]
    return pd.DataFrame([stop | {"vehicle_id": vehicle_id, "line_type": line_type} for stop in stop_data])


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


def delete_caltrain_emails():
    [msg.trash() for msg in GM.get_messages(query="subject:(caltrain status)")]
