# -*- coding: utf-8 -*-
import base64
import json
import os
import collections
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils import simplejson
from django.contrib.auth.models import User

from arsh.common.http.ajax import ajax_view, post_only
from arsh.storage.file_store import FileStore
from arsh.user_mail.UserManager import UserManager
from arsh.user_mail.Manager import DecoratorManager
from arsh.user_mail.forms import ComposeForm, FwReForm, ContactForm
from arsh.user_mail.config_manager import ConfigManager
from arsh.user_mail.mail_admin import MailAdmin
from arsh.user_mail.models import Label, Thread, Mail, ReadMail, AddressBook, MailProvider, MailReceiver, \
    TemporaryAttachments


def get_default_inbox():
    cf = ConfigManager.prepare()
    if cf.get('inbox-folder') == 'inbox':
        return Label.INBOX_LABEL_NAME
    return cf.get('inbox-folder')


@login_required
def setup(request):
    um = UserManager(request.user)
    um.setup_mailbox()
    return HttpResponse("Mailbox Setup Successful")


@login_required
def see(request, label_slug, thread_slug, archive=None):
    user_manager = UserManager.get(request.user)
    config_manager = ConfigManager.prepare()
    mail_admin = MailAdmin.prepare()

    # MailAccount
    if not mail_admin.user_has_mail_account(request.user):
        # creating a arshmail account for this new user
        mail_admin.create_arsh_mail_account(request.user)

    # label
    label_title = request.GET.get('label_title')
    if label_title:
        if label_slug:
            raise Http404('Either provide label_slug or label_name')
        # TODO: consider mail account in resolving label title
        try:
            label = get_object_or_404(Label, user=request.user, title=label_title)
        except Http404 as e:
            # Some std labels may be created on demand, not for all users by default
            if label_title in Label.STD_LABELS.values():
                label = Label.create(request.user, label_title)
            else:
                raise e
    else:
        if label_slug:
            label = get_object_or_404(Label, user=request.user, slug=label_slug)
        else:
            label = user_manager.get_label(Label.INBOX_LABEL_NAME)
            if not label:
                user_manager.setup_mailbox()
                label = user_manager.get_inbox()

    # thread
    thread = get_object_or_404(Thread, slug=thread_slug) if thread_slug else None
    if thread:
        if label_slug and not thread.has_label(label):
            raise Http404("Thread not in label")
        return show_thread(request, thread, label)

    if archive is None:
        archive = config_manager.get('default-view') == 'archive'
    return show_label(request, label, archive)


@login_required
def compose(request):
    cf = ConfigManager.prepare()

    initial_to = request.GET.get('to', '')
    initial_cc = request.GET.get('cc', '')
    initial_bcc = request.GET.get('bcc', '')
    label_ids = request.POST.get('labels')
    if label_ids:
        label_ids = label_ids.split(',')

    compose_form = ComposeForm()
    result_error = None
    if request.method == "POST":
        mail_uid = request.POST.get('mail_uid')
        # TODO: move these to the ComposeForm
        receivers = request.POST.get('receivers')
        initial_cc = request.POST.get('cc')
        initial_bcc = request.POST.get('bcc')
        initial_to = receivers
        compose_form = ComposeForm(request.POST, request.FILES)
        if compose_form.is_valid():
            subject = compose_form.cleaned_data['title']
            content = compose_form.cleaned_data['content']
            initial_labels = []
            if label_ids:
                initial_labels = list(Label.objects.filter(id__in=label_ids).values_list('title', flat=True))
            initial_labels.append(Label.SENT_LABEL_NAME)
            recipient_labels = [get_default_inbox()]
            if Label.REQUEST_LABEL_NAME in initial_labels:
                recipient_labels.append(Label.REQUEST_LABEL_NAME)
            if Label.TODO_LABEL_NAME in initial_labels:
                recipient_labels.append(Label.TODO_LABEL_NAME)

            # TODO: handle unsupported browsers for file upload
            attachments = TemporaryAttachments.get_mail_attachments(mail_uid) if mail_uid else []

            cc = request.POST.get('cc')
            bcc = request.POST.get('bcc')
            try:
                Mail.create(content, subject, request.user, parse_address(receivers), cc=parse_address(cc),
                            bcc=parse_address(bcc), titles=recipient_labels,
                            initial_sender_labels=initial_labels,
                            attachments=attachments)

                return HttpResponseRedirect(reverse('mail/home'))
            except ValidationError as e:
                result_error = e.messages[0]

    return render_to_response('mail/composeEmail.html', {
        'user': request.user,
        'initial_to': initial_to,
        'initial_cc': initial_cc,
        'initial_bcc': initial_bcc,
        'mailForm': compose_form,
        'all_labels': Label.get_user_labels(request.user),
        'send_error': result_error,
        'mail_uid': base64.urlsafe_b64encode(os.urandom(20)),
    }, context_instance=RequestContext(request))


