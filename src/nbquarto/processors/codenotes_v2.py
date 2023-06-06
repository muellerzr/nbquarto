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
import re
from typing import List

from ..notebook import NotebookCell, make_cell
from ..processor import Processor


raise NotImplementedError(
    "Hi! This processor isn't quite ready yet, please use `nbquarto.processors.codenotes` instead."
)


def make_panel_tabset(first_tab: str = "Code", second_tab: str = "Code & Explanation") -> List[NotebookCell]:
    """
    Creates a panel tabset with two tabs

    Args:
        first_tab (`str`):
            The title for the first tab
        second_tab (`str`):
            The title for the second tab

    Returns:
        List of `NotebookCell`: A list of cells that make up the panel tabset
    """
    cells = [
        make_cell(f"::: {{.panel-tabset}}\n\n## {first_tab}", cell_type="markdown"),
        # The original code will go between here
        make_cell(f"## {second_tab}", cell_type="markdown"),
        # The explanation will go under here
        make_cell(":::", cell_type="markdown"),
    ]
    return cells


def convert_explanation(explanation_cell: NotebookCell, source_code: str) -> NotebookCell:
    """
    Takes an explanation cell and source code, and links them together in a new cell

    Args:
        explanation_cell (`NotebookCell`):
            The cell containing `source_code`'s explanation
        source_code (`str`):
            The source code being annotated
    """
    python = "{.python}"
    newline = "\n"
    explanation = re.sub(r"\*|.*[\n]", "", explanation_cell.source)
    content = f"{newline}***{newline}```{python}{newline}{source_code}{newline}```"
    content += f"{newline}:::"
    content += "{style='padding-top: 0px;'}"
    content += f"{newline}{explanation}{newline}:::"
    return make_cell(content, cell_type="markdown")


def extract_code(
    start_code: str,
    end_code: str,
    source: str,
    start_instance_number: int,
    end_instance_number: int = 0,
) -> str:
    """
    Finds code between `start_code` and `end_code`, potentially within
    a selection of instances

    Args:
        start_code (`str`):
            The code that marks the beginning of the selection
        end_code (`str`):
            The code that marks the end of the selection
        source (`str`):
            The source code to search through
        start_instance_number (`int`):
            The instance of `start_code` to start the selection at
        end_instance_number (`int`, *optional*, defaults to 0):
            The instance of `end_code` to end the selection at

    Returns:
        `str`: The code between `start_code` and `end_code`
    """
    start_match = list(re.finditer(f"[ \t]*{start_code}", source))[start_instance_number]
    starting_character = start_match.span()[0]
    end_match = list(re.finditer(f"[ \t]*{end_code}", source))[end_instance_number]
    ending_character = end_match.span()[1]
    return source[starting_character:ending_character]


def parse_multiline_code(code_cell: NotebookCell, directives: List[str]):
    """
    Prases directives to extract code that needs to be highlighted

    Args:
        code_cell (`NotebookCell`):
            The cell containing the code to be highlighted
        directives (list of `str`):
            The directives in the markdown cell
    """
    if len(directives) == 4:
        start_code, start_instance_number, end_code, end_instance_number = directives
    # The user does not always need to define the end instance number
    else:
        start_code, start_instance_number, end_code = directives
        end_instance_number = 0
    start_code = re.escape(start_code)
    end_code = re.escape(end_code)
    return extract_code(
        start_code,
        end_code,
        code_cell.source,
        int(start_instance_number),
        int(end_instance_number),
    )


class CodeNoteProcessor(Processor):
    """
    A processor which checks and reorganizes cells for documentation with the proper
    explanations

    Specifically will look at source code cells that have markdown cells following them.
    Each markdown cell should contain `#| explain` followed by a selection of the source
    code the markdown cell is explaining. The processor will then create a panel tabset
    with the original code and the new explanation.

    For example:

    In a code cell:
    ```python
    def addition(a,b):
        return a+b
    ```

    In a subsequent markdown cell:
    ```markdown
    #| explain `addition(a,b)`
    This function adds two numbers together
    ```
    """

    directives = "explain"
    cell_types = ["code", "markdown"]

    offset: int = 0
    steps: list = []
    _index = 0

    def begin(self):
        self.reset()
        self.has_reset = False
        self.iteration = 0

    def reset(self):
        self.content = make_panel_tabset()
        self.code = []
        self.explanations = []
        self._code = None
        self.found_explanation = False
        self.end_link = False
        self.start_index = None
        self.end_index = None

    def process(self, cell):
        if cell.cell_type == "code":
            if not self.found_explanation:
                self._code = cell
                self.start_index = cell.index_
        elif cell.cell_type == "markdown" and "explain" in cell.directives_:
            self.found_explanation = True
            self.explanations.append(cell)

        if self.found_explanation:
            index = cell.index_ + 1
            if ("explain" not in self.notebook.cells[index].directives_) or (len(self.notebook.cells) <= index + 1):
                self.end_link = True
                self.end_index = index

            # After we have found all the code and explanations, we can start processing
            if self.end_link:
                tabset_code_index = 1
                tabset_explain_index = 3
                self.content.insert(tabset_code_index, self._code)
                explanations = [self._code]
                for i, explanation in enumerate(self.explanations):
                    source = parse_multiline_code(self._code, explanation.directives_["explain"])
                    converted_explanation = convert_explanation(explanation, source)
                    explanations.append(converted_explanation)
                    self.notebook.cells.remove(explanation)
                self.content = (
                    self.content[:tabset_explain_index] + explanations + [self.content[tabset_explain_index]]
                )
                self.notebook.cells.remove(self._code)
                offset = 0
                for cell in self.content:
                    cell.index_ = self.notebook.cells[self.start_index - 1].index_ + 1
                    self.notebook.cells.insert(self.start_index + offset, cell)
                    offset += 1
                self.iteration += 1
                self.reset()
                self.has_reset = True

                for i, cell in enumerate(self.notebook.cells):
                    cell.index_ = i
