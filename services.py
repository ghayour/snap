# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from arsh.common.http.ajax import ajax_view
from .UserManager import UserManager


@ajax_view
def mailbox_info(request):
    username = request.GET.get('username')
    user = get_object_or_404(User, username=username)  # todo: fix for dj6+
    um = UserManager.get(user)
    info = {
        'unread': um.get_inbox().get_unread_count(),
    }
    return info
