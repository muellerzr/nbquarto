"""
The processor in here is an exceedingly simple one,
designed for you to read and learn from on how the API
works

All it will do is add a comment to the top of a cell
that contains the `#| process` directive.
"""
import logging

from ..processor import Processor


logger = logging.getLogger(__name__)


class BasicProcessor(Processor):
    """
    A basic processor that adds a comment to the top of a cell

    Example usage:

    ```python
    #| process
    def my_function():
        return "Hello world!"
    ```
    """

    directives = "process"

    def process(self, cell):
        if any(directive in cell.directives_ for directive in self.directives):
            cell.source = f"# This code has been processed!\n{cell.source}"
        return cell
