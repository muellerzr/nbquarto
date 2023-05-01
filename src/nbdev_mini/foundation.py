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

    def copy(self):
        return AttributeDictionary(self)
