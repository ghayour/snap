# -*- coding: utf-8 -*-
import smtplib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils import simplejson
from django.contrib.auth.models import User

from arsh.common.http.ajax import ajax_view
from arsh.user_mail.UserManager import UserManager
from arsh.user_mail.Manager import DecoratorManager
from arsh.user_mail.config_manager import ConfigManager
from arsh.user_mail.forms import ComposeForm, FwReForm
from arsh.user_mail.models import Label, Thread, Mail, ReadMail, AddressBook, Contact, MailAccount, MailProvider


@login_required
def setup(request):
    um = UserManager(request.user)
    um.setup_mailbox()
    return HttpResponse("Mailbox Setup Successful")


@login_required
def see(request, label_slug, thread_slug, archive=None):
    user_manager = UserManager.get(request.user)
    config_manager = ConfigManager.prepare()

    # MailAccount
    accounts = request.user.mail_accounts.all().count()
    if not accounts:
        # creating a arshmail account for this new user
        MailAccount.objects.create(user=request.user, provider=MailProvider.get_default_provider(),
                                   email=request.user.username + '@' + MailProvider.get_default_domain())

    # label
    label = get_object_or_404(Label, user=request.user, slug=label_slug) if label_slug else user_manager.get_label(
        Label.INBOX_LABEL_NAME)
    if not label:
        user_manager.setup_mailbox()
        label = user_manager.get_inbox()

    # thread
    thread = get_object_or_404(Thread, slug=thread_slug) if thread_slug else None
    if thread:
        if label_slug and not thread.has_label(label):
            raise Http404("Thread not in label")
        return showThread(request, thread, label)

    if archive is None:
        archive = config_manager.get('default-view') == 'archive'
    return showLabel(request, label, archive)


@login_required
def compose(request):
    initial_to = request.GET.get('to', '')
    initial_cc = request.GET.get('cc', '')
    initial_bcc = request.GET.get('bcc', '')
    up = request.user
    cf = ConfigManager.prepare()
    composeForm = ComposeForm()
    result_error = None
    if request.method == "POST":
        receivers = request.POST.get('receivers')
        initial_cc = request.POST.get('cc')
        initial_bcc = request.POST.get('bcc')
        initial_to = receivers
        composeForm = ComposeForm(request.POST, request.FILES)
        if composeForm.is_valid():
            subject = composeForm.cleaned_data['title']
            content = composeForm.cleaned_data['content']
            attachments = request.FILES.getlist('attachments[]')

            cc = request.POST.get('cc')
            bcc = request.POST.get('bcc')
            try:
                Mail.create(content, subject, request.user, parse_address(receivers), cc=parse_address(cc),
                            bcc=parse_address(bcc), titles=[cf.get('inbox-folder')],
                            initial_sender_labels=[Label.SENT_LABEL_NAME],
                            attachments=attachments)

                return HttpResponseRedirect(reverse('mail/home'))
            except ValidationError as e:
                result_error = e.messages[0]

    return render_to_response('mail/composeEmail.html', {
        'user': up,
        'initial_to': initial_to,
        'initial_cc': initial_cc,
        'initial_bcc': initial_bcc,
        'mailForm': composeForm,
        'all_labels': Label.get_user_labels(up),
        'send_error': result_error
    }, context_instance=RequestContext(request))


