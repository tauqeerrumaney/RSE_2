"""
This script generates a basic LaTeX document based on research results
and outputs it as a PDF or LaTeX file.

Usage:
    Run the script from the command line with optional arguments
    for the output file names, section title, text, image, and json:
    ```
    python generate_latex_section.py
    output.tex "Section Title"
    --textin "path/to/textfile.txt"
    --imagein "path/to/image.png"
    --jsonin "path/to/jsonfile.json"
    ```

Functions:
    main(outfile, section, textin, imagein, jsonin)
        Generate a LaTeX section with the given content.
    extract_dict(indict)
        Extract key-value pairs of dictionary into string.

Command-Line Arguments:
    outfile (str): The path to the output .tex file.
    section (str): The title of the section.
    --textin (str): The path to the text file containing the description.
    --imagein (str): The path to the image file.
    --jsonin (str): The path to the JSON file containing additional data.
"""

from pylatex import Document, Section, Subsection, Figure, Package
import json
import argparse
import os

from utils import get_path
from logger import configure_logger

logger = configure_logger(os.path.basename(__file__))

# Define rules for processing keys globally
processing_rules = {
    "max_var_band": lambda data: f"Max Variability Band: {data}\n\n",
    "variability": lambda data: f"Calculated Variability \n{dict_str(data)}\n",
}


def dict_str(indict: dict):
    """
    Extracts key-value pairs from a dictionary
    and returns them as a formatted string.

    Args:
        indict (dict): The input dictionary.

    Returns:
        str: A formatted string containing the
            key-value pairs from the input dictionary.
    """
    outtext = ""
    try:
        if type(indict) is dict:
            for key in indict:
                outtext += f"{key}: {round(indict[key], 6)}\n"
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return outtext


def main(outfile, section, textin, imagein, jsonin):
    """
    Generate a LaTeX section with the given content.

    Args:
        outfile (str): The output file path for the generated LaTeX.
        section (str): The section title.
        text (str): The path to the text file to be included in the section.
        image (str): The path to the image file to be included in the section.
        json (str): The path to the JSON file to be included in the section.

    Returns:
        None
    """

    # Create a new document
    doc = Document("basic")

    # Add packages
    doc.packages.append(Package("float"))
    doc.packages.append(Package("graphicx"))
    doc.packages.append(Package("subfiles"))

    # Check if there is content to add to section
    if not any([imagein, jsonin, textin]):
        logger.error("Please provide at least one piece of valid content.")
        return

    with doc.create(Section(section)):

        if textin is not None:
            with doc.create(Subsection("Description")):
                # Try to add text from textblock
                text_path = get_path(textin)
                if os.path.exists(text_path):
                    # Add text
                    doc.append(open(text_path).read())
                    logger.info(f"Text from '{textin}' added")
                else:
                    logger.error(f"Text '{textin}' not found")

        with doc.create(Subsection("Results")):

            # check if image was created
            if imagein is not None:
                image_path = get_path(imagein)
                if os.path.exists(image_path):
                    # Add figure
                    with doc.create(Figure(position="H")) as pic:
                        pic.add_image(image_path, width="120px")
                        pic.add_caption(imagein)
                    logger.info(f"Image '{imagein}' added")
                else:
                    logger.error(f"Image '{imagein}' not found")

            # check if json was created
            if jsonin is not None:
                json_path = get_path(jsonin)
                if os.path.exists(json_path):
                    # Add json content
                    with open(json_path, "r") as f:
                        data = json.load(f)
                        absentKeys = []
                        for key, rule in processing_rules.items():
                            if key in data:
                                doc.append(rule(data[key]))
                            else:
                                absentKeys.append(key)
                        if absentKeys:
                            logger.info(f"Missing keys in JSON: {absentKeys}")
                    logger.info(f"JSON '{jsonin}' added")
                else:
                    logger.error(f"JSON '{jsonin}' not found")
        logger.info(f"Section '{section}' added")

    # Generate LaTeX
    try:
        if not outfile.endswith(".tex"):
            outfile = f"{outfile}.tex"
        doc.generate_tex(
            get_path(outfile).split(".tex")[0],
        )
        logger.info(f"LaTeX generated successfully at {outfile}")
    except FileNotFoundError as fnfe:
        logger.error(f"FileNotFoundError: {fnfe}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return


if __name__ == "__main__":
    USAGE = "Generate a LaTeX section with the given content."
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "outfile",
        type=str,
        help="The path to the output PDF file",
    )
    parser.add_argument(
        "section",
        type=str,
        help="Section Title",
        default="Section",
    )
    parser.add_argument(
        "--textin",
        type=str,
        help="The keyword to add textblock",
        default=None,
    )
    parser.add_argument(
        "--imagein",
        type=str,
        default=None,
        help="The path to an image",
    )
    parser.add_argument(
        "--jsonin",
        type=str,
        default=None,
        help="The path to a json input",
    )

    args = parser.parse_args()

    main(
        args.outfile,
        args.section,
        args.textin,
        args.imagein,
        args.jsonin,
    )
