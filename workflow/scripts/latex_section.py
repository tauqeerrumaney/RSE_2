"""
This script generates a basic LaTeX document based on research results
and outputs it as a PDF or LaTeX file.

Usage:
    Run the script from the command line with optional arguments
    for the output file names, section title, text, image, and json:

    python latex_section.py output.tex “Section Title” [--textin TEXTIN]
    [--imagein IMAGEIN] [--jsonin JSONIN]

Example:
    ```
    python latex_section.py  "Section Title"  --textin "path/to/textfile.txt"
    --imagein "path/to/image.png" --jsonin "path/to/jsonfile.json"
    ```

Options:
    outfile (str): Path to the output .tex file.
    section (str): The title of the section.
    --textin (str, optional): Path to the text file containing the description.
      Default is None.
    --imagein (str, optional): Path to the image file. Default is None.
    --jsonin (str, optional): Path to the JSON file containing additional data.
    Default is None.

Files:
    outfile: The output file where the LaTeX document will be saved.
    --textin (optional): The input text file containing the description.
    --imagein (optional): The input image file to be included in the document.
    --jsonin (optional): The input JSON file containing additional data.

Functions:
    main(outfile, section, textin=None, imagein=None, jsonin=None):
        Generate a LaTeX section with the given content.
    dict_text(dictin):
        Extract key-value pairs of dictionary into a string.
"""

import argparse
import json
import os
import traceback

from pylatex import Document, Figure, Package, Section, Subsection
from pylatex.utils import NoEscape

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))

# Define rules for processing JSON data
DATA_PROCESSING_RULES = {
    "max_var_band": lambda data: f"Max Variability Band: {data}.\n\n",
    "variability": lambda data: "\n".join(
        [
            (
                f"{key}: {data[key]:.4e}"
                if isinstance(data[key], float)
                else f"{key}: {data[key]}"
            )
            for key in data
        ]
    ),
}


def main(
    outfile: str,
    section: str,
    textin: str = None,
    imagein: str = None,
    jsonin: str = None,
):
    """
    Generate a LaTeX section with the given content.

    This function creates a LaTeX document with a specified section title,
    including optional text, an image, and JSON data.

    Args:
        outfile (str): Path to the output file where the generated
        LaTeX will be saved.
        section (str): The section title.
        textin (str):  Path to the text file to be included.
        imagein (str): Path to the image file to be included.
        jsonin (str): Path to the JSON file to be included.

    Returns:
        None

    Raises:
        TypeError: If the input parameters are not of the expected types.
        ValueError: If the output directory does not exist or no content is
            provided.
    """
    # Validate input types
    if not isinstance(outfile, str):
        raise TypeError(
            f"Expected 'outfile' to be of type str, but got "
            f"{type(outfile).__name__}"
        )
    if not isinstance(section, str):
        raise TypeError(
            f"Expected 'section' to be of type str, but got "
            f"{type(section).__name__}"
        )
    if textin is not None and not isinstance(textin, str):
        raise TypeError(
            f"Expected 'textin' to be of type str, but got "
            f"{type(textin).__name__}"
        )
    if imagein is not None and not isinstance(imagein, str):
        raise TypeError(
            f"Expected 'imagein' to be of type str, but got "
            f"{type(imagein).__name__}"
        )
    if jsonin is not None and not isinstance(jsonin, str):
        raise TypeError(
            f"Expected 'jsonin' to be of type str, but got "
            f"{type(jsonin).__name__}"
        )
    if not any([textin, imagein, jsonin]):
        raise ValueError("Please provide at least one piece of valid content.")

    # Validate output file
    out_path = get_path(outfile)
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        raise ValueError(f"Output directory does not exist: {out_dir}")

    # If out_path is a .tex file remove the extension
    if out_path.endswith(".tex"):
        out_path = out_path.split(".tex")[0]

    # Create a new document
    doc = Document("basic")

    # Add packages
    doc.packages.append(Package("float"))
    doc.packages.append(Package("graphicx"))
    doc.packages.append(Package("subfiles"))

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
                        pic.add_image(
                            image_path, width=NoEscape(r"\textwidth")
                        )
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
                        for key, rule in DATA_PROCESSING_RULES.items():
                            if key in data:
                                doc.append(rule(data[key]))
                            else:
                                absentKeys.append(key)
                        if absentKeys:
                            logger.warn(
                                f"Could not find rule to process keys: "
                                f"{absentKeys}"
                            )
                    logger.info(f"JSON '{jsonin}' added")
                else:
                    logger.error(f"JSON '{jsonin}' not found")
        logger.info(f"Section '{section}' added")

    # Generate LaTeX
    doc.generate_tex(out_path)
    logger.info(f"LaTeX generated successfully at {out_path}")


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
    try:
        main(
            args.outfile,
            args.section,
            args.textin,
            args.imagein,
            args.jsonin,
        )
    except (TypeError, ValueError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
