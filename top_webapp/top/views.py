# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from models import entry, exclusion, author
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic.list_detail import object_list

''' = entry.objects.all().order_by("-rating")
    if request.openid:
        exclude_authors = exclusion.objects.filter(what=0, openid__exact=str(request.openid))
        exclude_links = exclusion.objects.filter(what=1, openid__exact=str(request.openid))
        exclude_authors = [ex.txt for ex in exclude_authors]
        exclude_links = [ex.txt for ex in exclude_links]
        entries = entries.exclude(author__in=exclude_authors)
        entries = entries.exclude(link__in=exclude_links)
    entries = entries[:50]'''




def index(request):
    if request.openid:
        entries = entry.objects.filtered(openid=str(request.openid))
    else:
        entries = entry.objects.filtered()
    return render_to_response("index.html", {'entries':entries, 'openid':request.openid})

def nofilters(request):
    entries = entry.objects.filtered()
    return render_to_response("index.html", {'entries':entries, 'openid':request.openid, 'nofilters':True})

def exclude_author(request):
    ex = exclusion()
    ex.what=0
    ex.txt=str(request.POST["author"])
    ex.openid=str(request.openid)
    ex.save()
    return HttpResponse("ok")

def return_author(request):
    ex = exclusion.objects.filter(what=0, openid__exact=str(request.openid), txt__exact=(str(request.POST["author"])))[0]
    ex.delete()
    return HttpResponse("ok")

def exclude_post(request):
    ex = exclusion()
    ex.what=1
    ex.txt=str(request.POST["link"])
    ex.openid=str(request.openid)
    ex.save()
    return HttpResponse("ok")

def return_post(request):
    ex = exclusion.objects.filter(what=1, openid__exact=str(request.openid), txt__exact=(str(request.POST["link"])))[0]
    ex.delete()
    return HttpResponse("ok")

def settings(request):
    if request.openid:
        ex_author = author.objects.excluded(str(request.openid))
        entries = entry.objects.excluded(str(request.openid))
        return render_to_response("exclusion_list.html", {'ex_author': ex_author,
                                                          'entries': entries,
                                                          'openid': request.openid,})
    else:
        return HttpResponseRedirect('/')