@login_required
@ajax_view
@post_only
def attach(request):
    try:
        mail_uid = request.POST['mail_uid']
    except KeyError:
        raise Http404()
    uploaded_file = FileStore.handle_upload(request.FILES['file'], namespace=Mail.ATTACHMENTS_STORE_NAMESPACE)
    TemporaryAttachments.objects.create(filename=uploaded_file.name, mail_uid=mail_uid)
    return {}


@login_required
def attachments(request, attachment_slug):
    return FileStore.serve_file(request=request, filename=attachment_slug, namespace=Mail.ATTACHMENTS_STORE_NAMESPACE)

@ajax_view
def show_thread(request, thread, label=None):
    """
    :type thread: Thread
    """

    up = request.user
    cf = ConfigManager.prepare()
    address_book = AddressBook.get_addressbook_for_user(up, create_new=True)
    if label:
        UserManager.get()._cache_user(up)
    referrer = request.META.get('HTTP_REFERER', '')

    if not referrer or not referrer.startswith(settings.SITE_URL + 'mail/') \
            or referrer.startswith(settings.SITE_URL + 'mail/view'):
        referrer = reverse('mail/home')

    if request.method == "POST":
        #mail_uid = request.POST.get('mail_uid')
        mail_id = request.POST.get('mail_id', '')
        selected_mail = Mail.objects.get(pk=mail_id)
        #attachments = request.FILES.getlist('attachments[]')
        # TODO: handle unsupported browsers for file upload
        #attachments = TemporaryAttachments.get_mail_attachments(mail_uid) if mail_uid else []

        fw_re_form = FwReForm(request.POST, request.FILES, user_id=up.id)
        #fw_re_form = ComposeForm(request.POST, request.FILES)

        if fw_re_form.is_valid():
            content = fw_re_form.cleaned_data['content']
            title = fw_re_form.cleaned_data['title']
            receivers = parse_address(fw_re_form.cleaned_data['receivers'])
            cc = parse_address(fw_re_form.cleaned_data['cc'])
            bcc = parse_address(fw_re_form.cleaned_data['bcc'])

            if request.POST.get('re-fw', '') == 'forward':
                Mail.create(content=content, subject=title, sender=up, receivers=receivers,
                            cc=cc, bcc=bcc, thread=thread,
                            titles=[get_default_inbox()],
                            attachments=attachments)

            elif request.POST.get('re-fw', '') == 'reply':
                Mail.reply(content=content, sender=up, receivers=receivers,
                           cc=cc, bcc=bcc, in_reply_to=selected_mail, subject=title,
                           thread=thread,
                           titles=[get_default_inbox()], attachments=attachments)  # TODO: enable in middle reply

            fw_re_form = FwReForm(user_id=up.id)  # clearing sent mail details
            #fw_re_form = ComposeForm()  # clearing sent mail details
    else:
    #     fw_re_form = FwReForm(user_id=up.id)
        #fw_re_form = ComposeForm()
        action = request.GET.get('action', '')
        if request.is_ajax():
            re_cc =[]
            re_to = []
            re_mail_id = request.GET.get('mail', '')
            re_mail = Mail.objects.get(id=re_mail_id)
            receivers = MailReceiver.objects.filter(mail=re_mail)
            sender = re_mail.sender.username
            #
            if action=='reply-all':
                if sender != up.username :
                    re_to = [re_mail.sender.username]
                    for mr in receivers :
                        username = mr.user.username
                        if (mr.type == 'to' and username != up.username) or mr.type == 'cc' :
                            re_cc.append(username)


                else:
                    for mr in receivers :
                        username = mr.user.username
                        if mr.type == 'to':
                            re_to.append(username)
                        elif mr.type == 'cc':
                            re_cc.append(username)




            elif action == 'reply':
                if sender != up.username:
                    re_to = [re_mail.sender.username]
                else :
                    for mr in receivers :
                        username = mr.user.username
                        if mr.type == 'to':
                            re_to.append(username)





            data = {'to':re_to ,'cc': re_cc }
            return data

        else:
            fw_re_form = FwReForm(user_id=up.id)



    labels = thread.get_user_labels(up)

    labels = labels.exclude(title__in=[Label.SENT_LABEL_NAME, Label.TRASH_LABEL_NAME, Label.ARCHIVE_LABEL_NAME])
    all_mails = thread.get_user_mails(up)

    tobe_shown = collections.OrderedDict()
    mails_labeled = []
    for mail in all_mails:
        tobe_shown[mail] = mail.get_user_labels(up)
        if tobe_shown[mail]:
            for t in tobe_shown[mail]:
                l = t.label
                labels = labels.exclude(title = l.title)
        if mail.has_label(label):
                mails_labeled.append(mail)
    if not tobe_shown:
        return HttpResponseRedirect(reverse('mail/home'))

    env = {'reply': True, 'request': request, 'header': '', 'mails': all_mails}
    ReadMail.mark_mails(request.user, tobe_shown)
    unread = ReadMail.mark_as_read(request.user, tobe_shown)

    #END OF MOVE
    DecoratorManager.get().activate_hook('show_thread', all_mails[0], env)

    if not unread:
        try:
            thread.mark_as_read(up)
        except:
            pass


    if mails_labeled :
        all_mails = mails_labeled

    return render_to_response('mail/showThread.html', {
        'user': request.user,
        'up': up,
        'thread': thread,
        'label': label,
        'labels': labels,
        'ordered_mails': all_mails,
        'mails': tobe_shown,
        'fw_re_form': fw_re_form,
        'referrer': referrer,
        'env': env,
        'last_index': len(tobe_shown),
        #'user': request.user,
        #'initial_to': initial_to,
        #'initial_cc': initial_cc,
        #'initial_bcc': initial_bcc,
        ##'mailForm': compose_form,
        #'all_labels': Label.get_user_labels(request.user),
        #'send_error': result_error,
        #'mail_uid': base64.urlsafe_b64encode(os.urandom(20)),

    }, context_instance=RequestContext(request))


