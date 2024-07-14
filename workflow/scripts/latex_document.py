"""
This script generates a basic LaTeX document based on research results
and outputs it as a PDF or LaTeX file.

Usage:
    Run the script from the command line with optional arguments
    for the output file names, title, author, and sections:

    python latex_document.py [--pdf PDF] [--latex LATEX] [--title TITLE]
    [--author AUTHOR] [--sections ...]

Example:
    ```
    python latex_document.py --author "Author Name" --sections
    "section1.tex" "section2.tex"
    ```

Options:
    --pdf (str, optional): The filename for the generated PDF document.
        Default: None
    --latex (str, optional): The filename for the generated LaTeX document.
        Default: None
    --title (str, optional): The title of the document. Default: "Analysis
        Results of EEG Dataset"
    --author (str, optional): The author of the document. Default:
        "University of Potsdam, RSE 2024"
    --sections (str, optional): The sections to include in the document.

Files:
    --pdf: The output PDF file where the document will be saved.
    --latex: The output LaTeX file where the document will be saved.
    --sections: The input LaTeX section files to be included in the document.

Functions:
    main(pdf, latex, title, author, sections=[]):
        Creates a LaTeX document with the specified title and author
        and generates output documents in PDF and LaTeX formats.
"""

import argparse
import os
import traceback

from pylatex import Command, Document, Package
from pylatex.utils import NoEscape

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(
    pdf: str | None,
    latex: str | None,
    title: str,
    author: str,
    sections: list[str] = [],
):
    """
    Creates a LaTeX document with the specified title and author
    and generates output documents in PDF and LaTeX formats.

    Args:
        pdf (str): The filename for the generated PDF document.
            Default is None.
        latex (str): The filename for the generated LaTeX document.
            Default is None.
        title (str): The title of the document.
        author (str): The author of the document.
        sections (list): Paths to the sections to include in
            the document.

    Returns:
        None

    Raises:
        FileNotFoundError: If a section file does not exist.
        TypeError: If the input parameters are not of the expected types.
        ValueError: If the output directory does not exist.
    """
    # Validate input types
    if not isinstance(pdf, (str, type(None))):
        raise TypeError(
            f"Expected 'pdf' to be of type str or None, but got "
            f"{type(pdf).__name__}"
        )
    if not isinstance(latex, (str, type(None))):
        raise TypeError(
            f"Expected 'latex' to be of type str or None, but got "
            f"{type(latex).__name__}"
        )
    if not isinstance(title, str):
        raise TypeError(
            f"Expected 'title' to be of type str, but got "
            f"{type(title).__name__}"
        )
    if not isinstance(author, str):
        raise TypeError(
            f"Expected 'author' to be of type str, but got "
            f"{type(author).__name__}"
        )
    if not isinstance(sections, list):
        raise TypeError(
            f"Expected 'sections' to be of type list, but got "
            f"{type(sections).__name__}"
        )
    if not all(isinstance(section, str) for section in sections):
        raise TypeError(
            "Expected all elements in 'sections' to be of type str"
        )

    # Validate input files
    for section in sections:
        section_path = get_path(section)
        if not os.path.exists(section_path):
            raise FileNotFoundError(f"Section file not found: {section_path}")

    # Validate output files
    if pdf is not None:
        pdf_path = get_path(pdf)
        out_dir = os.path.dirname(pdf_path)
        if not os.path.exists(out_dir):
            raise ValueError(f"Output directory does not exist: {out_dir}")

        # If out_path is a .pdf file remove the extension
        if pdf_path.endswith(".pdf"):
            pdf_path = pdf_path.split(".pdf")[0]

    if latex is not None:
        tex_path = get_path(latex)
        out_dir = os.path.dirname(tex_path)
        if not os.path.exists(out_dir):
            raise ValueError(f"Output directory does not exist: {out_dir}")

        # If out_path is a .tex file remove the extension
        if tex_path.endswith(".tex"):
            tex_path = tex_path.split(".tex")[0]

    # Create basic document
    doc = Document("basic")
    doc.packages.append(Package("float"))
    doc.packages.append(Package("graphicx"))
    doc.packages.append(Package("subfiles"))

    # Create preamble
    doc.preamble.append(Command("title", title))
    doc.preamble.append(Command("author", author))
    doc.preamble.append(Command("date", NoEscape(r"\today")))
    doc.append(NoEscape(r"\maketitle"))

    # Add sections to the document
    for section in sections:
        doc.append(Command("subfile", NoEscape(get_path(section))))

    # Generate output documents
    if pdf_path:
        doc.generate_pdf(
            pdf_path,
            clean_tex=True,
            compiler="pdflatex",
        )
        logger.info(f"PDF generated successfully at {pdf_path}")

    if tex_path:
        doc.generate_tex(tex_path)
        logger.info(f"LaTeX generated successfully at {tex_path}")


if __name__ == "__main__":
    USAGE = "Generate a basic LaTeX document based on the research results"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="The path to the output PDF file. "
        "If not ending in '.pdf', it will be appended.",
    )
    parser.add_argument(
        "--latex",
        type=str,
        default=None,
        help="The path to the output LaTeX file. "
        "If not ending in '.tex', it will be appended.",
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
    parser.add_argument(
        "--sections",
        type=str,
        nargs="*",
        help="The sections to include in the document",
    )
    args = parser.parse_args()
    try:
        main(
            pdf=args.pdf,
            latex=args.latex,
            title=args.title,
            author=args.author,
            sections=args.sections,
        )
    except (TypeError, FileNotFoundError, ValueError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
