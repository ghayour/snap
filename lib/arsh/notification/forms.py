from django.forms.models            import ModelForm
from arsh.cms.update_tinyMCE        import UpdateTinyMCE
from arsh.notification.models import Notification

class NotificationForm(ModelForm):
    class Meta:
        model = Notification
        exclude = ['user',]
        widgets = {
            'description':UpdateTinyMCE(attrs={'cols': 75, 'rows': 25})
        }