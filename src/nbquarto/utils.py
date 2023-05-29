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

import importlib.util
import sys
from collections import defaultdict

from .foundation import AttributeDictionary


# The package importlib_metadata is in a different place, depending on the Python version
if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


def is_package_available(pkg_name: str) -> bool:
    """
    Checks if a package is available

    Args:
        pkg_name (`str`):
            The name of the package to check
    """
    package_exists = importlib.util.find_spec(pkg_name) is not None
    if package_exists:
        try:
            _ = importlib_metadata.version(pkg_name)
        except importlib_metadata.PackageNotFoundError:
            return False


def dict2obj(d: dict, dict_function: callable = AttributeDictionary) -> AttributeDictionary:
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
