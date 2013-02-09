# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
#from rezgh.accounts.AccountManager import AccountManager
#from arsh.simple_request.models import SimpleRequest




__docformat__ = 'reStructuredText'

FOOTER_SLUG = 'sdhf3akj22sf5hljhuh243u423yr87fdyshd8c'

def append_components_to_mail(self, content, components):
    """transform components dictionary to comma separated str and append end of mail
    :type content: str
    :type components: str
    :param content: original mail
    :param components: components that usually are button
    :type components: dict{'type':'' ,'url':'','label':''}
    :return: extended mail
    """
    form = u''
    for component in components:
        form += u'%s,%s,%s\n' % (component['type'], component['url'], component['label'])
    return content + FOOTER_SLUG + form



def get_html(sender, first_mail, env):
    """ create html codes of request form and add to env['ribbon']
    :param sender: sender
    :type sender: User
    :param env: environment
    :type env: dict
    :param first_mail: first mail of thread
    :type first_mail: Mail
    :rtype: changed env
    """
    request = None
    is_requester = first_mail.sender == env['request'].user
    is_responder = env['request'].user in first_mail.recipients.all()

    #breaking if this is not a request
    raw_content = first_mail.content
    index = raw_content.rfind(FOOTER_SLUG)
    if index == -1:
        env['ribbon'] = ''
        return env

    env['mark_as_read'] = False # درخواست‌ها باید به صورت صریح به صورت خوانده شده علامت زده شوند

    #breaking if there are no action buttons
    first_mail.content = raw_content[:index]
    raw_form = raw_content[index + len(FOOTER_SLUG):]
    if raw_form == '':
        env['ribbon'] = ''
        return env
    rows = raw_form.split("\n")

    form = u""
    for row in rows:
        row = row.strip()
        if not row: continue

        if row.startswith(':REQ:'):
            #FIXME: what if DoesNotExists?
            request = SimpleRequest.objects.get(id=row[5:])

        elements = row.split(',')
        action = str(elements[0]).strip()
        if action == "button":
            form += (
                u"""<button onclick='$.post("%s",{test:$("#accept_form_txt").val()},function(data) {})'>%s</button>""" % (
                    elements[1], elements[2]))
        #TODO: show accept/reject/... only for receiver
        elif action == "accept":
            if is_responder:
                form += u"""<img class="icon list-item" src="/static/images/icons/accept-128.png" width="48px" onclick="var val=$('#accept_form_txt').val();$.post('%s',{message:val},function(msg){reply('<b>درخواست شما تایید شد.</b><br/>'+val, mark_as_read, false);})" />""" % elements[1]
        elif action == "reject":
            if is_responder:
                form += u"""<img class="icon list-item" src="/static/images/icons/delete-128.png" width="48px" onclick="var val=$('#accept_form_txt').val();$.post('%s',{message:val},function(msg){reply('<b>درخواست شما رد شد.</b><br/>'+val, mark_as_read, false);})" />""" % elements[1]
        elif action == "talk":
            form += u"""<img class="icon list-item" src="/static/images/icons/comment-128.png" width="48px" id="talk_button" onclick="reply($('#accept_form_txt').val())" />"""
    if form:
        txt = u''
        if is_responder:
            txt = u"""<p class="fa" style="margin: 10px 0;">
        <b>این پیام حاوی یک درخواست است؛ لطفا آن را بررسی نمایید.</b><br/>
         پس از بررسی و احیانا وارد کردن توضیحات لازم در کادر زیر
        می‌توانید آن را تایید یا رد کنید یا که برای کسب اطلاعات بیش‌تر با درخواست‌دهنده گفتگو کنید.</p>"""
        if is_requester:
            txt = u"""<p class="fa" style="margin: 10px 0">
<b>این پیام نمایشگر وضعیت درخواست شماست.</b><br/>
 می‌توانید آخرین وضعیت درخواست را از اینجا ببینید یا با مسئول بررسی مکالمه نمایید.
            </p>"""
        txt += u"""<input id="accept_form_txt" type="text" name="content" style="width: 500px; margin-bottom: 10px;" /></br>"""
        form = txt + form

    #header buttons
    env['header'] = ''
    if is_requester:
        url = request.get_edit_url()
        if url:
            env['header'] += u'<button onclick="go(\'%s\')">ویرایش درخواست</button>' % url
    if is_responder:
        for action_title, url in request.get_inspect_urls():
            env['header'] += u'<a target="_blank" href="%s">%s</a>' % (url, action_title)
    if is_requester or not form: #اگر هیچ کاری نتواند بکند، باید بتواند درخواست را ببندد
        env['header'] += u'<button onclick="mark_as_read(true)">بستن درخواست</button>'
    env['header'] = mark_safe(env['header'])

    env['ribbon'] = mark_safe(u'<div class="Center" style="margin: 30px 0;">%s</div>' % form)

    env['reply'] = False
    env['request'] = request
    return env


def label_list(label, threads, user, env):
    env['headers'] = ['importance', 'status', 'open']
    for thread in threads:
        s = 'progress.png' if thread.is_unread() else ''
        try:
            txt = thread.firstMail.content
            key = FOOTER_SLUG+':REQ:'
            ind = txt.rfind(key)
            id = txt[ind+len(key):txt.find('\n', ind+1)]
            request = SimpleRequest.objects.get(id=id)
            o = request.get_status()
            if o is None:
                o = ''
            elif o:
                o = 'accept-128.png'
            else:
                o = 'delete-128.png'

            imp = 'important.png' if AccountManager.is_manager(request.requester) else ''
        except ValueError:
            o = ''
            imp = ''
        image_tag = '<div class="center"><img src="/static/images/icons/%s" alt="%s" width="24" /></div>'
        thread.rows = ['' if not image else mark_safe(image_tag % (image, image)) for image
                       in [imp, s, o]]


def get_mail_summary(env, mail):
    """
    :param mail:
    :type mail: Mail
    :return:
    """
    content = mail.content
    if FOOTER_SLUG in content:
        content = content[:content.rfind(FOOTER_SLUG)]
    env['content'] = content
