# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from arsh.user_mail.todo.todo_item import TodoItem


def todo_dashboard(request):
    todos = TodoItem.get_all_user_todos(request.user)

    return render_to_response('todo/dashboard.html', {
        'todos': sorted(todos, key=lambda td: td.due),
    }, context_instance=RequestContext(request))
