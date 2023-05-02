import unittest

from nbquarto.notebook import make_cell, new_notebook
from nbquarto.processor import Processor, NotebookProcessor


class BasicProcessor(Processor):
    """
    A basic processor that adds a comment to the top of a cell
    """

    directives = "process"

    def process(self, cell):
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
        self.notebook_processor = NotebookProcessor(
            processors=[self.processor], notebook=self.test_notebook
        )

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
        self.assertEqual(
            self.test_notebook.cells[2].source, "def multiplication(a,b):\n  return a*b"
        )