def show_label(request, label, archive_mode):
    user = request.user

    #Done: improve
    #TODO: Test
    related_threads = Thread.related_threads(user)
    if archive_mode:
        threads = related_threads.filter(labels=label).order_by('-pk').select_related()
    else:
        threads = related_threads.filter(Q(labels=label) &
                    Q(labels=UserManager.get(user).get_unread_label())).order_by('-pk').select_related()

    #improve here (too much query) ---> above
    #tls = Thread.objects.filter(labels=label).order_by('-pk').select_related()
    #threads = tls if archive_mode else tls.filter(labels=UserManager.get(user).get_unread_label())
    #threads = threads.related_threads(user)
    #threads = [t for t in threads if t.is_thread_related(user)]

    #threads = threads[:50]  # TODO: how to view all mails?

    env = {'headers': []}
    DecoratorManager.get().activate_hook('show_label', label, threads, user, env)

    return render_to_response('mail/label.html',
                              {'threads': threads, 'label': label, 'label_title': label.title, 'user': request.user,
                               'env': env,
                               'archive': archive_mode,
                               },
                              context_instance=RequestContext(request))


@login_required
def manage_label(request):
    user = request.user

    if request.is_ajax() and request.POST:
        action = request.POST.get('name')
        id1 = request.POST.get('pk')
        l = Label.objects.get(user=user, id=id1)
        if action == 'delete':
            l.delete()
        else:
            title = request.POST.get('value')
            l.title = title
            l.save()

    label = Label.get_user_labels(user)
    initial = Label.get_initial_labels()
    init_label = []
    for l in initial:
        init_label.append(Label.get_label_for_user(l, user))
        label = label.exclude(title=l)
    return render_to_response('mail/manage_label.html',
                              {'labels': label,
                               'init_label': init_label},
                              context_instance=RequestContext(request))


@ajax_view
def mail_validate(request):
    #rl = []
    x = request.POST.get('receivers', '')
    y = request.POST.get('cc', '')
    z = request.POST.get('bcc', '')
    rl = [x, y, z]

    for r in rl:
        if r:
            for c in r.split(','):
                if not Mail.validate_receiver(c):
                    return {"error": "گیرنده نامعتبر است."}
    return 'Ok'


