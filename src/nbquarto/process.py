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

from .foundation import AttributeDictionary
from .utils import langs


cell_magic = re.compile(r"^\s*%%\w+")


def format_directive(language: str = None):
    return rf"\s*{langs[language]}\s*\|"


def quarto_regex(language: str = None):
    return re.compile(format_directive(language) + r"\s*[\w|-]+\s*:")


def first_code_line(code_list: list, regex_pattern: str = None, language="python"):
    """
    Gets the first line number where code occurs

    Args:
        code_list (`list`):
            List of lines from source code
        regex_pattern (`str`, *optional*, defaults to None):
            The regex pattern to match
        language (`str`, *optional*, defaults to "python"):
            The language of the source code
    """
    if regex_pattern is None:
        regex_pattern = format_directive(language)
    for i, line in enumerate(code_list):
        if line.strip() != "" and not re.match(regex_pattern, line) and not cell_magic.match(line):
            return i
    return None


def partition_cell(cell: AttributeDictionary, language: str):
    """
    Splits a cell from the directives and code

    Args:
        cell (`AttributeDictionary`):
            A cell from a Jupyter Notebook
        language (`str`):
            The language of the source code
    """
    if not cell.source:
        return [], []
    lines = cell.source.splitlines(True)
    first_code = first_code_line(lines, language=language)
    return lines[:first_code], lines[first_code:]


def fix_quarto_directives(content: str, language: str = "python"):
    """
    Normalize quarto directives so they have a space after the column

    Args:
        content (`str`):
            The content of the cell
        language (`str`, *optional*, defaults to "python"):
            The language of the source code
    """
    regex = quarto_regex(language)
    match = regex.match(content)
    return f'{match.group(0)} {regex.sub("", content).lstrip()}' if match else content


def get_directive(content: str, language: str = "python"):
    """
    Get the directive from a cell

    Args:
        content (`str`):
            The content of the cell
        language (`str`, *optional*, defaults to "python"):
            The language of the source code
    """
    content = re.sub(f"^{format_directive(language)}", f"{langs[language]}|", content)
    if content.strip().endswith(":"):
        content = content.replace(":", "")
    if ":" in content:
        content = content.replace(":", ": ")
    content = content.strip()[2:]
    content = content.strip().split()
    if not content:
        return None
    directive, *args = content
    return directive, args


def extract_directives(cell: AttributeDictionary, remove_directives: bool = True, language: str = None):
    """
    Extracts directives from a cell

    Args:
        cell (`AttributeDictionary`):
            A cell from a Jupyter Notebook
        remove_directives (`bool`, *optional*, defaults to True):
            Whether to remove directives from the cell
        language (`str`, *optional*, defaults to None):
            The language of the source code
    """
    directives, code = partition_cell(cell, language=language)
    if directives is None:
        return {}
    if remove_directives:
        # Leave Quarto directives and magic inplace
        cell["source"] = "".join(
            [
                fix_quarto_directives(directive, language=language)
                for directive in directives
                if quarto_regex(language).match(directive) or cell_magic.match(directive)
            ]
            + code
        )
    return dict(get_directive(directive, language=language) for directive in directives)


def make_processors(processors: list, notebook: AttributeDictionary, processor_args: dict = {}):
    """
    Creates a list of processors for a notebook

    Args:
        processors (`list`):
            A list of functions to apply to the notebook
        notebook (`AttributeDictionary`):
            An object representing all the cells in a Jupyter Notebook
        processor_args (`dict`, *optional*, defaults to None):
            A dict of arguments to pass to a particular processor.
    """
    for i, processor in enumerate(processors):
        if isinstance(processor, type):
            if processor.__name__ in processor_args:
                function_args = processor_args[processor.__name__]
                processors[i] = processor(notebook=notebook, processor_args=function_args)
            else:
                processors[i] = processor(notebook=notebook)
    return processors


def is_directive(processor: callable):
    """
    Checks if a processor is a directive

    Args:
        processor (`callable`):
            A function to apply to a notebook cell's content
    """
    name = getattr(processor, "__name__", "-")
    return name[-1] == "_"
