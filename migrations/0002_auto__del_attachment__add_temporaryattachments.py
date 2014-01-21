# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Attachment'
        db.delete_table(u'user_mail_attachment')

        # Adding model 'TemporaryAttachments'
        db.create_table(u'user_mail_temporaryattachments', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('mail_uid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'user_mail', ['TemporaryAttachments'])

        # Adding M2M table for field attachments on 'Mail'
        m2m_table_name = db.shorten_name(u'user_mail_mail_attachments')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mail', models.ForeignKey(orm[u'user_mail.mail'], null=False)),
            ('storedfilemodel', models.ForeignKey(orm[u'storage.storedfilemodel'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mail_id', 'storedfilemodel_id'])


    def backwards(self, orm):
        # Adding model 'Attachment'
        db.create_table(u'user_mail_attachment', (
            ('mail', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.Mail'])),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('user_mail', ['Attachment'])

        # Deleting model 'TemporaryAttachments'
        db.delete_table(u'user_mail_temporaryattachments')

        # Removing M2M table for field attachments on 'Mail'
        db.delete_table(db.shorten_name(u'user_mail_mail_attachments'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'storage.storedfilemodel': {
            'Meta': {'object_name': 'StoredFileModel'},
            'disk_filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'real_filename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'user_mail.addressbook': {
            'Meta': {'object_name': 'AddressBook'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'user_mail.contact': {
            'Meta': {'object_name': 'Contact'},
            'additional_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'address_book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_mail.AddressBook']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        u'user_mail.databasemailaccount': {
            'Meta': {'object_name': 'DatabaseMailAccount', '_ormbases': [u'user_mail.MailAccount']},
            u'mailaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['user_mail.MailAccount']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'user_mail.imapmailaccount': {
            'Meta': {'object_name': 'ImapMailAccount', '_ormbases': [u'user_mail.MailAccount']},
            u'mailaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['user_mail.MailAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'selected_imap_settings': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_mail.ProviderImapSettings']"})
        },
        u'user_mail.label': {
            'Meta': {'object_name': 'Label'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': u"orm['user_mail.MailAccount']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': u"orm['auth.User']"})
        },
        u'user_mail.mail': {
            'Meta': {'object_name': 'Mail'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['storage.StoredFileModel']", 'symmetrical': 'False', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['user_mail.MailReceiver']", 'symmetrical': 'False'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender'", 'to': u"orm['auth.User']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mails'", 'to': u"orm['user_mail.Thread']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'user_mail.mailaccount': {
            'Meta': {'object_name': 'MailAccount'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mail_accounts'", 'to': u"orm['user_mail.MailProvider']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mail_accounts'", 'to': u"orm['auth.User']"})
        },
        u'user_mail.maildomain': {
            'Meta': {'object_name': 'MailDomain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'user_mail.mailprovider': {
            'Meta': {'object_name': 'MailProvider'},
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['user_mail.MailDomain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'user_mail.mailreceiver': {
            'Meta': {'object_name': 'MailReceiver'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_mail.Mail']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'user_mail.mailreply': {
            'Meta': {'object_name': 'MailReply'},
            'first': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['user_mail.Mail']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['user_mail.Mail']"})
        },
        u'user_mail.providerimapsettings': {
            'Meta': {'object_name': 'ProviderImapSettings'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imap_authentication': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'imap_port': ('django.db.models.fields.IntegerField', [], {}),
            'imap_security': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'imap_server': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['user_mail.MailProvider']"})
        },
        u'user_mail.readmail': {
            'Meta': {'object_name': 'ReadMail'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_mail.Mail']"}),
            'reader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'user_mail.temporaryattachments': {
            'Meta': {'object_name': 'TemporaryAttachments'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_uid': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'user_mail.thread': {
            'Meta': {'object_name': 'Thread'},
            'firstMail': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'headThread'", 'null': 'True', 'to': u"orm['user_mail.Mail']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'threads'", 'symmetrical': 'False', 'through': u"orm['user_mail.ThreadLabel']", 'to': u"orm['user_mail.Label']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'user_mail.threadlabel': {
            'Meta': {'object_name': 'ThreadLabel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_mail.Label']"}),
            'mails': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['user_mail.Mail']", 'null': 'True', 'blank': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_mail.Thread']"})
        }
    }

    complete_apps = ['user_mail']