@login_required
def create_label(request):
    title = request.POST.get('title')
    label = Label()
    label.user = request.user
    label.title = title
    label.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@ajax_view
def add_label(request):
    c = {}
    item_list = []
    label_id = int(request.POST['label_id'])
    item_type = request.POST['item_type']
    response_text = u"تغییری داده نشد."
    if request.POST.get('item_id', ''):
        item_list.append(request.POST['item_id'])
    else:
        item_list = request.POST.getlist('item_id[]')
    if not item_list:
        response_text = u"یک نامه برای برچسب گذاری انتخاب شود."

    if label_id >= 0:
        # existing label
        label = Label.objects.get(id=label_id)
    else:
        label_name = request.POST['label_name']
        label_name = label_name.split(u'(برچسب جدید)')[0]
        label = Label.create(user=request.user, title=label_name.strip())
        c['new_label'] = True
    label_url = "/mail/view/%s/" % label.slug

    if item_type == "mail":
        for mail_id in item_list:
            mail = Mail.objects.get(id=mail_id)
            if mail.add_label(label):
                response_text = "success"
            else:
                response_text = "قبلا نامه یا نخ حاوی آن برچسب زده شده است."

    elif item_type == "thread":
        for thread_id in item_list:
            thread = Thread.objects.get(id=int(thread_id))
            if thread.add_label(label):
                if label.title == Label.COMPLETED_LABEL_NAME:
                    thread.complete_todo()
                response_text = "success"
            else:
                response_text = "قبلا برچسب گذاری صورت گرفته است."
    else:
        response_text = "error"
    c.update({"response_text": response_text, "label_url": label_url, "label_id": label.id})
    return c


@ajax_view
def label_list(request):
    start = request.GET.get('name_startsWith')
    request_type = request.GET.get('request_type')
    labels = Label.objects.filter(user=request.user, title__startswith=start)
    if request_type == 'list':
        #prepare label list for compose form
        data = {'results': []}
        #labels = labels.exclude(title__in=Label.get_initial_labels())
        for label in labels:
            data['results'].append({'id': label.id, 'text': label.title})
        return data
    if request.GET.get('current_label', ''):
        labels.exclude(id=int(request.GET.get('current_label')))

    json_text = '['
    new_label_text = u'(برچسب جدید)'
    for label in labels:
        if not label.limited_labels():
            json_text += '{"value":"' + str(label.id) + '" , "label":"' + label.title + '"},'
    if not UserManager.get(request.user).get_label(start.strip()):
        json_text += '{"value":"' + '-1' + '" , "label":"' + start + ' ' + new_label_text + ' "},'
    json_text = json_text[:-1] + ']'

    return HttpResponse(json_text)


def delete_label(request):
    c = {"response_text": "error", }

    try:
        if request.POST.get('label_id', ''):
            label = Label.objects.get(user=request.user, id=int(request.POST['label_id']))
        if request.POST.get('current_label', ''):
            current_label = Label.objects.get(id=int(request.POST['current_label']))
        item_type = request.POST.get('item_type', '')
        if item_type == "mail":
            if request.POST.get('item_id', ''):
                mail = Mail.objects.get(id=int(request.POST['item_id']))
                mail.remove_label(label)
                c["response_text"] = "success"
                thread = mail.thread

        elif item_type == "thread":
            if request.POST.get('item_id', ''):
                thread = Thread.objects.get(id=int(request.POST['item_id']))
                thread.remove_label(label)
                c["response_text"] = "success"
                label_count = len(thread.get_user_labels(request.user).exclude(
                    title__in=[Label.SENT_LABEL_NAME, Label.UNREAD_LABEL_NAME]))
                if label_count == 0:
                    thread.add_label(Label.get_label_for_user(Label.ARCHIVE_LABEL_NAME, request.user))
                    c["archive_text"] = u"به بایگانی منتقل گردید."

        if current_label and not thread.has_label(current_label):
            c["referrer"] = reverse('mail/see_label', args=[request.POST.get('current_label_slug')])
    except:
        pass

    return HttpResponse(simplejson.dumps(c))


