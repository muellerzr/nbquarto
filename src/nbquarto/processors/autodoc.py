# coding=utf-8
# Copyright 2023 Zachary Mueller and The HuggingFace Team. All rights reserved.
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
import html
import importlib

from ..imports import is_black_available, is_hf_doc_builder_available
from ..processor import Processor


if is_hf_doc_builder_available():
    from doc_builder.autodoc import (
        _re_example_tags,
        _re_parameter_group,
        _re_parameters,
        _re_raisederrors,
        _re_raises,
        _re_returns,
        _re_returntype,
        _re_yields,
        _re_yieldtype,
        convert_md_docstring_to_mdx,
        find_documented_methods,
        find_object_in_package,
        format_signature,
        get_shortest_path,
        get_source_link,
        is_dataclass_autodoc,
        is_getset_descriptor,
        quality_check_docstring,
    )


def get_signature_component(name, anchor, signature, object_doc, source_link=None, is_getset_desc=False):
    """
    Returns the Quarto `Docstring` component string.
    Args:
    - **name** (`str`) -- The name of the function or class to document.
    - **anchor** (`str`) -- The anchor name of the function or class that will be used for hash links.
    - **signature** (`List(Dict(str,str))`) -- The signature of the object.
    - **object_doc** (`str`) -- The docstring of the the object.
    - **source_link** (Union[`str`, `None`], *optional*, defaults to `None`) -- The github source link of the the object.
    - **is_getset_desc** (`bool`, *optional*, defaults to `False`) -- Whether the type of obj is `getset_descriptor`.
    """

    def inside_example_finder_closure(match, tag):
        """
        This closure find whether parameters and/or returns sections has example code block inside it
        """
        match_str = match.group(1)
        examples_inside = _re_example_tags.search(match_str)
        if examples_inside:
            example_tag = examples_inside.group(1)
            match_str = match_str.replace(example_tag, f"</{tag}>{example_tag}", 1)
            return f"<{tag}>{match_str}"
        return f"<{tag}>{match_str}</{tag}>"

    def regex_closure(object_doc, regex):
        """
        This closure matches given regex & removes the matched group from object_doc
        """
        re_match = regex.search(object_doc)
        object_doc = regex.sub("", object_doc)
        match = None
        if re_match:
            _match = re_match.group(1).strip()
            if len(_match):
                match = _match
        return object_doc, match

    object_doc = _re_returns.sub(lambda m: inside_example_finder_closure(m, "returns"), object_doc)
    object_doc = _re_parameters.sub(lambda m: inside_example_finder_closure(m, "parameters"), object_doc)

    object_doc, parameters = regex_closure(object_doc, _re_parameters)
    # TODO: Get these as part of the docstring that can be rendered.
    # ... Check out `transformers` probably for ideas on it
    object_doc, return_description = regex_closure(object_doc, _re_returns)
    object_doc, returntype = regex_closure(object_doc, _re_returntype)
    object_doc, yield_description = regex_closure(object_doc, _re_yields)
    object_doc, yieldtype = regex_closure(object_doc, _re_yieldtype)
    object_doc, raise_description = regex_closure(object_doc, _re_raises)
    object_doc, raisederrors = regex_closure(object_doc, _re_raisederrors)
    object_doc = object_doc.replace("[`", "`").replace("`]", "`")

    docstring = f"### `{name}` " + f"{{#{anchor}}}"
    docstring += "\n"
    if source_link:
        docstring += f"[\<source\>]({source_link})"
        docstring += '{style="float:right;font-size:.875rem;"}'
    docstring += '\n<p style="font-size:.875rem;line-height:1.25rem;">\n('
    for param in signature:
        if "*" in param["name"] or param["val"] == "":
            docstring += f'**`{param["name"]}`**, '
        else:
            docstring += f'**`{param["name"]}`**`{param["val"]}`, '
    if len(signature) > 0:
        docstring = docstring[:-2]
    docstring += ")\n</p>\n\n"
    docstring += '<div style="font-size:.875rem;line-height:1.25rem;margin-bottom:1.25em; margin-top:1.25em; padding_bottom:0;">'
    if parameters is not None:
        docstring += "**Parameters:**\n\n"

    if parameters is not None:
        parameters_str = ""
        groups = _re_parameter_group.split(parameters)
        group_default = groups.pop(0)
        parameters_str += group_default
        n_groups = len(groups) // 2
        for idx in range(n_groups):
            idx + 1
            title, group = groups[2 * idx], groups[2 * idx + 1]
            parameters_str += f"**{title}**"
            parameters_str += f"*{group}*"
        docstring += parameters_str

    docstring = html.unescape(f"{docstring}\n{object_doc}\n</div>")

    return docstring


