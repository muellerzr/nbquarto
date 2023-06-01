---
title: "nbquarto"
---

# nbquarto

`nbquarto` is a small python library built around the idea of creating quick extensions (`Processors`) to use in [Quarto](https://quarto.org) projects.

The general idea is that a `Processor` handles a "cell" in a notebook (or `qmd` eventually) and modifies its contents for documentation purposes (but can be used for other things). This project is built on the idea (and most of the code) from the [nbdev](https://github.com/fastai/nbdev) project by fast.ai, however it explicitly removes any magicalness from the code and creates a library that is purely "pythonic". 

As a result, the codebase here is almost a 1:1 of the code in nbdev *functionally*, while making it a bit easier for users to use, and some key tweaks to the original version of `nbdev`. Most noteably, this library's sole purpose is to create processors, it does not handle anything else that `nbdev` provides. 

## Important terms:

- `cell`: A singular module or item in a Jupyter Notebook, of which can either execute code written in it or contain Markdown that will be presented to a reader or on a Quarto website
- `directive`: A comment block in a notebook cell that Quarto (and `nbquarto`) can process or recognize. Generally denoted with a pipe (`|`) after the comment, such as `#| directive` or `# | directive`
- `Processor`: A class which modifies a cell in a Jupyter Notebook

## Creating a `Processor`

As mentioned earlier, a `Processor` take the content in any Jupyter Notebook cell and modify it in some way. The original design intention was to inject Quarto-specific nuonces into the cell to help with code formatting, or to write quick shortcuts to create complex combinations in quarto syntax on the fly.

The following is a small snippet (taken from the [official example processor](src/nbquarto/processors/example.py)) which simply injects the code:

```python
# This code has been processed!
```
to the top of any cell.

```python
from nbquarto import Processor

class BasicProcessor(Processor):
    """
    A basic processor that adds a comment to the top of a cell
    """

    directives = "process"

    def process(self, cell):
        if any(directive in cell.directives_ for directive in self.directives):
            cell.source = f"# This code has been processed!\n{cell.source}"
```

The `process` function is what will get applied to the notebook cell, after checking if any directives to look for exist in the cell. 

## Creating a config file

After either creating your own processor, or deciding what processor to use, a config file should be generated that contains the exact imports for processors you want to use, and where processed notebooks should be sent to. 

See below for an example, located [here](tests/test_artifacts/single_processor.yaml) in the repo:

```yaml
output_folder: processed_notebooks
processors: [
  nbquarto.processors.example:BasicProcessor
]
```
This reads as follows:
- `output_folder`: All notebooks will be saved to a (potentially new) `processed_notebooks` directory
- `processors`: This contains the list of processors we want to apply
- `nbquarto.processors.example:BasicProcessor`: This is the exact import for the processor to apply

## Calling the `Processor`(s) from the CLI

Finally, by calling the `nbquarto-process` command you can process notebooks with your configured `Processor`(s):

```bash
nbquarto-process --config_file tests/test_artifacts/single_processor.yaml --notebook_file tests/test_artifacts/test_example.ipynb
```