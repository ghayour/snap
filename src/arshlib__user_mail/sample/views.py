# -*- coding: utf-8 -*-
from django.http                           import HttpResponse




def sample1(request):
    return HttpResponse('OK')
