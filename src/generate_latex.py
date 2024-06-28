"""Generate a basic LaTeX document based on the research results"""

from pylatex import Document, Section, Subsection, Command, Figure, Package
from pylatex.utils import italic, NoEscape
import argparse
import os


def create_document(title, author):
    """Create a basic document.

    Args:
        title (str): The title of the document.
        author (str): The author of the document.

    Returns:
        None
    """
    # Create basic document
    doc = Document("basic")

    # Add packages
    doc.packages.append(Package('float'))

    # Create preamble
    create_preamble(doc, title, author)

    # Create preamble and generate title
    doc.preamble.append(Command("title", "Analyis Results of EEG Dataset"))
    doc.preamble.append(Command("author", "RSE 2024 Group L"))
    doc.preamble.append(Command("date", NoEscape(r"\today")))
    doc.append(NoEscape(r"\maketitle"))

    # add contents to document
    fill_document(doc)

    for image in [
        "spectrum",
        "topology",
        "statistical",
    ]:
        image_path = os.path.join(
            os.path.dirname(__file__), f'../results/images/{image}_placeholder.png')
        if os.path.exists(image_path):
            with doc.create(Section(f'{image} Section')):
                doc.append(f"{get_text(image)}")
                with doc.create(Figure(position='H')) as pic:
                    pic.add_image(image_path, width='120px')
                    pic.add_caption(f'Image: {image}')
        else:
            print(f"Image not found in {image_path}")

    # generate output documents
    doc.generate_pdf(
        "results/pdf/dummy",
        clean_tex=True,
        compiler="pdflatex",
    )
    # doc.generate_tex("results/text/dummy")
    print("Document generated successfully!")


def create_preamble(doc, title, author):
    """
    Create the preamble for the LaTeX document.

    Args:
        doc (Document): The LaTeX document object.
        title (str): The title of the document.
        author (str): The author of the document.
    """
    # Create preamble and generate title
    doc.preamble.append(Command("title", title))
    doc.preamble.append(Command("author", author))
    doc.preamble.append(Command("date", NoEscape(r"\today")))
    doc.append(NoEscape(r"\maketitle"))


def fill_document(doc):

    with doc.create(Section("Dataset")):
        doc.append("Some regular text and some ")
        doc.append(italic("italic text. "))

        with doc.create(Subsection("A subsection")):
            doc.append("Also some crazy characters: $&#{}")


def get_text(keyword):
    text_dict = {}
    with open(os.path.join(os.path.dirname(__file__), '../data/textblocks.txt'), "r") as file:
        for line in file.readlines():
            line_parts = line.split(";")
            print(line_parts)
            key, value = line_parts[0], line_parts[1]
            text_dict[key] = value
    return text_dict[keyword]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
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

    create_document(args.title, args.author)
