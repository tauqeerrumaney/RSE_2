"""
This script generates a basic LaTeX document based on research results
and outputs it as a PDF or LaTeX file.

Usage:
    Run the script from the command line with optional arguments
    for the output file names, title, and author:
    ```
    python generate_document.py --pdf output.pdf --latex output.tex
    --title "Document Title" --author "Author Name"
    ```

Functions:
    create_document(pdf, latex, title, author)
        Creates a LaTeX document with the specified title and author
        and generates output documents in PDF and LaTeX formats.

    get_text(keyword)
        Retrieves the text associated with a given keyword from a text file.

Constants:
    FILE_NAMES: A dictionary mapping image names to their file paths.

Command-Line Arguments:
    --pdf (str): The filename for the generated PDF document. Default: None
    --latex (str): The filename for the generated LaTeX document. Default: None
    --title (str): The title of the document.
        Default: "Analysis Results of EEG Dataset"
    --author (str): The author of the document.
        Default: "University of Potsdam, RSE 2024"

"""

from pylatex import Document, Section, Command, Figure, Package
from pylatex.utils import NoEscape
import argparse
import os

from utils import get_path
from logger import configure_logger

FILE_NAMES = {
    "erp_difference": get_path("results/erp_difference.png"),
    "ica_components": get_path("results/ica_components.png"),
    "O1_vs_O2": get_path("results/O1vO2.png"),
    "spectogram": get_path("results/spectogram.png"),
    "variability": get_path("results/variability.png"),
}


def create_document(pdf, latex, title, author):
    """
    Creates a LaTeX document with specified title and author
    and generates output documents in PDF and LaTeX formats.

    Parameters:
    - pdf (str): The filename for the generated PDF document.
    - latex (str): The filename for the generated LaTeX document.
    - title (str): The title of the document.
    - author (str): The author of the document.

    Returns:
        None
    """

    # Configure logger
    logger = configure_logger()

    if pdf is None and latex is None:
        logger.error("Please provide a filename for the output PDF or LaTeX.")
        return

    # Create basic document
    doc = Document("basic")
    logger.info("Document created successfully!")

    # Add packages
    doc.packages.append(Package("float"))

    # Create preamble
    doc.preamble.append(Command("title", title))
    doc.preamble.append(Command("author", author))
    doc.preamble.append(Command("date", NoEscape(r"\today")))
    doc.append(NoEscape(r"\maketitle"))
    logger.info("Preamble created successfully!")

    doc.append(get_text("introduction"))

    for image in FILE_NAMES.keys():
        # check if image was created
        image_path = get_path(FILE_NAMES[image])
        if os.path.exists(image_path):

            # Create Section
            section_title = image.replace("_", " ")
            with doc.create(Section(f"{section_title.capitalize()} Section")):

                # Add figure
                with doc.create(Figure(position="H")) as pic:
                    pic.add_image(image_path, width="120px")
                    pic.add_caption(f"Image: {image}")

                # Try to add text from textblock
                try:
                    doc.append(f"{get_text(image)}")
                except ValueError as ve:
                    logger.error(f"ValueError: {ve}")
                except Exception as e:
                    logger.error(f"An unexpected error occurred: {e}")
                logger.info(f"Section '{section_title}' added successfully!")

    try:
        # generate output documents
        if pdf is not None:
            if not pdf.endswith(".pdf"):
                pdf = f"{pdf}.pdf"
            doc.generate_pdf(
                get_path(pdf).strip(".pdf"),
                clean_tex=True,
                compiler="pdflatex",
            )
            logger.info(f"PDF generated successfully at {pdf}")

        if latex is not None:
            if not latex.endswith(".tex"):
                latex = f"{latex}.tex"
            doc.generate_tex(
                get_path(latex).split(".tex")[0],
            )
            logger.info(f"LaTeX generated successfully at {latex}")
    except FileNotFoundError as fnfe:
        logger.error(f"FileNotFoundError: {fnfe}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return


def get_text(keyword):
    """
    Retrieves the text content associated with the given keyword.

    Args:
        keyword (str): The keyword used to identify the text content.

    Returns:
        str: The text content associated with the keyword,
            or None if the file is not found.

    Raises:
        FileNotFoundError: If the keyword file is not found.
        Exception: If an unexpected error occurs while reading the file.
    """
    # Configure logger
    logger = configure_logger()

    try:
        with open(get_path(f"data/textblocks/{keyword}.txt"), "r") as file:
            keyword_text = file.read()
        return keyword_text
    except FileNotFoundError as fnfe:
        logger.error(f"FileNotFoundError: {fnfe}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return


if __name__ == "__main__":
    USAGE = "Generate a basic LaTeX document based on the research results"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="The path to the output PDF file",
    )
    parser.add_argument(
        "--latex",
        type=str,
        default=None,
        help="The path to the output LaTeX file",
    )
    parser.add_argument(
        "--title",
        type=str,
        help="The title of the document",
        default="Analysis Results of EEG Dataset",
    )
    parser.add_argument(
        "--author",
        type=str,
        help="The author of the document",
        default="University of Potsdam, RSE 2024",
    )
    args = parser.parse_args()

    create_document(args.pdf, args.latex, args.title, args.author)
