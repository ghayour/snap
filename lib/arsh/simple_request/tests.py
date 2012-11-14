# -*- coding: utf-8 -*-

from rezgh.places.models import Shop
from django.contrib.auth.models import User
from MailRequest import SimpleMailRequest
from django.test import TestCase

class SimpleTest(TestCase):
    def test_simpleMailRequest(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        u  = User.objects.all()[0]
        s  = Shop.objects.create(registrar=u,name=u'پفک')
        smr = SimpleMailRequest(u, None, s, None)
        print smr.get_responders()
        self.assertEqual(1 + 2, 3)
