# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import RequestContext, render_to_response, get_object_or_404, redirect
from arsh.notification.forms import NotificationForm
from arsh.notification.models import Notification

@login_required
def show_notifications(request):
    notifications = Notification.objects.filter(user = request.user).order_by('type')
    notificationList = []
    if notifications:
        tempArray = [notifications[0]]
        for i in range(1, len(notifications)):
        # After this for loop, we have a 2D array that contains notifications separated according to their type
            if (notifications[i-1].type == notifications[i].type):
                tempArray.append(notifications[i])
            else:
                notificationList.append(tempArray)
                tempArray = [notifications[i]]
        notificationList.append(tempArray)

    return render_to_response('notification/show_notifications.html', {
        'notifications': notificationList,
    }, context_instance=RequestContext(request))

@login_required
def show_description(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    return render_to_response('notification/show_details.html', {
        'notification': notification,
        }, context_instance=RequestContext(request))

@login_required
def notification_create(request):
    notificationForm = NotificationForm()
    if request.method == "POST":
        notificationForm = NotificationForm(request.POST)
        if notificationForm.is_valid():
            name            = notificationForm.cleaned_data['name']
            desc            = notificationForm.cleaned_data['description']
            level           = notificationForm.cleaned_data['level']
            created_at      = notificationForm.cleaned_data['created_at']
            type            = notificationForm.cleaned_data['type']
            can_close       = notificationForm.cleaned_data['can_close']
            display_until   = notificationForm.cleaned_data['display_until']
            display_count   = notificationForm.cleaned_data['display_count']
            notification    = Notification(name=name, description=desc, user=request.user, level=level,
                created_at=created_at, type=type, can_close=can_close, display_until=display_until, display_count=display_count)
            notification.save()
            return redirect('/CMS/notifications/')

    return render_to_response('notification/create_notification.html', {
        'notificationForm': notificationForm,
        }, context_instance=RequestContext(request))