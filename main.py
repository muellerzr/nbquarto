from nbquarto.notebook import write_notebook
from nbquarto.processor import NotebookProcessor, BasicProcessor


processor = NotebookProcessor(
    "docs/test.ipynb",
    processors=[BasicProcessor]
)
processor.process_notebook()

write_notebook(processor.notebook, "docs/result.ipynb")