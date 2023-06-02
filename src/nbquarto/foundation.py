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


class AttributeDictionary(dict):
    """
    `dict` subclass that also provides access to keys as attributes.

    Example:
        ```python
        >>> d = AttrDict({'a': 1, 'b': 2})
        >>> d.a
        1
        >>> d.b
        2
        >>> d.c = 3
        >>> d['c']
        3
        ```
    """

    def __getattr__(self, k):
        if k not in self:
            raise AttributeError(k)
        return self[k]

    def __setattr__(self, k, v):
        is_private = k[0] == "_"
        if is_private:
            super().__setattr__(k, v)
        else:
            self[k] = v

    def __dir__(self):
        res = [*self.keys()]
        res.extend(super().__dir__())
        return res
