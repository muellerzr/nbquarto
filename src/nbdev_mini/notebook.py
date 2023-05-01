import ast
import json
from pathlib import Path
from .foundation import AttributeDictionary
from .utils import dict2obj


class NotebookCell(AttributeDictionary):
    """
    A cell for a Jupyter Notebook
    """

    def __init__(self, index: int, cell: dict):
        """
        Args:
            index (`int`):
                The index of the cell in the entire notebook order
            cell (`dict`):
                The cell from the Jupyter Notebook
        """
        super().__init__(cell)
        self.index_ = index
        if "source" in self:
            self.set_source(self.source)

    def set_source(self, source: list):
        """
        Sets the source attribute of the cell as a string and removes parsed directives

        Args:
            source (`list`):
                The source of the cell as a list of strings
        """
        self.source = "".join(source)
        if "_parsed_" in self:
            del self._parsed_

    def parsed_(self):
        if self.cell_type != "code" or self.source.strip()[:1] in ["%", "!"]:
            return
        if "_parsed_" not in self:
            try:
                self._parsed_ = ast.parse(self.source.body)
            # You cna assign the result of ! to a variable in a notebook cell,
            # which results in a Syntax Error if parsed with ast
            except SyntaxError:
                return
        return self._parsed_

    def __hash__(self):
        return hash(self.source) + hash(self.cell_type)

    def __eq__(self, other):
        return self.source == other.source and self.cell_type == other.cell_type


def dict2notebook(d: dict = None, **kwargs):
    """
    Converts dictionary `d` to an `AttributeDictionary`

    Args:
        d (`dict`, *optional*, defaults to None):
            A dictionary to convert
    """
    notebook = dict2obj(d or kwargs)
    notebook.cells = [NotebookCell(*cell) for cell in enumerate(notebook.cells)]
    return notebook


def read_notebook(path: str):
    """
    Reads a Jupyter Notebook from a filepath

    Args:
        path (`str`):
            The path to the Jupyter Notebook
    """
    content = Path(path).read_text(encoding="utf-8")
    notebook = dict2notebook(json.loads(content))
    notebook["path_"] = str(path)
    return notebook


def notebook_language(notebook: AttributeDictionary) -> str:
    """
    Get the language of a notebook

    Args:
        notebook (`AttributeDictionary`):
            An object representing all the cells in a Jupyter Notebook
    """
    if "metadata" in notebook:
        if "kernelspec" in notebook.metadata:
            return getattr(notebook.metadata.kernelspec, "language", "python")
    return "python"


def new_notebook(
    cells: list = [], metadata: dict = {}, nbformat: int = 4, nbformat_minor: int = 5
):
    """
    Creates a new empty notebook

    Args:
        cells (`list` of `NotebookCell`, *optional*, defaults to []):
            A list of cells to make up the notebook
        metadata (`dict`, *optional*, defaults to {}):
            Metadata for the notebook
        nbformat (`int`, *optional*, defaults to 4):
            The nbformat of the notebook
        nbformat_minor (`int`, *optional*, defaults to 5):
            The minor nbformat version of the notebook
    """
    return dict2notebook(
        cells=cells, metadata=metadata, nbformat=nbformat, nbformat_minor=nbformat_minor
    )


def make_cell(text: str, cell_type: str = "code", **kwargs):
    """
    Makes a blank notebook cell

    Args:
        text (`str`):
            The source code for the cell
        cell_type (`str`, *optional*, defaults to "code"):
            The type of cell to make, must be one of "code", "markdown", or "raw"
        kwargs:
            Additional arguments to pass to the cell, such as `metadata`
    """
    if cell_type not in ["code", "markdown", "raw"]:
        raise ValueError(
            f"cell_type must be one of 'code', 'markdown', or 'raw', not {cell_type}"
        )
    metadata = kwargs.pop("metadata", {})
    cell = dict(
        cell_type=cell_type, source=text, directives_={}, metadata=metadata, **kwargs
    )
    return NotebookCell(0, cell)