def showThread(request, thread, label=None):
    """
    :type thread: Thread
    """

    up = request.user
    cf = ConfigManager.prepare()
    address_book = AddressBook.get_addressbook_for_user(up, create_new=True)
    if label:
        UserManager.get()._cache_user(up)
    referrer = request.META.get('HTTP_REFERER', '')

    if not referrer or not referrer.startswith(settings.SITE_URL + 'mail/') or referrer.startswith(
                    settings.SITE_URL + 'mail/view'):
        referrer = reverse('mail/home')

    if request.method == "POST":
        mail_id = request.POST.get('mail_id', '')
        selected_mail = Mail.objects.get(pk=mail_id)
        attachments = request.FILES.getlist('attachments[]')
        fw_re_form = FwReForm(request.POST, request.FILES, user_id=up.id)

        if fw_re_form.is_valid():
            content = fw_re_form.cleaned_data['content']
            title = fw_re_form.cleaned_data['title']
            receivers = fw_re_form.cleaned_data['receivers']
            cc = fw_re_form.cleaned_data['cc']
            bcc = fw_re_form.cleaned_data['bcc']

            if request.POST.get('re-fw', '') == 'forward':
                Mail.create(content=content, subject=title, sender=up, receivers=parse_address(receivers),
                            cc=parse_address(cc), bcc=parse_address(bcc), thread=thread,
                            titles=[cf.get('inbox-folder')],
                            attachments=attachments)

            elif request.POST.get('re-fw', '') == 'reply':
                Mail.reply(content=content, sender=up, in_reply_to=selected_mail, subject=title, thread=thread,
                           attachments=attachments)  # TODO: enable in middle reply

            fw_re_form = FwReForm(user_id=up.id)  # clearing sent mail details
    else:
        fw_re_form = FwReForm(user_id=up.id)

    labels = thread.get_user_labels(up)
    #TODO: MOVE TO METHOD
    allMails = thread.mails.all().select_related().order_by('created_at')

    tobeShown = {}

    #TODO: JOIN!
    for mail in allMails:
        if mail.sender_id == up.id:
            tobeShown[mail] = mail.get_user_labels(up)
        elif up.id in [user.id for user in mail.recipients.all()]:
            tobeShown[mail] = mail.get_user_labels(up)
            #TODO: above loop can be replace by thread.get_user_mails() please check if else is required!!
        else:
            pass # mail is not related to user

    if not tobeShown:
        return HttpResponseRedirect(reverse('mail/home'))

    env = {'reply': True, 'request': request, 'header': '', 'mails': allMails}
    ReadMail.mark_mails(request.user, tobeShown)
    unread = ReadMail.mark_as_read(request.user, tobeShown)

    #END OF MOVE
    DecoratorManager.get().activate_hook('show_thread', allMails[0], env)

    if not unread:
        try:
            thread.mark_as_read(up)
        except:
            pass

    return render_to_response('mail/showThread.html', {
        'user': request.user,
        'up': up,
        'thread': thread,
        'label': label,
        'labels': labels,
        'mails': tobeShown,
        'fw_re_form': fw_re_form,
        'referrer': referrer,
        'env': env,
        'last_index': len(tobeShown),
    }, context_instance=RequestContext(request))


def showLabel(request, label, archive_mode):
    up = request.user

    tls = Thread.objects.filter(labels=label).order_by('-pk').select_related()
    threads = tls if archive_mode else tls.filter(labels=UserManager.get(up).get_unread_label())
    threads = threads[:50]  # TODO: how to view all mails?
    threads = [t for t in threads if t.is_thread_related(up)]

    env = {'headers': []}
    DecoratorManager.get().activate_hook('show_label', label, threads, up, env)

    return render_to_response('mail/label.html',
                              {'threads': threads, 'label': label, 'label_title': label.title, 'user': request.user,
                               'env': env,
                               'archive': archive_mode,
                              },
                              context_instance=RequestContext(request))


@ajax_view
def mail_validate(request):
    rl = []
    rl.append(request.POST.get('receivers', ''))
    rl.append(request.POST.get('cc', ''))
    rl.append(request.POST.get('bcc', ''))
    for r in rl:
        if r:
            for c in r.split(','):
                if not Mail.validate_receiver(c):
                    return {"error": "گیرنده نامعتبر است."}
    return 'Ok'


@login_required
def createLabel(request):
    title = request.POST.get('title')
    label = Label()
    label.user = request.user
    label.title = title
    label.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@ajax_view
def add_label(request):
    item_list = []
    label_id = int(request.POST['label_id'])
    item_type = request.POST['item_type']
    if request.POST.get('item_id', ''):
        item_list.append(request.POST['item_id'])
    else:
        item_list = request.POST.getlist('item_id[]')

    if label_id >= 0:
        # existing label
        label = Label.objects.get(id=label_id)
    else:
        label_name = request.POST['label_name']
        label_name = label_name.split(u'(برچسب جدید)')[0]
        label = Label.create(user=request.user, title=label_name.strip())
    label_url = "/mail/view/%s/" % label.slug

    if item_type == "mail":
        for mail_id in item_list:
            mail = Mail.objects.get(id=mail_id)
            mail.add_label(label)
        response_text = "success"

    elif item_type == "thread":
        for thread_id in item_list:
            thread = Thread.objects.get(id=int(thread_id))
            thread.add_label(label)
        response_text = "success"

    else:
        response_text = "error"

    return {"response_text": response_text, "label_url": label_url, "label_id": label.id}


