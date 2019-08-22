from ..models import *
from ..forms import *
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404,render,redirect

#from IPython.core.debugger import Pdb; Pdb().set_trace()
def mybadgebox(request):
    profile=request.user.get_profile()
    all=Badge.objects.all()
    badges=list(profile.badges.values_list("name",flat=True))
    public=True
    mode="my"
    return render(request,"badge/details.html",locals())

def badgebox(request,pk):
    profile=get_object_or_404(Profile,pk=pk)
    all=Badge.objects.all()
    badges=list(profile.badges.values_list("name",flat=True))
    public=profile.is_public
    mode="user"
    return render(request,"badge/details.html",locals())


def check_all_badges(user):
    count_1article(user)
    count_10articles(user)
    passed_5days_from_registration(user)

######### methods of checking budge ##########
def count_1article(user):
    data={
        "name":"1article",
        "description":"You submitted 1 article",
        "datetime":datetime(2012, 1, 1, 12, 00,tzinfo=timezone.get_current_timezone()),
    }
    def filter(profile):
        num=Article.objects.filter(author=profile).count()
        return num>=1
    return check_badge("1article",filter,data,user)

def count_10articles(user):
    data={
        "name":"10articles",
        "description":"You submitted 10 articles",
        "datetime":datetime(2012, 1, 1, 12, 00,tzinfo=timezone.get_current_timezone())
    }
    def filter(profile):
        num=Article.objects.filter(author=profile).count()
        return num>=10
    return check_badge("10articles",filter,data,user)

def passed_5days_from_registration(user):
    data={
        "name":"5days",
        "description":"5days was passed from registration",
        "datetime":datetime(2012, 1, 1, 12, 00,tzinfo=timezone.get_current_timezone())
    }
    def filter(profile):
        delta=timezone.datetime.now(timezone.get_current_timezone())-profile.created_at
        return delta>timezone.timedelta(days=5)
    return check_badge("5days",filter,data,user)
###############################################

def check_badge(name,filter,badge_data,user):
    if user.has_profile():
        profile=user.get_profile()
        if filter(profile):
            badge,created=get_badge(badge_data)
            profile.badges.add(badge)
            return True
    return False

def get_badge(data):
    badge,created=Badge.objects.get_or_create(
        name=data["name"],
        description=data["description"],
        proposed_at=data["datetime"]
    )
    return badge,created
