from django.conf import settings
import bleach
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, datetime
from django.utils import timezone

#from IPython.core.debugger import Pdb; Pdb().set_trace()

#please refer to https://mutter.monotalk.xyz/posts/0e3919de7bf1480964b475ec208bb31a
def get_json_model_field():
    is_defalut_database_sqlite3 = "django.db.backends.sqlite3" == settings.DATABASES.get("default").get("ENGINE")
    if is_defalut_database_sqlite3:
        from jsonfield import JSONField as JSONField
        return JSONField()
    else:
        from django.contrib.postgres.fields import JSONField
        return JSONField()

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_bleach_default_options():
    bleach_args = {}
    bleach_settings = {
        'BLEACH_ALLOWED_TAGS': 'tags',
        'BLEACH_ALLOWED_ATTRIBUTES': 'attributes',
        'BLEACH_ALLOWED_STYLES': 'styles',
        'BLEACH_STRIP_TAGS': 'strip',
        'BLEACH_STRIP_COMMENTS': 'strip_comments',
        'BLEACH_ALLOWED_PROTOCOLS': 'protocols'
    }

    for setting, kwarg in bleach_settings.items():
        if hasattr(settings, setting):
            bleach_args[kwarg] = getattr(settings, setting)
    return bleach_args

def bleach_value(value, tags=None):
    bleach_args = get_bleach_default_options()
    if tags is not None:
        args = bleach_args.copy()
        args['tags'] = tags.split(',')
    else:
        args = bleach_args
    bleached_value = bleach.clean(value, **args)
    return mark_safe(bleached_value)

def bleach_linkify(value):
    return bleach.linkify(value, parse_email=True)

def paginate_query(request, queryset, count):
  paginator = Paginator(queryset, count)
  page = request.GET.get('page')
  try:
    page_obj = paginator.page(page)
  except PageNotAnInteger:
    page_obj = paginator.page(1)
  except EmptyPage:
    page_obj = paginatot.page(paginator.num_pages)
  return page_obj

 # def author_required(view):
 #     def _wrapped_view(request, *args, **kwargs):
 #         if request.user.is_authenticated():
 #             request.
 #             return view(request, *args, **kwargs)
 #     return HttpResponseForbiden()
 #   return _wrapped_view
