from pylatex import Document, Section, Subsection, Command

# Create a basic document
doc = Document("dummy")

# Add a title
doc.preamble.append(Command("title", "Dummy Document"))
doc.preamble.append(Command("author", "Your Name"))
doc.preamble.append(Command("date", "2022"))

doc.append(Section("Section 1"))
doc.append("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

doc.append(Section("Section 2"))
doc.append(Subsection("Subsection 2.1"))
doc.append(
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
)

doc.append(Subsection("Subsection 2.2"))
doc.append(
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
)

# Compile the document to PDF
doc.generate_pdf("results/dummy", clean_tex=False, compiler="pdflatex")

print("Dummy PDF created successfully!")