@ajax_view
def move_thread(request):
    c = {"response_text": "error", }
    thread_list = []
    label_name = request.POST.get('label')
    if label_name:
        real_title = Label.parse_label_title(label_name)
        label = UserManager.get(request.user).get_label(real_title)
    else:
        try:
            label_id = int(request.POST['label_id'])
        except (KeyError, ValueError):
            raise Http404('invalid arguments')
        else:
            if label_id >= 0:
                try:
                    label = Label.objects.get(id=label_id)
                except Label.DoesNotExist:
                    label = None
            else:
                label_name = request.POST['label_name']
                label_name = label_name.split(u'(برچسب جدید)')[0]
                label = Label.create(user=request.user, title=label_name.strip())
    if label is None:
        raise Http404('Invalid label: {0}'.format(label))

    current_label = None
    if request.POST.get('current_label', ''):
        current_label = Label.objects.get(id=int(request.POST.get('current_label')))

    if request.POST.get('item_id', ''):
        thread_list.append(request.POST['item_id'])
    else:
        thread_list = request.POST.getlist('item_id[]')

    for thread_id in thread_list:
        try:
            thread = Thread.objects.get(id=int(thread_id))
        except (ValueError, Thread.DoesNotExist):
            raise Http404('Invalid thread id')
        if label.limited_labels():
            for lbl in thread.get_user_labels(request.user).exclude(title=Label.UNREAD_LABEL_NAME):
                thread.remove_label(lbl)
                if lbl.title == Label.TRASH_LABEL_NAME:
                    return {'response_text': 'success'}
        else:
            thread.remove_label(current_label)  # todo: fix this
        thread.add_label(label)
        c['response_text'] = "success"
    return c


def get_search_query(token, user):
    dict_query = {
        u'از':  Q(mails__sender__username__contains=token[1]) |
                Q(mails__sender__first_name__contains=token[1]) |
                Q(mails__sender__last_name__contains=token[1]),
        u'به':  Q(mails__recipients__username__contains=token[1]) |
                Q(mails__recipients__first_name__contains=token[1]) |
                Q(mails__recipients__last_name__contains=token[1]),
        u'عنوان': Q(mails__title__contains=token[1]),
        u'محتوا': Q(mails__content__contains=token[1]),
        u'برچسب': search_labels
    }
    rs = dict_query.get(token[0], 0)
    if hasattr(rs, '__call__'):
        return rs(token[1], user)
    return rs


def search_labels(keyword, user):
    labels_list = keyword.split(u'،')
    search_query = Q()
    user_labels = Label.get_user_labels(user)
    for label in labels_list:
        if label:
            search_query = search_query | (Q(labels__title__contains=label) & Q(labels__in=user_labels))
    return search_query


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
            try:
                tuple_keywords = token.split(':')
                query = get_search_query(tuple_keywords, up)
                if not query:
                    raise ValueError
                if not search_query:
                    search_query = query
                else:
                    search_query = search_query & query
            except (IndexError, ValueError):
                raise Http404(u"عبارت جستجو را به درستی وارد نمایید.")

        answer = Thread.get_user_threads(up).filter(search_query).distinct()
        return render_to_response('mail/label.html', {
            'threads': answer,
            'label_title': 'نتایج جستجو',
            'search_exp': keywords
        }, context_instance=RequestContext(request))


def parse_address(input_s):
    input_s = input_s.replace(',', ';')
    tokens = input_s.split(';')
    result = []
    for s in tokens:
        s = s.strip(' \t\n\r')
        if s:
            result.append(s)
    return result


def mails_gc():
    """
        تابعی که باید به صورت دوره‌ای اجرا شود و میل‌های حذف شده را از پایگاه داده نیز حذف کند.
    """
    Thread.objects.filter(labels__isnull=True).delete()


@login_required
def mark_thread(request, thread_slug, action):
    thread = get_object_or_404(Thread, slug=thread_slug)
    if action == 'read':
        if thread.is_unread(request.user):
            thread.mark_as_read(request.user)
    elif action == 'unread':
        if not thread.is_unread(request.user):
            thread.mark_as_unread(request.user)

    if request.is_ajax():
        return HttpResponse('OK')
    return HttpResponseRedirect(
        reverse('mail/see_label', args=[thread.labels.all()[0].slug]))
        #FIXME: what if no labels?


@login_required
def ajax_mark_thread(request):
    thread_list = []
    if 'item_id[]' in request.POST:
        thread_list = request.POST.getlist('item_id[]')
    action = request.POST.get('action', '')
    response_text = "success"
    if not thread_list:
        response_text = u"حداقل یک نامه باید انتخاب شود."
    else:
        if action == 'read':
            for thread_id in thread_list:
                thread = Thread.objects.get(id=int(thread_id))
                if thread.is_unread(request.user):
                    thread.mark_as_read(request.user)
        elif action == 'unread':
            for thread_id in thread_list:
                thread = Thread.objects.get(id=int(thread_id))
                if not thread.is_unread(request.user):
                    thread.mark_as_unread(request.user)
        else:
            response_text = u"عملیات درخواستی امکان پذیر نیست."

    return HttpResponse(simplejson.dumps({'response_text': response_text, }))