def label_list(request):
    start = request.GET.get('name_startsWith')
    labels = Label.objects.filter(user=request.user, title__startswith=start)
    if request.GET.get('current_label', ''):
        labels.exclude(id=int(request.GET.get('current_label')))

    jsonText = '['
    new_label_text = u'(برچسب جدید)'
    for label in labels:
        if not label.is_deleted_label():
            jsonText += '{"value":"' + str(label.id) + '" , "label":"' + label.title + '"},'
    if not UserManager.get(request.user).get_label(start.strip()):
        jsonText += '{"value":"' + '-1' + '" , "label":"' + start + ' ' + new_label_text + ' "},'
    jsonText = jsonText[:-1] + ']'

    return HttpResponse(jsonText)


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
                if current_label and not mail.thread.has_label(current_label):
                    c["referrer"] = reverse('mail/home')

        elif item_type == "thread":
            if request.POST.get('item_id', ''):
                thread = Thread.objects.get(id=int(request.POST['item_id']))
                thread.remove_label(label)
                c["response_text"] = "success"
                if current_label and not thread.has_label(current_label):
                    c["referrer"] = reverse('mail/home')
    except:
        pass

    return HttpResponse(simplejson.dumps(c))


@ajax_view
def move_thread(request):
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

    if request.POST.get('current_label', ''):
        current_label = Label.objects.get(id=int(request.POST.get('current_label')))

    thread_list = request.POST.getlist('item_id[]')
    for thread_id in thread_list:
        try:
            thread = Thread.objects.get(id=int(thread_id))
        except (ValueError, Thread.DoesNotExist):
            raise Http404('Invalid thread id')
        if label.is_deleted_label():
            for lbl in thread.labels.all():
                if lbl.title != Label.UNREAD_LABEL_NAME:
                    thread.remove_label(lbl)
        else:
            thread.remove_label(current_label)  # todo: fix this
        thread.add_label(label)

    return {"response_text": "success", }


def search_dic(token):
    return {
        u'از': Q(mails__sender__username__contains=token[1]) | Q(mails__sender__first_name__contains=token[1]) | Q(
            mails__sender__last_name__contains=token[1]),
        u'به': Q(mails__recipients__username__contains=token[1]) | Q(
            mails__recipients__first_name__contains=token[1]) | Q(
            mails__recipients__last_name__contains=token[1]),
        u'عنوان': Q(mails__title__contains=token[1]),
        u'محتوا': Q(mails__content__contains=token[1]),
        u'برچسب': search_labels(token[1])
    }.get(token[0], 1)


def search_labels(keyword):
    label_list = keyword.split(u'،')
    search_query = Q()
    for label in label_list:
        search_query = search_query | Q(labels__title__contains=label)
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
            tuple_keywords = token.split(':')
            if not search_query:
                search_query = search_dic(tuple_keywords)
            else:
                search_query = search_query & search_dic(tuple_keywords)

        answer = Thread.get_user_threads(up).filter(search_query).distinct()
        return render_to_response('mail/label.html', {
            'threads': answer,
            'label_title': 'نتایج جستجو',
        }, context_instance=RequestContext(request))


def parse_address(input):
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


@login_required
def ajax_mark_thread(request):
    thread_list = []
    if 'item_id[]' in request.POST:
        thread_list = request.POST.getlist('item_id[]')
    action = request.POST.get('action', '')
    response_text = "success"
    if action == 'read':
        for thread_id in thread_list:
            thread = Thread.objects.get(id=int(thread_id))
            thread.mark_as_read(request.user)
    elif action == 'unread':
        for thread_id in thread_list:
            thread = Thread.objects.get(id=int(thread_id))
            thread.mark_as_unread(request.user)
    else:
        response_text = "error"

    return HttpResponse(simplejson.dumps({'response_text': response_text, }))


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
    replies = []
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
            if ab.has_contact_address(contact_user.username+'@'+MailProvider.get_default_domain()) or contact_user == user:
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