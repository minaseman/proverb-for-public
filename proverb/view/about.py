from django.http import HttpResponse
from django.shortcuts import render

def us(request,template_name="about/us.html"):
    return render(request,template_name,locals())

def how_to_use(request,template_name="about/how_to_use.html"):
    return render(request,template_name,locals())

def what_is_proverb(request,template_name="about/what_is_proverb.html"):
    return render(request,template_name,locals())

def proverb(request,template_name="about/proverb.html"):
    return render(request,template_name,locals())

def privacy_policy(request,template_name="about/privacy_policy.html"):
    return render(request,template_name,locals())

def writing_policy(request,template_name="about/writing_policy.html"):
    return render(request,template_name,locals())

def copyright(request,template_name="about/copyright.html"):
    return render(request,template_name,locals())

def developped_by(request,template_name="about/developped_by.html"):
    return render(request,template_name,locals())
