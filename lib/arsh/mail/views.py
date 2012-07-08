# -*- coding: utf-8 -*-
from django.conf                           import settings
from django.contrib.auth.decorators        import login_required
from django.core.urlresolvers              import reverse
from django.db.models.query_utils          import Q
from django.http                           import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts                      import render_to_response, get_object_or_404
from django.template.context               import RequestContext

from arsh.mail.UserManager                 import UserManager
from arsh.mail.Manager                     import DecoratorManager
from arsh.mail.forms                       import ComposeForm, ReplyForm
from arsh.mail.models                      import Label, Thread, Mail




@login_required
def setup(request):
    um = UserManager(request.user)
    um.setup_mailbox()
    return HttpResponse("Mailbox Setup Successful")


@login_required
def see(request, label_slug, thread_slug, archive=False):
    um = UserManager.get(request.user)
    label = get_object_or_404(Label, slug=label_slug) if label_slug else um.get_label(Label.INBOX_LABEL_NAME)
    if not label:
        um.setup_mailbox()
        label = um.get_inbox()
    thread = get_object_or_404(Thread, slug=thread_slug) if thread_slug else None

    if thread:
        if label_slug and not thread.has_label(label):
            raise Http404("Thread not in label")
        return showThread(request, thread)
    return showLabel(request, label, archive)


@login_required
def compose(request):
    initial_to = request.GET.get('to', '')
    initial_cc = request.GET.get('cc', '')
    initial_bcc = request.GET.get('bcc', '')
    up = request.user
    composeForm = ComposeForm()
    if request.method == "POST":
        receivers = request.POST.get('recipients')
        initial_cc = request.POST.get('cc')
        initial_bcc = request.POST.get('bcc')
        initial_to = receivers
        composeForm = ComposeForm(request.POST)
        if composeForm.is_valid():
            subject = composeForm.cleaned_data['title']
            content = composeForm.cleaned_data['content']

            cc = request.POST.get('cc')
            bcc = request.POST.get('bcc')
            Mail.create(content, subject, request.user, parse_address(receivers), cc=parse_address(cc),
                bcc=parse_address(bcc), titles=[u'کاربران'], initial_sender_labels=[u'کاربران'])

            return HttpResponseRedirect(reverse('mail/home'))
    return render_to_response('mail/composeEmail.html', {
        'initial_to': initial_to,
        'initial_cc': initial_cc,
        'initial_bcc': initial_bcc,
        'mailForm': composeForm,
        'all_labels': Label.get_user_labels(up),
        }, context_instance=RequestContext(request))


def showThread(request, thread):
    """
    :type thread: Thread
    """
    up = request.user
    UserManager.get()._cache_user(up)
    referrer = request.META.get('HTTP_REFERER', '')
    if not referrer or not referrer.startswith(settings.SITE_URL + 'mail/'):
        referrer = reverse('mail/home')
    if request.method == "POST":
        # processing reply
        replyForm = ReplyForm(request.POST)
        if replyForm.is_valid():
            content = replyForm.cleaned_data['content']
            Mail.reply(content, up, thread.get_last_mail(), thread) #TODO: enable in middle reply

            replyForm = ReplyForm() # clearing sent reply details
    else:
        replyForm = ReplyForm()

    labels = thread.get_user_labels(up)
    allMails = thread.mails.all().select_related().order_by('created_at')

    tobeShown = []
    #TODO: JOIN!
    for mail in allMails:
        if mail.sender_id == up.id:
            tobeShown.append(mail)
        elif up in mail.recipients.all():
            tobeShown.append(mail)

    env = {'reply': True, 'request': request, 'header': '', 'mark_as_read': True}
    DecoratorManager.get().activate_hook('show_thread', up, allMails[0], env)
    if env['mark_as_read']:
        thread.mark_as_read(up)

    return render_to_response('mail/showThread.html', {
        'user': request.user,
        'up': up,
        'thread': thread,
        'labels': labels,
        'mails': tobeShown,
        'replyForm': replyForm,
        'referrer': referrer,
        'env': env,
        }, context_instance=RequestContext(request))


def showLabel(request, label, archive_mode):
    up = request.user

    tls = Thread.objects.filter(labels=label).order_by('-pk').select_related()
    threads = tls if archive_mode else tls.filter(labels=UserManager.get(up).get_unread_label())[:100]

    env = {'headers': []}
    DecoratorManager.get().activate_hook('show_label', label, threads, up, env)

    return render_to_response('mail/label.html',
            {'threads': threads, 'label': label, 'user': request.user, 'env': env,
             'archive': archive_mode},
        context_instance=RequestContext(request))


@login_required
def createLabel(request):
    title = request.POST.get('title')
    label = Label()
    label.user = request.user
    label.title = title
    label.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def search(request):
    up = request.user
    keywords = request.POST.get('keywords')
    if not keywords:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        tokens = parse_address(keywords)
        search_query = Q()
        for token in tokens:
            search_query = search_query | Q(mails__title__contains=token) | Q(mails__content__contains=token) | Q(
                mails__sender__username__contains=token) | Q(mails__sender__first_name__contains=token) | Q(
                mails__sender__last_name__contains=token) | Q(mails__recipients__username__contains=token) | Q(
                mails__recipients__first_name__contains=token) | Q(mails__recipients__last_name__contains=token)
        answer = Thread.get_user_threads(up).filter(search_query).distinct()

        return render_to_response('mail/label.html', {
            'threads': answer,
            'label': 'نتایج جستجو',
            }, context_instance=RequestContext(request))


def parse_address(input):
    input = input.replace(' ', ';')
    input = input.replace(',', ';')
    tokens = input.split(';')
    result = []
    for s in tokens:
        s = s.strip(' \t\n\r')
        if s: result.append(s)
    return result


def mails_gc():
    """
        تابعی که باید به صورت دوره‌ای اجرا شود و میل‌های حذف شده را از پایگاه داده نیز حذف کند.
    """
    #XXX: do it on label modification?
    Thread.objects.filter(labels__isnull=True).delete()


@login_required
def mark_thread(request, thread_slug, action):
    thread = get_object_or_404(Thread, slug=thread_slug)
    if action == 'read':
        thread.mark_as_read(request.user)
    elif action == 'unread':
        thread.mark_as_unread(request.user)

    if request.is_ajax():
        return HttpResponse('OK')
    return HttpResponseRedirect(
        reverse('mail/see_label', args=[thread.labels.all()[0].slug])) #FIXME: what if no labels?
