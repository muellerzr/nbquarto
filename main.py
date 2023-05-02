from nbquarto.notebook import write_notebook
from nbquarto.processor import NotebookProcessor

class BasicProcessor(Processor):
    """
    A basic processor that adds a comment to the top of a cell
    """

    directives = "process"

    def process(self, cell):
        cell.source = f"# This code has been processed!\n{cell.source}"


processor = NotebookProcessor(
    "docs/test.ipynb",
    processors=[BasicProcessor]
)
processor.process_notebook()

write_notebook(processor.notebook, "docs/result.ipynb")