from collections import defaultdict
from .foundation import AttributeDictionary

langs = defaultdict(
    r = "#",
    python = "#",
    julia = "#",
    scala = "//",
    matlab = "%",
    csharp = "//",
    fsharp = "//",
    c = ["/*",  "*/"],
    css = ["/*",  "*/"],
    sas = ["*", ";"],
    powershell = "#",
    bash = "#",
    sql = "--",
    mysql = "--",
    psql = "--",
    lua = "--",
    cpp = "//",
    cc = "//",
    stan = "#",
    octave = "#",
    fortran = "!",
    fortran95 = "!",
    awk = "#",
    gawk = "#",
    stata = "*",
    java = "//",
    groovy = "//",
    sed = "#",
    perl = "#",
    ruby = "#",
    tikz = "%",
    js = "//",
    d3 = "//",
    node = "//",
    sass = "//",
    coffee = "#",
    go = "//",
    asy = "//",
    haskell = "--",
    dot = "//",
    apl = "⍝"
)

def notebook_language(notebook:AttributeDictionary) -> str:
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