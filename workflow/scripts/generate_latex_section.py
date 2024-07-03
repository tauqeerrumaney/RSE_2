from pylatex import Document, Section, Subsection, Figure, Package
import argparse
import os

from utils import get_path, get_text
from logger import configure_logger


def create_section(outfile, image, json, keyword):

    # Configure logger
    logger = configure_logger()

    # Create a new document
    doc = Document("basic")

    # Add packages
    doc.packages.append(Package("float"))

    # Check if there is content to add to section
    if image is None and json is None and not found_keyword(keyword):
        logger.error("Please provide at least one piece of valid content.")
        return

    # Create Section
    section_title = keyword.replace("_", " ")
    with doc.create(Section(f"{section_title.capitalize()}")):

        with doc.create(Subsection("Description")):
            # Try to add text from textblock
            try:
                doc.append(get_text(image))
            except ValueError as ve:
                logger.error(f"ValueError: {ve}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
            logger.info(f"Description for '{section_title}' added")

        with doc.create(Subsection("Results")):
            # check if image was created
            image_path = get_path(image)
            if os.path.exists(image_path):
                # Add figure
                with doc.create(Figure(position="H")) as pic:
                    pic.add_image(image_path, width="120px")
                    pic.add_caption(image)
                logger.info(f"Image '{image}' added")
            else:
                logger.error(f"Image '{image}' not found")

            # check if json was created
            json_path = get_path(json)
            if os.path.exists(json_path):
                # Add json content
                with open(json_path, 'r') as f:
                    data = json.load(f)
                max_var_band = data["max_var_band"]
                variability = data["variability"]

                doc.append(f"Max Variability Band: {max_var_band}")
                doc.append(f"Variability: {variability}")

                logger.info(f"JSON '{json}' added")
            else:
                logger.error(f"JSON '{json}' not found")

        logger.info(f"Section '{section_title}' added")

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


def found_keyword(keyword):
    if get_text(keyword) is not False:
        return True
    else:
        return False


if __name__ == "__main__":
    USAGE = "Generate a basic LaTeX document based on the research results"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "outfile",
        type=str,
        help="The path to the output PDF file",
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="The path to an image",
    )
    parser.add_argument(
        "--json",
        type=str,
        default=None,
        help="The path to a json input",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        help="The keyword to add textblock",
        default=None,
    )
    args = parser.parse_args()

    create_section(args.outfile, args.image, args.json, args.keyword)
