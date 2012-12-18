class AppTest(TestCase): 
	fixtures = ['auth']
	def setUp(self):
		self.client = Client()
		self.assertTrue(self.client.login(username='admin',password='admin'))

	def testmail__compose(self):
		#view function = <function compose at 0x10301f500>
		response = self.client.get('mail/compose')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__search(self):
		#view function = <function search at 0x10301f668>
		response = self.client.get('mail/search/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__home(self):
		#view function = <function see at 0x10301f398>
		response = self.client.get('mail/view/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__inbox_archive(self):
		#view function = <function see at 0x10301f398>
		response = self.client.get('mail/view/archive/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__see_label(self):
		#view function = <function see at 0x10301f398>
		response = self.client.get('mail/view/(?P<label_slug[a-zA-Z0-9_\.]+)/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__see_label_archive(self):
		#view function = <function see at 0x10301f398>
		response = self.client.get('mail/view/(?P<label_slug[a-zA-Z0-9_\.]+)/archive')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__see_thread(self):
		#view function = <function see at 0x10301f398>
		response = self.client.get('mail/view/(?P<label_slug[a-zA-Z0-9_\.]+)/(?P<thread_slug[a-zA-Z0-9_\.]+)/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__see_thread_direct(self):
		#view function = <function see at 0x10301f398>
		response = self.client.get('mail/threads/view/(?P<thread_slug[a-zA-Z0-9_\.]+)/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testmail__thread__mark(self):
		#view function = <function mark_thread at 0x10301f938>
		response = self.client.get('mail/threads/(?P<thread_slug[a-zA-Z0-9_\.]+)/mark_(?P<actionread|unread)')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')

	def testsetup(self):
		#view function = <function setup at 0x10301f230>
		response = self.client.get('mail/setup')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'')
