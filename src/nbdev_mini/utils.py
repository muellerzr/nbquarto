from collections import defaultdict
from .foundation import AttributeDictionary


def dict2obj(
    d: dict, dict_function: callable = AttributeDictionary
) -> AttributeDictionary:
    """
    Convert (possibly nested) dictionaries (or list of dictionaries)
    to `AttributeDictionary`

    Args:
        d (`dict`):
            A dictionary to convert
        dict_function (`callable`, *optional*, defaults to AttributeDictionary):
            A function to convert dictionaries to
    """
    if isinstance(d, list):
        return list(map(dict2obj, d))
    if not isinstance(d, dict):
        return d
    return dict_function(**{k: dict2obj(v) for k, v in d.items()})


langs = defaultdict(
    r="#",
    python="#",
    julia="#",
    scala="//",
    matlab="%",
    csharp="//",
    fsharp="//",
    c=["/*", "*/"],
    css=["/*", "*/"],
    sas=["*", ";"],
    powershell="#",
    bash="#",
    sql="--",
    mysql="--",
    psql="--",
    lua="--",
    cpp="//",
    cc="//",
    stan="#",
    octave="#",
    fortran="!",
    fortran95="!",
    awk="#",
    gawk="#",
    stata="*",
    java="//",
    groovy="//",
    sed="#",
    perl="#",
    ruby="#",
    tikz="%",
    js="//",
    d3="//",
    node="//",
    sass="//",
    coffee="#",
    go="//",
    asy="//",
    haskell="--",
    dot="//",
    apl="⍝",
)


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
