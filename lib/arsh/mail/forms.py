# -*- coding: utf-8 -*-
from django                                import forms

from tinymce.widgets                       import TinyMCE

from arsh.mail.models                      import Mail



class ComposeForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))



    class Meta:
        model = Mail
        exclude = ('sender', 'recipients', 'thread')



class ReplyForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 100, 'rows': 30}), label='')



    class Meta:
        model = Mail
        exclude = ('sender', 'title', 'recipients', 'thread')
