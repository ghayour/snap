# -*- coding: utf-8 -*-
from django.forms import ClearableFileInput


class MultiFileInput(ClearableFileInput):
    input_type = 'file'
    needs_multipart_form = True

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}

        if attrs.has_key('class'):
            attrs['class'] += ' multi'
        else:
            attrs['class'] = 'multi'

        name += '[]'

        return super(MultiFileInput, self).render(name, None, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        return files.get(name+'[]', None)
