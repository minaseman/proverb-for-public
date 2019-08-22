#https://docs.djangoproject.com/ja/2.2/topics/http/middleware/
from proverb import utils
from proverb.models import *
import json
from django.shortcuts import get_object_or_404
from datetime import date, datetime,timedelta
from django.utils import timezone

class LogggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self,request, view_func, view_args, view_kwargs):
        if view_func.__name__=="ArticleDetailView":
            self.logging_article(request, view_func, view_args, view_kwargs)
        self.logging(request, view_func, view_args, view_kwargs)
        # log.request_meta = json.dumps(data,default=utils.json_serial)

    def process_exception(self, request, exception):
        pass

    def logging(self,request, view_func, view_args, view_kwargs):
        log=Log()
        if request.user.is_authenticated:
            log.user=request.user
        #log.ip_address=request.META["REMOTE_ADDR"] or ""
        log.ip_address=utils.get_client_ip(request)
        log.path=request.path_info
        log.func_name=str(view_func.__name__)
        log.method=request.method
        log.save()

    def logging_article(self,request, view_func, view_args, view_kwargs):
        user=None
        if request.user.is_authenticated:
            user=request.user
        now=timezone.now()
        today=datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=now.tzinfo)
        tommorrow=today+timedelta(days=1)
        logs=Log.objects.filter(created_at__range=(today,tommorrow))
        logs=logs.filter(user=user,path=request.path_info,ip_address=utils.get_client_ip(request))
        article = get_object_or_404(Article, pk=view_kwargs["pk"])
        if logs.count()<=0:
            article.plus_one_views()

# def add_one_browsing_to_article(filter,pk):
#     if filter(profile):
#         obj = get_object_or_404(MyModel, pk=1)
#         return True
#     return False

class TestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    def process_view(self,request, view_func, view_args, view_kwargs):
        # if view_func.__name__.startswith('api'):
        #     return HttpResponseBadRequest()
        # else:
        #     return None
        #https://docs.djangoproject.com/ja/2.0/ref/request-response/
        print("request method : "+request.method)
        print("request path : "+request.path_info)
        print("request path META : "+str(request.META))
        # print("request META REMOTE_ADDR: "+str(request.META["REMOTE_ADDR"]))
        # print("request META REMOTE_HOST: "+str(request.META["REMOTE_HOST"]))
        # print("request META REMOTE_USER: "+str(request.META["REMOTE_USER"]))
        print("view_func : "+ str(view_func.__name__))
        print("view_args : "+str(view_args))
        print("view_kwargs : "+str(view_kwargs))
