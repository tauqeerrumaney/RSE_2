import pandas as pd
import numpy as np
import os
import traceback
import argparse
from utils import logger, set_path


def main(args):
    file_path = set_path(args.file_name)

    # format of MindBigData data set
    columns = ["id", "event", "device", "channel", "code", "size", "signal"]
    rows = []

    logger.info("Reading data")
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split("\t")
            row_dict = {
                "id": int(parts[0]),
                "event": int(parts[1]),
                "device": parts[2],
                "channel": parts[3],
                "code": int(parts[4]),
                "size": int(parts[5]),
                "signal": list(map(float, parts[6].split(","))),
            }
            rows.append(row_dict)

    df = pd.DataFrame(rows, columns=columns)
    df.drop(columns=["device"], inplace=True)

    # this corresponds to the LSB of the resolution of the EEG device
    # emotiv.com/products/epoc-x
    conversion_factor = 0.125
    df["signal"] = df["signal"].apply(
        lambda x: np.array(x) * conversion_factor
    )

    logger.info("Finished reading data")

    try:
        if args.mock:
            out_path = set_path("raw_data_MOCK.feather")
            df_mock = df.head(10000)
            df_mock.to_feather(out_path)
            logger.info(f"Mock file saved to {out_path}")
        else:
            # save data in feather format -> smaller
            out_path = set_path("raw_data_EPOC.feather")
            df.to_feather(out_path)
            logger.info(f"Raw file saved to {out_path}")
    # TODO: handle different error types independently
    except Exception:
        logger.error("An error occurred: %s", traceback.format_exc())


if __name__ == "__main__":
    USAGE = "loading the data"  # TODO: make more precise
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "--mock",
        type=bool,
        help="use only a subset of the data",
        default=True,
    )
    parser.add_argument(
        "--file_name", "-f", type=str, help="name of the file to load", default="raw_data_EPOC.txt",
    )

    args = parser.parse_args()
    main(args)
