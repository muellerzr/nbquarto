# Copyright 2023 Zachary Mueller and fast.ai. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Union, List

from .foundation import AttributeDictionary
from .notebook import read_notebook, notebook_language
from .process import make_processors, extract_directives, is_directive


class Processor:
    """
    Base class for all notebook processors.
    Any processors should inherit this class.

    When writing a processor, you can override methods that
    modify the content of a cell with the `process_cell` function.

    The class stores the entire notebook in the `notebook`
    attribute.

    When using a processor, simply call the class and pass
    in a single cell.

    Example:

    ```python
    class BasicProcessor(Processor):
        "A basic processor that adds a comment to the top of a cell"
        directive = "process"

        def process(self, cell):
            cell.source = f"# This code has been processed!\n{cell.source}"
    ```
    """

    directives: Union[List[str], str] = None
    cell_types: Union[List[str], str] = "code"

    def __init__(self, notebook: AttributeDictionary):
        """
        Args:
            notebook (`AttributeDictionary`):
                An object representing all the cells in a Jupyter Notebook
        """
        self.notebook = notebook
        if not isinstance(self.directives, list):
            self.directives = [self.directives]
        if not isinstance(self.cell_types, list):
            self.cell_types = [self.cell_types]

    def process(self, cell: AttributeDictionary):
        """
        A function to apply on a cell.

        Args:
            cell (`AttributeDictionary`):
                A cell from a Jupyter Notebook
        """
        raise NotImplementedError(
            "You must implement the `process` method to apply this processor"
        )

    def process_cell(self, cell: AttributeDictionary):
        """
        Applies the processor to a cell if the cell is of the
        correct type and contains the correct directive

        Args:
            cell (`AttributeDictionary`):
                A cell from a Jupyter Notebook
        """
        if cell.cell_type in self.cell_types:
            return self.process(cell)

    def __call__(self, cell: AttributeDictionary):
        """
        Processes a single cell of a notebook

        Args:
            cell (`AttributeDictionary`):
                A cell from a Jupyter Notebook
        """
        return self.process_cell(cell)


class NotebookProcessor:
    def __init__(
        self,
        path: str = None,
        processors: list = [],
        notebook: AttributeDictionary = None,
        debug: bool = False,
        remove_directives: bool = True,
        process_immediately: bool = False,
    ):
        """
        Processes notebook cells and comments in a notebook

        Args:
            path (`str`, *optional*, defaults to None):
                The path to the notebook
            processors (`list`, *optional*, defaults to []):
                A list of functions to apply to the notebook
            notebook (`AttributeDictionary`, *optional*, defaults to None):
                An object representing all the cells in a Jupyter Notebook.
                If None, will be loaded from path
            debug (`bool`, *optional*, defaults to False):
                Whether to print debug statements
            remove_directives (`bool`, *optional*, defaults to True):
                Whether to remove directives from each cell after processing
            process_immediately (`bool`, *optional*, defaults to False):
                Whether to process the notebook after initialization
        """
        self.notebook = read_notebook(path) if notebook is None else notebook
        self.language = notebook_language(self.notebook)
        for cell in self.notebook.cells:
            cell.directives_ = extract_directives(
                cell, remove_directives=remove_directives, language=self.language
            )
        self.processors = make_processors(processors, notebook=self.notebook)
        self.debug = debug
        self.remove_directives = remove_directives
        if process_immediately:
            self.process_notebook()

    def process_cell(self, processor: callable, cell: AttributeDictionary):
        """
        Processes a single cell of a notebook. Should not be called
        explicitly and instead a user should use `process_notebook`

        Args:
            processor (`callable`):
                A function to apply to a notebook cell's content
            cell (`AttributeDictionary`):
                A cell from a Jupyter Notebook
        """
        if not hasattr(cell, "source"):
            return
        if callable(processor) and not is_directive(processor):
            processed_cell = processor(cell)
            if processed_cell is not None:
                cell = processed_cell

    def process_notebook(self):
        """
        Processes the content of the notebook
        """
        for processor in self.processors:
            if hasattr(processor, "begin"):
                processor.begin()
            for cell in self.notebook.cells:
                try:
                    self.process_cell(processor, cell)
                except Exception as e:
                    raise Exception(
                        f"Error processing cell {cell.index_} with processor:"
                        f" `{processor.__module__}.{processor.__class__.__name__}`. "
                        "Please check earlier in the trace to see the true issue."
                    ) from e
            if hasattr(processor, "end"):
                processor.end()
            self.notebook.cells = [
                cell
                for cell in self.notebook.cells
                if cell is not None and getattr(cell, "source", None) is not None
            ]
            for i, cell in enumerate(self.notebook.cells):
                cell.index_ = i
