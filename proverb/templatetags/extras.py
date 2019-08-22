from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def dict_to_param(data):
    s=""
    keys=sorted(data)
    start=""
    for key in keys:
        if not data[key]=="":
            if start=="":
                start=key
            else:
                s+="&"
            s+=key+"="+data[key]
    return s

#https://docs.djangoproject.com/en/2.2/howto/custom-template-tags/
@register.simple_tag(takes_context=True)
def request_get(context):
    # request = context['request']
    try:
        request = context['request']
        if request.user.is_authenticated():
            user_authenticated = True
        else:
            user_authenticated = False
            return user_authenticated
    except:
        return 'None'
    return False