def document_object(object_name, package, page_info, full_name=True, anchor_name=None, version_tag_suffix=""):
    """
    Writes the document of a function, class or method.
    Args:
        object_name (`str`): The name of the object to document.
        package (`types.ModuleType`): The package of the object.
        full_name (`bool`, *optional*, defaults to `True`): Whether to write the full name of the object or not.
        anchor_name (`str`, *optional*): The name to give to the anchor for this object.
        version_tag_suffix (`str`, *optional*, defaults to `"src/"`):
            Suffix to add after the version tag (e.g. 1.3.0 or main) in the documentation links.
            For example, the default `"src/"` suffix will result in a base link as `https://github.com/{repo_owner}/{package_name}/blob/{version_tag}/src/`.
            For example, `version_tag_suffix=""` will result in a base link as `https://github.com/{repo_owner}/{package_name}/blob/{version_tag}/`.
    """
    if page_info is None:
        page_info = {}
    if "package_name" not in page_info:
        page_info["package_name"] = package.__name__
    obj = find_object_in_package(object_name=object_name, package=package)
    if obj is None:
        raise ValueError(
            f"Unable to find {object_name} in {package.__name__}. Make sure the path to that object is correct."
        )
    if isinstance(obj, property):
        # Propreties have no __module__ or __name__ attributes, but their getter function does.
        obj = obj.fget

    if anchor_name is None:
        anchor_name = get_shortest_path(obj, package)
    if full_name and anchor_name is not None:
        name = anchor_name
    else:
        name = obj.__name__

    prefix = "class " if isinstance(obj, type) else ""
    object_doc = ""
    signature_name = prefix + name
    signature = format_signature(obj)
    if getattr(obj, "__doc__", None) is not None and len(obj.__doc__) > 0:
        object_doc = obj.__doc__
        if is_dataclass_autodoc(obj):
            object_doc = ""
        else:
            quality_check_docstring(object_doc, object_name=object_name)
            object_doc = convert_md_docstring_to_mdx(obj.__doc__, page_info)

    source_link = get_source_link(obj, page_info, version_tag_suffix)
    is_getset_desc = is_getset_descriptor(obj)
    component = get_signature_component(
        signature_name, anchor_name, signature, object_doc, source_link, is_getset_desc
    )
    return component


def autodoc(object_name, package, methods=None, page_info=None, version_tag_suffix="src/"):
    """
    Generates the documentation of an object, with a potential filtering on the methods for a class.

    Args:
        object_name (`str`): The name of the function or class to document.
        package (`types.ModuleType`): The package of the object.
        methods (`List[str]`, *optional*):
            A list of methods to document if `obj` is a class. If nothing is passed, all public methods with a new
            docstring compared to the superclasses are documented. If a list of methods is passed and ou want to add
            all those methods, the key "all" will add them.
        return_anchors (`bool`, *optional*, defaults to `False`):
            Whether or not to return the list of anchors generated.
        page_info (`Dict[str, str]`, *optional*): Some information about the page.
        version_tag_suffix (`str`, *optional*, defaults to `"src/"`):
            Suffix to add after the version tag (e.g. 1.3.0 or main) in the documentation links.
            For example, the default `"src/"` suffix will result in a base link as `https://github.com/{repo_owner}/{package_name}/blob/{version_tag}/src/`.
            For example, `version_tag_suffix=""` will result in a base link as `https://github.com/{repo_owner}/{package_name}/blob/{version_tag}/`.
    """
    if page_info is None:
        page_info = {}
    if "package_name" not in page_info:
        page_info["package_name"] = package.__name__
    page_info["repo_owner"] = "muellerzr"

    obj = find_object_in_package(object_name=object_name, package=package)
    documentation = document_object(
        object_name=object_name,
        package=package,
        page_info=page_info,
        version_tag_suffix=version_tag_suffix,
    )

    if isinstance(obj, type):
        documentation = document_object(
            object_name=object_name,
            package=package,
            page_info=page_info,
            version_tag_suffix=version_tag_suffix,
            full_name=False,
        )
        documentation = html.unescape(documentation)
        if methods is None:
            methods = find_documented_methods(obj)
        elif "all" in methods:
            methods.remove("all")
            methods_to_add = find_documented_methods(obj)
            methods.extend([m for m in methods_to_add if m not in methods])
        for method in methods:
            method_doc = document_object(
                object_name=f"{object_name}.{method}",
                package=package,
                page_info=page_info,
                full_name=False,
                version_tag_suffix=version_tag_suffix,
            )
            method_doc = html.unescape(method_doc)
            documentation += f'<div style="background:#f7f7f7; border:2px solid #5a5a5a; border-top-width:2px; border-left-width: 2px; border-top-left-radius: 0.75rem; margin-top: 2rem; margin-bottom: 1.5rem; padding-left: 1rem; padding-right: .5rem;">\n#{method_doc}</div>\n'

    style = '<div style="background:#f7f7f7; border:2px solid #5a5a5a; border-top-width:2px; border-left-width: 2px; border-top-left-radius: 0.75rem; margin-top: 2rem; margin-bottom: 1.5rem; padding-left: 1rem; padding-right: .5rem;">\n'
    documentation = f"{style}\n{documentation}\n</div>\n"

    return documentation


