## Key Terms

- `Cell`: An executing module or Markdown container in a Jupyter Notebook.
- `Directive`: A pipe-delineated (`|`) comment block recognized by Quarto and `nbquarto`.
- `Processor`: A class that tailors a cell based on its directives.

## Introducing `nbquarto`: Your Python-Powered Notebook Enhancer

Harness the might of Python with `nbquarto`, a dynamic interface to externally transform Jupyter Notebook cells, designed ideally for [Quarto](https://quarto.org/) projects. 
This framework streamlines your documentation process by enabling rapid creation and implementation of post-processors for Jupyter Notebooks. 
Although Quarto-focused, `nbquarto` serves as a valuable asset for any Python project leveraging Jupyter Notebooks.

## Getting Started

Check out the installation directions [here](https://muellerzr.github.io/nbquarto) to get started!

## Choose `nbquarto` for a Superior Experience

Drawing inspiration from [nbdev](https://github.com/fastai/nbdev), `nbquarto` steers towards a more comprehensible and less abstracted interface. 
It focuses on modifications to Jupyter Notebooks as to fully capitalize on Quarto's abundant features, minimizing dependencies, and enhancing code readability.

## No More Learning Curve with `nbquarto`

Why learn a new language (Lua) to modify content already in Python? 
`nbquarto` emerges as the Pythonic alternative to Quarto Extensions. Offering flexibility and simplicity at the cost of a negligible increase in processing time, 
`nbquarto` empowers you to control the narrative.

## How Does `nbquarto` Work?

At the heart of `nbquarto` is a `Processor`. This component modifies a cell to fine-tune code formatting or swiftly craft complex Quarto syntax combinations. 
Each `cell` object encompasses two crucial elements: `directives_` (a list of cell directives) and `source` (modifiable cell text).

See how easy it is to add a comment to the top of a cell's text source:

```python
>>> from nbquarto import Processor

>>> class BasicProcessor(Processor):
...    "A basic processor that adds a comment to the top of a cell's text source."
...
...    directives = "process"
...
...    def process(self, cell):
...        if any(directive in cell.directives_ for directive in self.directives):
...            cell.source = f"# This code has been processed!\n{cell.source}"
```

And in a notebook cell:
```python
# Input
>>> #| process
... print("Hello, world!")

# Output
>>> # This code has been processed!
... print("Hello, world!")
```

## Simplified Configuration

Say goodbye to confusion with `nbquarto`'s configuration file. This handy feature organizes processor use, notebook paths, and processor constants for a seamless user experience.

```yaml
documentation_source: tests
processors: [
    nbquarto.processors.example:BasicProcessor,
    nbquarto.processors.autodoc:AutoDocProcessor
]

processor_args:
  AutoDocProcessor: 
      repo_owner: muellerzr
      repo_name: nbquarto
```

## Efficient Notebook Processing

Execute the `nbquarto-process` command to let the configured `Processor`(s) work their magic on your notebooks. All processed notebooks, saved as `qmd` files, land safely in your desired output folder:

```bash
nbquarto-process \
--config_file tests/test_artifacts/single_processor.yaml \
--notebook_file tests/test_artifacts/test_example.ipynb \
--output_folder docs/
```

## `nbdev` Reinvented: Experience `nbquarto`

Transform your understanding of `nbdev` with `nbquarto`, a user-friendly reimagining of the original project. 
Bask in the simplicity of an unambiguous interface for modifying Jupyter Notebooks, enjoy the luxury of minimal abstraction, 
relish clear error messages, and appreciate the adherence to excellent Python coding practices. 