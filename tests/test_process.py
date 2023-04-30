import unittest
from execnb.nbio import new_nb, mk_cell

from nbdev_mini.process import Processor, NotebookProcessor

class TestProcessor(Processor):
    def process_cell(self, cell):
        if cell.cell_type == "code":
            if "process" in cell.directives_:
                cell.source = f'# This code has been processed!\n{cell.source}'

class TestProcess(unittest.TestCase):
    """
    Tests for verifying that notebooks can successfully
    be processed. 
    """
    processor = TestProcessor

    def reset_cells(self):
        test_cells = [
            mk_cell("#| process\ndef addition(a,b):\n  return a+b", "code"),
            mk_cell("#|process\ndef subtraction(a,b):\n  return a-b", "code"),
            mk_cell("def multiplication(a,b):\n  return a*b", "code"),
        ]
        self.test_notebook = new_nb(cells=test_cells)

    def setUp(self):
        self.reset_cells()
        self.notebook_processor = NotebookProcessor(processors=[self.processor], notebook=self.test_notebook)

    def test_notebook_process(self):
        """
        Test that a notebook can be processed
        """
        self.notebook_processor.process_notebook()
        self.assertEqual(self.test_notebook.cells[0].source, "# This code has been processed!\ndef addition(a,b):\n  return a+b")
        self.assertEqual(self.test_notebook.cells[1].source, "# This code has been processed!\ndef subtraction(a,b):\n  return a-b")
        self.assertEqual(self.test_notebook.cells[2].source, "def multiplication(a,b):\n  return a*b")