class AutoDocProcessor(Processor):
    """
    A processor which will automatically generate API documentation for a given class or method.
    Largely relies on the implementation in [hf-doc-builder](https://github.com/huggingface/doc-builder),
    while adding some customizations for Quarto.

    This processor expects the following directives:

    - `autodoc`, (`str`):
        Should contain the exact import location (or relative) of an object or function to document,
        such as `nbquarto.processors.AutoDocProcessor`.
    - `methods`, (`List[str]`, *optional*):
        A list of methods to expose for the specified class. If nothing is passed, all public methods
        will be documented. If special methods should be documented including all special methods, such
        as `__call__`, the key `all` can be passed along with the special methods to document.

    Examples:

    To expose all public methods:
    ```markdown
    #| autodoc: nbquarto.processors.AutoDocProcessor
    ```

    To specify specific functions to document along with the init:
    ```markdown
    #| autodoc nbquarto.processors.AutoDocProcessor
    #| methods process
    ```

    To expose all public methods and include special or hidden methods:
    ```markdown
    #| autodoc nbquarto.processors.AutoDocProcessor
    #| methods all, __call__
    ```
    """

    cell_types = "markdown"
    directives = ["autodoc", "methods"]

    def __init__(self, notebook, processor_args: dict = {}):
        missing_imports = []
        if not is_hf_doc_builder_available():
            missing_imports.append(["hf-doc-builder", "hf-doc-builder"])
        if not is_black_available():
            missing_imports.append(["black", "black~=23.1"])
        if len(missing_imports) > 0:
            missing_imports = "\n".join(
                [f"- {missing_import[0]} ({missing_import[1]})" for missing_import in missing_imports]
            )
            raise ImportError(
                f"The following packages are required to use the `AutoDocProcessor`:\n    {missing_imports}\nPlease install them and try again."
            )
        super().__init__(notebook)
        self.repo_owner = None
        self.repo_name = None
        # Modules are a reusable dict of module_name: module
        if processor_args is not None:
            self.repo_owner = processor_args.get("repo_owner", None)
            self.repo_name = processor_args.get("repo_name", None)
        self.modules = {}
        self.package_name = None

    def process(self, cell):
        if self.has_directives(cell):
            item_to_document = cell.directives_["autodoc"][0]
            object_name = item_to_document.split(".")[-1]
            if self.package_name is None:
                self.package_name = item_to_document.split(".")[0]
            # Methods will be parsed in as a list of strings we can pass to autodoc
            methods = cell.directives_.get("methods", None)
            import_location = ".".join(item_to_document.split(".")[:-1])
            # Autodoc requires the module to be imported
            if import_location not in self.modules:
                module = importlib.import_module(import_location)
                self.modules[import_location] = module
            else:
                module = self.modules[import_location]
            page_info = {"package_name": self.package_name, "no_prefix": True}
            if self.repo_owner is not None:
                page_info["repo_owner"] = self.repo_owner
            if self.repo_name is not None:
                page_info["repo_name"] = self.repo_name
            cell.source = autodoc(object_name, module, methods=methods, page_info=page_info)
        return cell
