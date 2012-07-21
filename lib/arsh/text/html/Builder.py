# -*- coding: utf-8 -*-

from functools                             import wraps

from django.conf                           import settings
from django.template                       import Template, Context
from django.utils.safestring import mark_safe




def processed(func):
    @wraps(func)
    def with_process(*args, **kwargs):
        return func(*args, **kwargs)

    return with_process



class Builder():
    def __init__(self):
        self._html = u""

    @processed
    def open_tag(self, tag, **kwargs):
        tag = u"<" + tag
        for attr, val in kwargs.items():
            if attr.startswith('attr_'):
                attr = attr[5:]
            tag += ' %s="%s"' % (attr, val)
        tag += u"> "
        self._html += tag


    @processed
    def close_tag(self, tag):
        self._html += u"</" + tag + u">"


    def close_all(self):
        pass


    @processed
    def clear(self):
        self._html = u''


    @processed
    def html(self, html):
        self._html += html


    @processed
    def br(self):
        self._html += u"<br/>"


    @processed
    def tag(self, tag_name, html, **kwargs):
        self.open_tag(tag_name, **kwargs)
        self.html(html)
        self.close_tag(tag_name)


    @processed
    def single_tag(self, tag_name, **kwargs):
        u"""
            e.g: <a href=... />
        """
        tag = u"<" + tag_name
        for attr, val in kwargs.items():
            if attr == 'class_name':
                attr = 'class'
            tag += ' %s="%s"' % (attr, val)
        self._html += tag
        self._html += ' />'


    @processed
    def p(self, html, **kwargs):
        return self.tag('p', html, **kwargs)


    @processed
    def wrap_by(self, tag_name, **kwargs):
        h = self.render()
        self.clear()
        self.open_tag(tag_name, **kwargs)
        self.html(h)
        self.close_tag(tag_name)


    @processed
    def list(self, list):
        answer = u"<ul>"
        for l in list:
            answer += u"<li> " + l.__unicode__() + u"</li>"
        answer += u"</ul>"
        self._html += answer

    @processed
    def open_list(self):
        self._html += u'<ul>'

    @processed
    def li(self, html, **kwargs):
        self.tag('li', html, **kwargs)

    @processed
    def close_list(self):
        self._html += u'</ul>'


    @processed
    def select(self, options, **kwargs):
        try:
            selected_value = kwargs.pop('selected_value')
        except KeyError:
            selected_value = None
        self.open_tag('select', **kwargs)
        for k, v in options.items():
            if selected_value == k:
                self.tag('option', v, attr_value=k, attr_selected='selected')
            else:
                self.tag('option', v, attr_value=k)
        self.close_tag('select')


    @processed
    def text_input(self, **kwargs):
        if not kwargs.get('id'):
            kwargs['id'] = kwargs['name']
        try:
            label = kwargs.pop('label')
            label_properties = {}
            for k,v in kwargs.items():
                if k.startswith('label_'):
                    label_properties[k[6:]] = v
            for k in label_properties.keys():
                kwargs.pop('label_'+k)
            self.tag('label', label, attr_for=kwargs['id'], **label_properties)
        except KeyError:
            pass
        self.open_tag('input', **kwargs)
        self.close_tag('input')


    def render(self, safe=True):
        if safe:
            return mark_safe(self._html)
        return self._html


    def load_template_code(self, html, context):
        temp = Template(html)
        context = Context(context)
        self.html(temp.render(context))

    def load_template_file(self, filename, context):
        #TODO: search in all template_dirs in order
        code = open(settings.BASEPATH + 'templates/' + filename).read()
        self.load_template_code(code, context)
