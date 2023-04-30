from .foundation import AttributeDictionary
from .utils import notebook_language, langs
from execnb.nbio import read_nb
import re

cell_magic = re.compile(r"^\s*%%\w+")

def format_directive(language:str=None): 
    return fr'\s*{langs[language]}\s*\|'

def quarto_regex(language:str=None):
    return re.compile(
        format_directive(language) + r'\s*[\w|-]+\s*:'
    )

def first_code_line(code_list:list, regex_pattern:str=None, language="python"):
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

def partition_cell(cell:AttributeDictionary, language:str):
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

def fix_quarto_directives(content:str, language:str="python"):
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

def get_directive(content:str, language:str="python"):
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

def extract_directives(cell:AttributeDictionary, remove_directives:bool=True, language:str=None):
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
            ] + code
        )
    return dict(
        get_directive(directive, language=language)
        for directive in directives
    )

def make_processors(processors:list, notebook:AttributeDictionary):
    """
    Creates a list of processors for a notebook

    Args:
        processors (`list`):
            A list of functions to apply to the notebook
        notebook (`AttributeDictionary`):
            An object representing all the cells in a Jupyter Notebook
    """
    for i, processor in enumerate(processors):
        if isinstance(processor, type):
            processors[i] = processor(notebook=notebook)
    return processors

def is_directive(processor:callable):
    """
    Checks if a processor is a directive

    Args:
        processor (`callable`):
            A function to apply to a notebook cell's content
    """
    name = getattr(processor, "__name__", "-")
    return name[-1] == "_"

class NotebookProcessor:
    def __init__(
            self, 
            path:str=None, 
            processors:list=[], 
            notebook:AttributeDictionary=None, 
            debug:bool=False, 
            remove_directives:bool=True, 
            process_immediately:bool=False
        ):
        """
        Processes notebook cells and comments in a notebook

        Args:
            path (`str`, *optional*, defaults to None):
                The path to the notebook
            processors (`list`, *optional*, defaults to []):
                A list of functions to apply to the notebook
            notebook (`AttributeDictionary`, *optional*, defaults to None):
                An object representing all the cells in a Jupyter Notebook. If None, will be loaded from path
            debug (`bool`, *optional*, defaults to False):
                Whether to print debug statements
            remove_directives (`bool`, *optional*, defaults to True):
                Whether to remove directives from each cell after processing
            process_immediately (`bool`, *optional*, defaults to False):
                Whether to process the notebook after initialization
        """
        self.notebook = read_nb(path) if notebook is None else notebook
        self.language = notebook_language(self.notebook)
        for cell in self.notebook.cells:
            cell.directives_ = extract_directives(cell, remove_directives=remove_directives, language=self.language)
            # print(f'Directives: {cell.directives_}')
        self.processors = make_processors(processors, notebook=self.notebook)
        self.debug = debug
        self.remove_directives = remove_directives
        if process_immediately:
            self.process_notebook()

    def process_comment(self, processor:callable, cell:AttributeDictionary, command:str):
        """
        Processes a comment in a notebook cell

        Args:
            processor (`callable`):
                A function to apply to a notebook cell's content
            cell (`AttributeDictionary`):
                A cell from a Jupyter Notebook
            command (`str`):
                The command to process
        """
        arguments = cell.directives_[command]
        if self.debug:
            print(f"Processing {command} in cell {cell} with arguments {arguments}")
        return processor(cell, command, arguments)

    def process_cell(self, processor:callable, cell:AttributeDictionary):
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
                    raise Exception(f"Error processing cell {cell.idx_} with processor {processor.__class__}") from e
            if hasattr(processor, "end"):
                processor.end()
            self.notebook.cells = [
                cell for cell in self.notebook.cells
                if cell is not None and getattr(cell, "source", None) is not None
            ]
            for i, cell in enumerate(self.notebook.cells):
                cell.index_ = i

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
    """
    def __init__(self, notebook:AttributeDictionary):
        """
        Args:
            notebook (`AttributeDictionary`):
                An object representing all the cells in a Jupyter Notebook
        """
        self.notebook = notebook

    def process_cell(self, cell:AttributeDictionary):
        """
        Processes a single cell of a notebook

        Args:
            cell (`AttributeDictionary`):
                A cell from a Jupyter Notebook
        """
        raise NotImplementedError("You must implement the `process_cell` method to apply this processor")

    def __call__(self, cell:AttributeDictionary):
        """
        Processes a single cell of a notebook

        Args:
            cell (`AttributeDictionary`):
                A cell from a Jupyter Notebook
        """
        return self.process_cell(cell)


