# -*- coding: utf-8 -*-
from tinymce.widgets import TinyMCE
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Submit, Hidden, Button

from user_mail.models import Mail, AddressBook
from user_mail.widgets import MultiFileInput
from arsh.rich_form.layout.utils import LayoutUtils
from arsh.rich_form.validation import ValidationService


class ComposeForm(forms.ModelForm):
    attachments = forms.FileField(label=u'فایل ضمیمه', widget=MultiFileInput, required=False)

    class Meta:
        model = Mail
        exclude = ('sender', 'recipients', 'thread')

    def __init__(self, *args, **kwargs):
        super(ComposeForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs['style'] = 'min-width:60%'

        self.fields['content'].widget = TinyMCE(attrs={'cols': 50, 'rows': 15, 'style': 'width:60%'})

        self.fields['receivers'] = forms.CharField(required=False)
        self.fields['receivers'].widget.attrs['class'] = 'info'
        self.fields['receivers'].widget.attrs['type'] = 'hidden'
        self.fields['receivers'].widget.attrs['style'] = 'min-width:60%'

        self.fields['cc'] = forms.CharField(required=False)
        self.fields['cc'].widget.attrs['class'] = 'info'
        self.fields['cc'].widget.attrs['type'] = 'hidden'
        self.fields['cc'].widget.attrs['style'] = 'min-width:60%'

        self.fields['bcc'] = forms.CharField(required=False)
        self.fields['bcc'].widget.attrs['class'] = 'info'
        self.fields['bcc'].widget.attrs['type'] = 'hidden'
        self.fields['bcc'].widget.attrs['style'] = 'min-width:60%'


        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'compose-form'
        self.helper.form_class = 'form margin-30'
        self.helper.layout = LayoutUtils(has_submit=True, has_reset=False,
                                         fields_order=['title', 'receivers', 'cc', 'bcc', 'content',
                                                       'attachments']).generate_table_layout(self, 1)
        v = ValidationService(self, "#%s" % self.helper.form_id)
        v.validationalize_form()


class FwReForm(forms.ModelForm):
    attachments = forms.FileField(label=u'فایل ضمیمه', widget=MultiFileInput, required=False)

    class Meta:
        model = Mail
        exclude = ('thread', 'recipients', 'sender')

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', -1)
        qs = AddressBook.get_addressbook_for_user(get_object_or_404(User, pk=self.user_id)).get_all_contacts()

        super(FwReForm, self).__init__(*args, **kwargs)

        self.fields['content'].widget = TinyMCE(attrs={'cols': 50, 'rows': 15, 'style': 'width:70%'})

        self.fields['receivers'] = forms.CharField(required=False)
        self.fields['receivers'].widget.attrs['class'] = 'info'
        self.fields['receivers'].widget.attrs['type'] = 'hidden'
        self.fields['receivers'].widget.attrs['style'] = 'min-width:60%'

        self.fields['cc'] = forms.CharField(required=False)
        self.fields['cc'].widget.attrs['class'] = 'info'
        self.fields['cc'].widget.attrs['type'] = 'hidden'
        self.fields['cc'].widget.attrs['style'] = 'min-width:60%'

        self.fields['bcc'] = forms.CharField(required=False)
        self.fields['bcc'].widget.attrs['class'] = 'info'
        self.fields['bcc'].widget.attrs['type'] = 'hidden'
        self.fields['bcc'].widget.attrs['style'] = 'min-width:60%'


        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'fw-re-form'
        self.helper.form_class = 'form margin-30'
        self.helper.layout = LayoutUtils(has_submit=True, has_reset=False,
                                         fields_order=['title', 'receivers', 'cc', 'bcc', 'content',
                                                       'attachments']).generate_table_layout(self, 1)
        v = ValidationService(self, "#%s" % self.helper.form_id)
        v.validationalize_form()

