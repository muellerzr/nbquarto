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
    name = name.replace("class ", "")

    docstring = f"### `{name}` " + f"{{#{anchor}}}"
    docstring += "\n"
    if source_link:
        docstring += f"[\<source\>]({source_link})"
        docstring += '{style="float:right;font-size:.875rem;"}'
    docstring += '\n<p style="font-size:.875rem;line-height:1.25rem;">\n('
    for param in signature:
        docstring += f'**`{param["name"]}`**{param["val"]}, '
    if len(signature) > 0:
        docstring = docstring[:-2]
    docstring += ")\n</p>\n\n"
    docstring += '<div style="font-size:.875rem;line-height:1.25rem;margin-bottom:1.25em; margin-top:1.25em; padding_bottom:0;">'
    if parameters is not None:
        docstring += "**Parameters:**\n"

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

    return docstring + f"\n{object_doc}\n</div>"


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


def autodoc(object_name, package, methods=None, return_anchors=False, page_info=None, version_tag_suffix="src/"):
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
            documentation += f"\n#{method_doc}\n"

    return documentation