#TODO: correct that based on changes/where is used?
@ajax_view
def get_total_unread_mails(request):
    total_unread_mails = 0
    user = request.user
    unread_label = UserManager.get(user).get_unread_label()
    labels = Label.objects.raw("""
        SELECT l.id,l.title,l.slug,
          (SELECT COUNT(*) FROM mail_threadlabel tl
            WHERE
              tl.label_id=l.id
            AND
              (SELECT COUNT(*) FROM mail_threadlabel tl2
                 WHERE tl2.label_id=%d AND tl2.thread_id=tl.thread_id
              )>0
          ) AS unread_threads_count
        FROM mail_label l
        WHERE l.user_id=%d AND l.title <> 'unread'
        ORDER BY title
    """ % (unread_label.id, user.id))
    for label in labels:
        unread = 0
        for t in label.threads.all():
            unread += len(t.get_unread_mails(user))
        if label.title != Label.SENT_LABEL_NAME:
            total_unread_mails += unread
    return total_unread_mails


@ajax_view
def mail_reply(request):
    try:
        mail_id = request.POST.get("mail_id", -1)
        mail = Mail.objects.get(pk=mail_id)
        replies = list(mail.get_reply_mails())
    except Mail.DoesNotExist:
        replies = []
    return replies


@ajax_view
def add_contact(request):
    try:
        user_id = request.POST.get("user_id", -1)
        user = get_object_or_404(User, pk=user_id)
        contact_user_id = request.POST.get("contact_user_id", -1)
        contact_user = get_object_or_404(User, pk=contact_user_id)
        if request.POST.get('action', 'add') == 'validate':
            ab = AddressBook.get_addressbook_for_user(user, create_new=True)
            if ab.has_contact_address(contact_user.username + '@' + MailProvider.get_default_domain()) \
                    or contact_user == user:
                return {'result': False}
            else:
                return {'result': True}
        contact = AddressBook.get_addressbook_for_user(user, create_new=True).add_contact_by_user(contact_user)
        return {'id': contact.id, 'display_name': contact.get_display_name()}
    except ValueError as e:
        return {'errors': unicode(e.message)}


@ajax_view
def contact_list(request):
    try:
        data = {'results': []}
        user_id = request.POST.get("user_id", -1)
        q = request.POST.get("q", -1)

        user = get_object_or_404(User, pk=user_id)
        all_contacts = AddressBook.get_addressbook_for_user(user, create_new=True).get_all_contacts().filter(
            Q(display_name__startswith=q) | Q(first_name__startswith=q) | Q(last_name__startswith=q) | Q(
                email__startswith=q))
        for c in all_contacts:
            data['results'].append({'id': c.email, 'text': c.email})
        return data
    except ValueError as e:
        pass


@login_required
def addressbook_edit(request):

    if request.is_ajax() and request.POST:
        user = request.user
        value = request.POST.get('value')
        field = request.POST.get('name')
        pk = request.POST.get('pk')
        contacts = AddressBook.objects.get(user=user).get_all_contacts()
        newcontact = contacts.get(pk=pk)
        if field == 'displayname':
            newcontact.display_name = value
        if field == 'firstname':
            newcontact.first_name = value
        elif field == 'lastname':
            newcontact.last_name = value
        elif field == 'email':
            newcontact.email = value
        elif field == 'ex_email':
            newcontact.additional_email = value
        newcontact.save()
        return HttpResponse(json.dumps(value), content_type='application/json')
    return HttpResponseNotAllowed(['post'])


@login_required
def addressbook_view(request):
    user = request.user
    contacts = AddressBook.objects.get_or_create(user=user)[0].get_all_contacts()
    contact_form = ContactForm()
    if request.is_ajax() and request.method == 'POST':
        pk = request.POST.get('pk')
        contacts = AddressBook.objects.get(user=user).get_all_contacts()
        delete_contact = contacts.get(pk=pk)
        delete_contact.delete()

    return render_to_response('mail/address_book.html', {'contacts': contacts},
                              context_instance=RequestContext(request))
