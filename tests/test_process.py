import unittest

from nbquarto.notebook import make_cell, new_notebook
from nbquarto.processor import NotebookProcessor, Processor
from nbquarto.processors import AutoDocProcessor, CodeNoteProcessor, SemanticVersioningProcessor
from nbquarto.processors.semantic_versioning import REFERENCE_JAVASCRIPT, REFERENCE_JQUERY


class BasicProcessor(Processor):
    """
    A basic processor that adds a comment to the top of a cell
    """

    directives = "process"

    def process(self, cell):
        if any(directive in cell.directives_ for directive in self.directives):
            cell.source = f"# This code has been processed!\n{cell.source}"


class TestProcess(unittest.TestCase):
    """
    Tests for verifying that notebooks can successfully
    be processed.
    """

    processor = BasicProcessor

    def reset_cells(self):
        test_cells = [
            make_cell("#| process\ndef addition(a,b):\n  return a+b", "code"),
            make_cell("#|process\ndef subtraction(a,b):\n  return a-b", "code"),
            make_cell("def multiplication(a,b):\n  return a*b", "code"),
        ]
        self.test_notebook = new_notebook(cells=test_cells)

    def setUp(self):
        self.reset_cells()
        self.notebook_processor = NotebookProcessor(processors=[self.processor], notebook=self.test_notebook)

    def test_notebook_process(self):
        """
        Test that a notebook can be processed
        """
        self.notebook_processor.process_notebook()
        self.assertEqual(
            self.test_notebook.cells[0].source,
            "# This code has been processed!\ndef addition(a,b):\n  return a+b",
        )
        self.assertEqual(
            self.test_notebook.cells[1].source,
            "# This code has been processed!\ndef subtraction(a,b):\n  return a-b",
        )
        self.assertEqual(self.test_notebook.cells[2].source, "def multiplication(a,b):\n  return a*b")


class TestCodeNotes(unittest.TestCase):
    processor = CodeNoteProcessor

    def reset_cells(self):
        test_cells = [
            make_cell("# Test Notebook", "markdown"),
            make_cell("def addition(a,b):\n  return a+b", "code"),
            make_cell(
                "#| explain addition 0 (\nThis function adds two numbers together",
                "markdown",
            ),
            make_cell("", "markdown"),
        ]
        self.test_notebook = new_notebook(cells=test_cells)

    def setUp(self):
        self.reset_cells()
        self.notebook_processor = NotebookProcessor(processors=[self.processor], notebook=self.test_notebook)

    def test_codenotes(self):
        self.notebook_processor.process_notebook()
        from nbquarto.notebook import write_notebook

        write_notebook(self.test_notebook, "test.ipynb")
        self.assertEqual(self.test_notebook.cells[1].source, "::: {.panel-tabset}\n\n## Code")
        self.assertEqual(self.test_notebook.cells[2].source, "def addition(a,b):\n  return a+b")
        self.assertEqual(self.test_notebook.cells[3].source, "## Code & Explanation")
        self.assertEqual(self.test_notebook.cells[4].source, "def addition(a,b):\n  return a+b")
        self.assertEqual(
            self.test_notebook.cells[5].source,
            (
                "\n***\n```{.python}\n addition("
                "\n```\n:::{style='padding-top: 0px;'}"
                "\nThis function adds two numbers together\n:::"
            ),
        )


class TestAutoDoc(unittest.TestCase):
    processor = AutoDocProcessor

    def reset_cells(self):
        test_cells = [
            make_cell("# Test Notebook", "markdown"),
            make_cell("#| autodoc nbquarto.processors.AutoDocProcessor\n#| methods process", "markdown"),
            make_cell("#| autodoc nbquarto.processor.Processor", "markdown"),
            make_cell("", "markdown"),
        ]
        self.test_notebook = new_notebook(cells=test_cells)

    def setUp(self):
        self.reset_cells()
        self.notebook_processor = NotebookProcessor(
            processors=[self.processor],
            notebook=self.test_notebook,
            config={"autodoc": {"repo_name": "nbquarto", "repo_owner": "muellerzr"}},
        )

    def test_codenotes(self):
        self.notebook_processor.process_notebook()
        self.assertTrue("Should contain the exact import location" in self.notebook_processor.notebook.cells[1].source)
        self.assertTrue(
            "Applies the processor to a cell if the cell is of the" in self.notebook_processor.notebook.cells[2].source
        )


class TestSemanticVersioning(unittest.TestCase):
    processor = SemanticVersioningProcessor

    def test_procesor(self):
        content = "---\ntitle: Test Notebook\n---\n# Test Notebook"
        processor = SemanticVersioningProcessor(content)
        processed_content = processor.process()
        self.assertEqual(processed_content, f"{REFERENCE_JQUERY}\n{REFERENCE_JAVASCRIPT}\n{content}")
