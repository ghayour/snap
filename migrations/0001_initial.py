# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MailDomain'
        db.create_table('user_mail_maildomain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('user_mail', ['MailDomain'])

        # Adding model 'MailProvider'
        db.create_table('user_mail_mailprovider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('user_mail', ['MailProvider'])

        # Adding M2M table for field domains on 'MailProvider'
        m2m_table_name = db.shorten_name('user_mail_mailprovider_domains')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailprovider', models.ForeignKey(orm['user_mail.mailprovider'], null=False)),
            ('maildomain', models.ForeignKey(orm['user_mail.maildomain'], null=False))
        ))
        db.create_unique(m2m_table_name, ['mailprovider_id', 'maildomain_id'])

        # Adding model 'MailAccount'
        db.create_table('user_mail_mailaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mail_accounts', to=orm['auth.User'])),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mail_accounts', to=orm['user_mail.MailProvider'])),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('user_mail', ['MailAccount'])

        # Adding model 'ProviderImapSettings'
        db.create_table('user_mail_providerimapsettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['user_mail.MailProvider'])),
            ('imap_server', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('imap_port', self.gf('django.db.models.fields.IntegerField')()),
            ('imap_security', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('imap_authentication', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('user_mail', ['ProviderImapSettings'])

        # Adding model 'ImapMailAccount'
        db.create_table('user_mail_imapmailaccount', (
            ('mailaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user_mail.MailAccount'], unique=True, primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('selected_imap_settings', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.ProviderImapSettings'])),
        ))
        db.send_create_signal('user_mail', ['ImapMailAccount'])

        # Adding model 'DatabaseMailAccount'
        db.create_table('user_mail_databasemailaccount', (
            ('mailaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user_mail.MailAccount'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('user_mail', ['DatabaseMailAccount'])

        # Adding model 'Mail'
        db.create_table('user_mail_mail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sender', to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mails', to=orm['user_mail.Thread'])),
        ))
        db.send_create_signal('user_mail', ['Mail'])

        # Adding model 'Attachment'
        db.create_table('user_mail_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mail', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.Mail'])),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('user_mail', ['Attachment'])

        # Adding model 'MailReply'
        db.create_table('user_mail_mailreply', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['user_mail.Mail'])),
            ('reply', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['user_mail.Mail'])),
        ))
        db.send_create_signal('user_mail', ['MailReply'])

        # Adding model 'MailReceiver'
        db.create_table('user_mail_mailreceiver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mail', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.Mail'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal('user_mail', ['MailReceiver'])

        # Adding model 'Label'
        db.create_table('user_mail_label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', to=orm['user_mail.MailAccount'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('user_mail', ['Label'])

        # Adding model 'Thread'
        db.create_table('user_mail_thread', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('firstMail', self.gf('django.db.models.fields.related.ForeignKey')(related_name='headThread', null=True, to=orm['user_mail.Mail'])),
        ))
        db.send_create_signal('user_mail', ['Thread'])

        # Adding model 'ThreadLabel'
        db.create_table('user_mail_threadlabel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.Thread'])),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.Label'])),
        ))
        db.send_create_signal('user_mail', ['ThreadLabel'])

        # Adding M2M table for field mails on 'ThreadLabel'
        m2m_table_name = db.shorten_name('user_mail_threadlabel_mails')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('threadlabel', models.ForeignKey(orm['user_mail.threadlabel'], null=False)),
            ('mail', models.ForeignKey(orm['user_mail.mail'], null=False))
        ))
        db.create_unique(m2m_table_name, ['threadlabel_id', 'mail_id'])

        # Adding model 'AddressBook'
        db.create_table('user_mail_addressbook', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('user_mail', ['AddressBook'])

        # Adding model 'Contact'
        db.create_table('user_mail_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address_book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.AddressBook'])),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('additional_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal('user_mail', ['Contact'])

        # Adding model 'ReadMail'
        db.create_table('user_mail_readmail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mail', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_mail.Mail'])),
            ('reader', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('user_mail', ['ReadMail'])


    def backwards(self, orm):
        # Deleting model 'MailDomain'
        db.delete_table('user_mail_maildomain')

        # Deleting model 'MailProvider'
        db.delete_table('user_mail_mailprovider')

        # Removing M2M table for field domains on 'MailProvider'
        db.delete_table(db.shorten_name('user_mail_mailprovider_domains'))

        # Deleting model 'MailAccount'
        db.delete_table('user_mail_mailaccount')

        # Deleting model 'ProviderImapSettings'
        db.delete_table('user_mail_providerimapsettings')

        # Deleting model 'ImapMailAccount'
        db.delete_table('user_mail_imapmailaccount')

        # Deleting model 'DatabaseMailAccount'
        db.delete_table('user_mail_databasemailaccount')

        # Deleting model 'Mail'
        db.delete_table('user_mail_mail')

        # Deleting model 'Attachment'
        db.delete_table('user_mail_attachment')

        # Deleting model 'MailReply'
        db.delete_table('user_mail_mailreply')

        # Deleting model 'MailReceiver'
        db.delete_table('user_mail_mailreceiver')

        # Deleting model 'Label'
        db.delete_table('user_mail_label')

        # Deleting model 'Thread'
        db.delete_table('user_mail_thread')

        # Deleting model 'ThreadLabel'
        db.delete_table('user_mail_threadlabel')

        # Removing M2M table for field mails on 'ThreadLabel'
        db.delete_table(db.shorten_name('user_mail_threadlabel_mails'))

        # Deleting model 'AddressBook'
        db.delete_table('user_mail_addressbook')

        # Deleting model 'Contact'
        db.delete_table('user_mail_contact')

        # Deleting model 'ReadMail'
        db.delete_table('user_mail_readmail')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'user_mail.addressbook': {
            'Meta': {'object_name': 'AddressBook'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'user_mail.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_mail.Mail']"})
        },
        'user_mail.contact': {
            'Meta': {'object_name': 'Contact'},
            'additional_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'address_book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_mail.AddressBook']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        'user_mail.databasemailaccount': {
            'Meta': {'object_name': 'DatabaseMailAccount', '_ormbases': ['user_mail.MailAccount']},
            'mailaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user_mail.MailAccount']", 'unique': 'True', 'primary_key': 'True'})
        },
        'user_mail.imapmailaccount': {
            'Meta': {'object_name': 'ImapMailAccount', '_ormbases': ['user_mail.MailAccount']},
            'mailaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user_mail.MailAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'selected_imap_settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_mail.ProviderImapSettings']"})
        },
        'user_mail.label': {
            'Meta': {'object_name': 'Label'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['user_mail.MailAccount']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['auth.User']"})
        },
        'user_mail.mail': {
            'Meta': {'object_name': 'Mail'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['user_mail.MailReceiver']", 'symmetrical': 'False'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender'", 'to': "orm['auth.User']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mails'", 'to': "orm['user_mail.Thread']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'user_mail.mailaccount': {
            'Meta': {'object_name': 'MailAccount'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mail_accounts'", 'to': "orm['user_mail.MailProvider']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mail_accounts'", 'to': "orm['auth.User']"})
        },
        'user_mail.maildomain': {
            'Meta': {'object_name': 'MailDomain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'user_mail.mailprovider': {
            'Meta': {'object_name': 'MailProvider'},
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': "orm['user_mail.MailDomain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'user_mail.mailreceiver': {
            'Meta': {'object_name': 'MailReceiver'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_mail.Mail']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'user_mail.mailreply': {
            'Meta': {'object_name': 'MailReply'},
            'first': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['user_mail.Mail']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['user_mail.Mail']"})
        },
        'user_mail.providerimapsettings': {
            'Meta': {'object_name': 'ProviderImapSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imap_authentication': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'imap_port': ('django.db.models.fields.IntegerField', [], {}),
            'imap_security': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'imap_server': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['user_mail.MailProvider']"})
        },
        'user_mail.readmail': {
            'Meta': {'object_name': 'ReadMail'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_mail.Mail']"}),
            'reader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'user_mail.thread': {
            'Meta': {'object_name': 'Thread'},
            'firstMail': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'headThread'", 'null': 'True', 'to': "orm['user_mail.Mail']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'threads'", 'symmetrical': 'False', 'through': "orm['user_mail.ThreadLabel']", 'to': "orm['user_mail.Label']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'user_mail.threadlabel': {
            'Meta': {'object_name': 'ThreadLabel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_mail.Label']"}),
            'mails': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['user_mail.Mail']", 'null': 'True', 'blank': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_mail.Thread']"})
        }
    }

    complete_apps = ['user_mail']