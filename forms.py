# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper

from arsh.user_mail.models import Mail, AddressBook, Contact
from arsh.user_mail.widgets import MultiFileInput
from arsh.rich_form.layout.utils import LayoutUtils
from arsh.rich_form.validation import ValidationService


class ComposeForm(forms.ModelForm):
    # attachments = forms.FileField(label=u'فایل ضمیمه', widget=MultiuploaderField, required=False)
    attachments = forms.FileField(label=u'فایل ضمیمه', widget=MultiFileInput, required=False )
    # attachments = MultiuploaderField(label= u"فایل ضمیمه" ,required=False)

    labels = forms.CharField(label=u'برچسب های اولیه', required=False)

    class Meta:
        model = Mail
        exclude = ('sender', 'recipients', 'thread')

    def __init__(self, *args, **kwargs):
        super(ComposeForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs['style'] = 'width:60%'
        self.fields['labels'].widget.attrs['class'] = 'initial-labels'
        self.fields['labels'].widget.attrs['style'] = 'min-width:60%'

        #from tinymce.widgets import TinyMCE
        #self.fields['content'].widget = TinyMCE(attrs={'cols': 50, 'rows': 15, 'style': 'width:60%'})

        self.fields['receivers'] = forms.CharField(required=False, label=u"گیرنده")
        self.fields['receivers'].widget.attrs['class'] = 'info'
        self.fields['receivers'].widget.attrs['type'] = 'hidden'
        self.fields['receivers'].widget.attrs['style'] = 'min-width:60%'

        self.fields['cc'] = forms.CharField(required=False, label=u"رونوشت")
        self.fields['cc'].widget.attrs['class'] = 'info'
        self.fields['cc'].widget.attrs['type'] = 'hidden'
        self.fields['cc'].widget.attrs['style'] = 'min-width:60%'

        self.fields['bcc'] = forms.CharField(required=False, label=u"رونوشت مخفی")
        self.fields['bcc'].widget.attrs['class'] = 'info'
        self.fields['bcc'].widget.attrs['type'] = 'hidden'
        self.fields['bcc'].widget.attrs['style'] = 'min-width:60%'


        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'compose-form'
        self.helper.form_class = 'form margin-30'
        self.helper.layout = LayoutUtils(has_submit=True, has_reset=False,
                                         fields_order=['title', 'receivers', 'cc', 'bcc', 'labels', 'content',
                                                       'attachments']).generate_table_layout(self, 1)
        v = ValidationService(self, "#%s" % self.helper.form_id)
        v.validationalize_form()


class FwReForm(forms.ModelForm):
    attachments = forms.FileField(label=u'فایل ضمیمه', widget=MultiFileInput, required=False)

    class Meta:
        model = Mail
        exclude = ('thread', 'recipients', 'sender')
        # exclude = ('thread', 'sender')

    def __init__(self, *args, **kwargs):
        from tinymce.widgets import TinyMCE

        self.user_id = kwargs.pop('user_id', -1)
        qs = AddressBook.get_addressbook_for_user(get_object_or_404(User, pk=self.user_id)).get_all_contacts()

        super(FwReForm, self).__init__(*args, **kwargs)

        self.fields['content'].widget = TinyMCE(attrs={'cols': 50, 'rows': 15, 'style': 'width:70%'})

        self.fields['receivers'] = forms.CharField(required=False, label=u"گیرنده")
        self.fields['receivers'].widget.attrs['class'] = 'info'
        self.fields['receivers'].widget.attrs['type'] = 'hidden'
        self.fields['receivers'].widget.attrs['style'] = 'min-width:60%'

        self.fields['cc'] = forms.CharField(required=False, label=u"رونوشت")
        self.fields['cc'].widget.attrs['class'] = 'info'
        self.fields['cc'].widget.attrs['type'] = 'hidden'
        self.fields['cc'].widget.attrs['style'] = 'min-width:60%'

        self.fields['bcc'] = forms.CharField(required=False, label=u"رونوشت مخفی")
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



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = ('address_book')

        def __init__(self, *args, **kwargs):
            super(ContactForm, self).__init__(*args, **kwargs)
            self.field['display_name'].widget.attrs['class']= 'myeditable'
            self.field['display_name'].widget.attrs['data-url']= '/edit/addressbook'

            self.field['first_name'].widget.attrs['class']= 'myeditable'
            self.field['first_name'].widget.attrs['data-url']= '/edit/addressbook'

            self.field['last_name'].widget.attrs['class']= 'myeditable'
            self.field['last_name'].widget.attrs['data-url']= '/edit/addressbook'

            self.field['email'].widget.attrs['class']= 'myeditable'
            self.field['email'].widget.attrs['data-url']= '/edit/addressbook'

            self.field['email_additional'].widget.attrs['class']= 'myeditable'
            self.field['email_additional'].widget.attrs['data-url']= '/edit/addressbook'


