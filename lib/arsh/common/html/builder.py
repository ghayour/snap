# -*- coding: utf-8 -*-
from functools import wraps

from django.template import Template, Context
from django.utils.safestring import mark_safe


def processed(func):
    @wraps(func)
    def with_process(*args, **kwargs):
        return func(*args, **kwargs)

    return with_process


class Builder():
    def __init__(self):
        self._html = u""
        self._jQuery = True

    @processed
    def xml(self):
        self._html += '<?xml version="1.0" encoding="utf-8" ?>'

    @processed
    def open_tag(self, tag, **kwargs):
        tag = u"<" + tag
        for attr, val in kwargs.items():
            if attr == 'class_name' or attr == 'attr_class':
                attr = 'class'
            if attr.startswith('data_'):
                attr = attr[:4] + '-' + attr[5:]
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
    def text(self, text):
        #TODO: escape text
        self._html += text

    @DeprecationWarning
    def add_simpletext(self, text):
        self.text(text)

    @processed
    def br(self):
        self._html += u"<br/>"


    @processed
    def hr(self):
        self._html += u"<hr/>"


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
            if attr == 'class_name' or attr == 'attr_class':
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
    def list(self, list, ordered=False, render_function=None):
        if render_function is None:
            render_function = unicode
        tag_name = 'ol' if ordered else 'ul'
        self.open_tag(tag_name)
        for l in list:
            self.tag('li', render_function(l))
        self.close_tag(tag_name)


    @processed
    def select(self, options, **kwargs):
        self.open_tag('select', **kwargs)
        for k, v in options.items():
            self.tag('option', v, attr_value=k)
        self.close_tag('select')


    @processed
    def text_input(self, **kwargs):
        kwargs['id'] = kwargs['name'] #TODO: this is not so predictable
        try:
            label = kwargs.pop('label')
            self.tag('label', label, attr_for=kwargs['id'])
        except KeyError:
            pass
        self.open_tag('input', **kwargs)
        self.close_tag('input')


    def paginate(self, list, per_page):
        #TODO: refactor
        page_nums = len(list) / per_page
        if len(list) % per_page != 0:
            page_nums += 1
        page_counter = 1
        self._html += "<script type='text/javascript'>function goNextPage(pageNum){"
        self._html += "document.getElementById(pageNum).style.display = 'none';"
        self._html += "nextId = pageNum+1; document.getElementById(nextId).style.display = 'block';}"
        self._html += "function goPrevPage(pageNum){ document.getElementById(pageNum).style.display = 'none';"
        self._html += "nextId = pageNum-1; document.getElementById(nextId).style.display = 'block';}"
        self._html += "</script>"

        #first page
        self._html += "<div id='" + str(page_counter) + "'>"
        self.list(list[0:per_page])
        self._html += "<input type='button' value='next' name='" + str(page_counter) + "' onclick='goNextPage(" + str(
            page_counter) + ");'></div>"
        page_counter += 1

        #middle pages
        for i in xrange(per_page, (page_nums - 1) * per_page, per_page):
            self._html += "<div style='display:none;' id='" + str(page_counter) + "'>"
            self.list(list[i:i + per_page])
            self._html += "<input type='button' value='prev' name='" + str(
                page_counter) + "' onclick='goPrevPage(" + str(
                page_counter) + ");'><input type='button' value='next' name='" + str(
                page_counter) + "' onclick='goNextPage(" + str(page_counter) + ");'></div>"
            page_counter += 1

        #last page
        self._html += "<div style='display:none;' id='" + str(page_counter) + "'>"
        self.list(list[(page_nums - 1) * per_page:len(list)])
        self._html += "<input type='button' value='prev' name='" + str(page_counter) + "' onclick='goPrevPage(" + str(
            page_counter) + ");'></div>"


    def ready_script(self, script):
        if self._jQuery:
            self.html('<script type="text/javascript">$(function(){%s});</script>' % script)
        else:
            raise NotImplementedError

    def render(self, safe=True):
        if safe:
            return mark_safe(self._html)
        return self._html


    @staticmethod
    def load_template(html, dic):
        temp = Template(html)
        context = Context(dic)
        return temp.render(context)
