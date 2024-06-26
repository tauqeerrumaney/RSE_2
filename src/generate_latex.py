from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape


def fill_document(doc):
    """Add a section, a subsection and some text to the document.

    Args:
        doc (object): The document object to which the content will be added.

    Returns:
        None
    """
    with doc.create(Section("Dataset")):
        doc.append("Some regular text and some ")
        doc.append(italic("italic text. "))

        with doc.create(Subsection("A subsection")):
            doc.append("Also some crazy characters: $&#{}")


if __name__ == "__main__":
    # Create basic document
    doc = Document("basic")

    # Create preamble and generate title
    doc.preamble.append(Command("title", "Dummy title"))
    doc.preamble.append(Command("author", "RSE 2024 Group L"))
    doc.preamble.append(Command("date", NoEscape(r"\today")))
    doc.append(NoEscape(r"\maketitle"))

    # add contents to document
    fill_document(doc)

    # generate output documents
    doc.generate_pdf("results/dummy", clean_tex=False, compiler="pdflatex")
    doc.generate_tex("results/dummy")
