import pandas as pd
import os
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# let these be specified by argparse in the main file
file_name = "raw_data_EPOC.txt"
MOCK = True
# also specify file type to which will be saved?

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, f"../data/{file_name}")

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
logger.info("Finished reading data")

try:
    if MOCK:
        out_path = os.path.join(current_dir, "../data/raw_data_MOCK.feather")
        df_mock = df.head(10000)
        df_mock.to_feather(out_path)
        logger.info("Mock file saved")
    else:
        out_path = os.path.join(current_dir, "../data/raw_data_EPOC.feather")
        df.to_feather(out_path)
        logger.info("Raw file saved")
except Exception as e:
    logger.error("An error occurred: %s", traceback.format_exc())
