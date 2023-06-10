# Copyright 2023 Zachary Mueller. All rights reserved.
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

import logging

from ..processor import RawPostProcessor


logger = logging.getLogger(__name__)

# This is the javascript that will be injected into the top of the notebook
# to enable semantic versioning of the documentation

REFERENCE_JAVASCRIPT = """/**
 * Enables semantic versioning through careful sidebar menu item selection.
 * Hide sidebar menu items that are not related to the current page that is open.
 * Assumes a directory structure of:
 *   - version_1
 *    - page_1
 *    - page_2
 *  - version_2
 *    - page_2
 *    - page_3
 *
 * If version_1 is open, then version_2 and it's pages will not be visible to the sidebar.
 * These will also link to {url}/{version_num}/page_{num}.
 *
 * In the `_quarto.yml` sidebar *must* be set to `auto` for this to work.
 */
var all_versioned_menus = $(".sidebar-menu-container > .list-unstyled").children()
// Get the current url, which should be something like: /branch_name/{version_number}/{something}
// the latter parts after the version number are not important nor will be in there.
// eventually need to handle a special case when we use the latest stable version
var url = window.location.pathname.split("/")[1]
url = `/${url}/`

// Create a dropdown menu for the versions
var version_menu = '<select id="version-menu" class="form-input mr-1 !mt-0 !w-20 rounded !border border-gray-200 p-1 text-xs uppercase dark:!text-gray-400" style="width:100%;">'
raw_urls = []

function AddVersion(index, version_value, version_url){
    if (window.location.pathname.split("/")[1] === version_value){
        version_menu += `<option value="${version_value}" version-url="${version_url}" selected>${version_value}</option>`
    }
    else{
        version_menu += `<option value="${version_value}" version-url="${version_url}">${version_value}</option>`
    }
}

(all_versioned_menus).each(
    (index) => {
        let menu = all_versioned_menus[index]
        let version_url = $(menu).find(`a[href]`)[0].href
        let version = version_url.split("/").at(-2)
        // Add the version number to the list of version numbers
        AddVersion(index, version, version_url)
    }
)

version_menu += '</select>'

// Add the version menu to the sidebar
let container = $(".sidebar-menu-container")
container.prepend(version_menu)

// Add the event listener to the version menu
$(document).ready(function() {
    $('#version-menu').on('change', function() {
        var nSelectOption = $('#version-menu').find(':selected');
        window.location.href = nSelectOption.attr('version-url');
    });
});

// Hide all non-active versioned menus
for (var versioned_menu of all_versioned_menus){
    // Check if the current url extension is in the sidebar menu
    var active_sidebar = $(versioned_menu).find(`a[href*="${url}"]`)[0]
    // If it is, wrap it in a div so it's easily recognizeable
    if (active_sidebar !== undefined){
        $(active_sidebar).parent().parent().wrap("<div id='active-sidebar'></div>")
    }
    // Else hide the additional menus
    else {
        versioned_menu.style.display = "none"
    }
}"""

# We inject it directly to the markdown so there doesn't have to be other random files we need to worry about
REFERENCE_JQUERY = '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.3/jquery.min.js"></script>'
REFERENCE_JAVASCRIPT = f"<script>{REFERENCE_JAVASCRIPT}</script>"


class SemanticVersioningProcessor(RawPostProcessor):
    """
    A processor which will inject javascript into the top of the `qmd`
    to enable semantic versioning of the documentation by hiding parts
    of the sidebar.

    Assumes your documentation structure is as follows:

    ```
    - docs/
        - version_1
            - page_1.qmd
            - page_2.qmd
        - version_2
            - page_1.qmd
            - page_2.qmd
    ```

    From here, the sidebar will be populated based on the
    current opened page and its semantic version. So if
    you are on `/docs/version_1/page_1`, the sidebar will
    hide all of `version_2`'s pages (and any others there may be),
    and only show `version_1`.
    """

    def process(self):
        replacement_str = "\n".join([REFERENCE_JQUERY, REFERENCE_JAVASCRIPT])
        if replacement_str not in self.content:
            self.content = "\n".join([REFERENCE_JQUERY, REFERENCE_JAVASCRIPT, self.content])
        return self.content
