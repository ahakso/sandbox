from rwc_sf_trains import RwcSfTrains
import argparse
import sys
from tabulate import tabulate


def main():
    parser = argparse.ArgumentParser(description="Get next train options for Caltrain.")
    parser.add_argument("direction", choices=["north", "south"], help="Direction of the train")
    args = parser.parse_args()

    self = RwcSfTrains(args.direction)
    self.fetch_data()
    next_trains = self.next_train_options().data
    for c in ["departure", "arrival"]:
        next_trains.loc[:, c + " stop"] = next_trains.loc[:, c + " stop"].str.split(" ").apply(lambda x: x[0])
        next_trains.loc[:, "scheduled " + c] = next_trains.loc[:, "scheduled " + c].dt.strftime("%H:%m")

    for c in ["late arriving", "late departing", "travel time"]:
        next_trains.loc[:, c] = (next_trains.loc[:, c].dt.seconds / 60).apply(lambda x: f"{x:0.1f} minutes")

    print(tabulate(next_trains.T, headers=[f"option {x+1}" for x in range(next_trains.shape[0])], tablefmt="presto"))


if __name__ == "__main__":
    sys.path.append("/Users/ahakso/gd/sandbox/caltrain")
    main()
