#coding=utf-8
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from rss.models import RSSItem, ClassItem, Subscription, News
import time

def render_addrss(request):
    return render_to_response('addrss.html')

def render_addclass(request):
    return render_to_response('addclass.html')


@csrf_exempt
def add_rss(request):
    url = request.POST.get('rss_url')
    if not url: return HttpResponse('RSS URL is empty.')
    new_rss = RSSItem(url=url, update_time=format_time(time.localtime(0)))
    new_rss.save()
    return HttpResponse('Add RSS URL successfully!')

@csrf_exempt
def add_class(request):
    class_title = request.POST.get('class')
    if not class_title: return HttpResponse('class is empty.')
    new_class = ClassItem(title=class_title)
    new_class.save()
    #return HttpResponse('Add class successfully!')
    return render_to_response('addclass.html')

def format_time(secs):
    return time.strftime('%Y-%m-%d %H:%M:%S', secs)

