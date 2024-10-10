from simplegmail import Gmail

GM = Gmail("/Users/ahakso/.alex_hakso_gsheets_credentials.json")

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

MINUTES_FROM_PRE_SF_STOP_NORTHWARD = {
    "22nd Street Caltrain Station": 6,
    "South San Francisco Caltrain Station": 13,
    "Millbrae Caltrain Station": 19,
}
MINUTES_FROM_PRE_SF_STOP_NORTHWARD = MINUTES_FROM_PRE_SF_STOP_NORTHWARD | {
    k + " Northbound": v for k, v in MINUTES_FROM_PRE_SF_STOP_NORTHWARD.items()
}
MINUTES_FROM_PRE_SF_STOP_SOUTHWARD = {
    "22nd Street Caltrain Station": -5,
    "South San Francisco Caltrain Station": -13,
    "Millbrae Caltrain Station": -18,
}

DESTINATION_NAMES = {
    "south": set.union(
        *[
            {x, x + " Southbound"}
            for x in [
                "Gilroy",
                "San Jose Diridon",
                "Tamien Caltrain Station",
                "Tamien",
                "San Jose Diridon Caltrain Station",
                "Tamien Caltrain Station",
            ]
        ]
    ),
    "north": set.union(*[{x, x + " Northbound"} for x in ["San Francisco Caltrain Station", "San Francisco"]]),
    # these have been renamed, but things are in the air. appending new names, but may want to clear later
}
