# -*- coding: utf-8 -*-
from arsh.common.html.builder import Builder

class TodoList(object):
    def __init__(self):
        self._list = []
        self._items = []

    def __unicode__(self):
        return self.render()

    def add_item(self, text, done=False, details='', actions=None):
        if actions is None:
            actions = []
        self._items.append({'text': text, 'done': done, 'details': details, 'actions': actions})

    def render(self):
        def render_item(item):
            li = u'<span>%s</span>' % item['text']
            if item['done']:
                li = u'<span class="strike-out">' + li + u'</span>'
            if item['details']:
                li += ' <span>%s</span>' % item['details']
            for action in item['actions']:
                li += u'&nbsp;&nbsp;<a href="%s">%s</a>' % (action['url'], action['name'])
            return li

        b = Builder()
        b.list(self._items, ordered=True, render_function=render_item)
        return b.render()
