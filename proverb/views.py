from django.http import HttpResponse
# from django.views.generic import DetailView,ListView
# from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from django.core.urlresolvers import reverse_lazy,reverse
# from django.core import urlresolvers
from django.shortcuts import render
from proverb.models import *
from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from .forms import LoginForm
from .view.badge import check_all_badges

# from homepage.models import *
# from django.contrib.auth.decorators import permission_required
# from django.http import Http404
# from django import forms
# import re

# Create your views here.
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

def index(request,template_name="index.html"):
    if request.user.is_authenticated and request.user.has_profile():
        check_all_badges(request.user)
    new=Article.objects.filter(is_active=True,is_public=True).order_by("created_at")
    return render(request,template_name,locals())

def account_index(request,template_name="account.html"):
    return render(request,template_name,locals())

def account_create(request,template_name="account.html"):
    return render(request,template_name,locals())

class Login(LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    next_page="/accounts/"

class Logout(LoginRequiredMixin, LogoutView):
    template_name = 'login.html'
    next_page="/"
# class Form_connection(forms.Form):
#     username=forms.CharField(label="Login")
#     password=forms.CharField(label="Password",widget=forms.PasswordInput)
#     def clean(self):
#         cleaned_data=super(Form_connection,self).clean()
#         username=self.cleaned_data.get("username")
#         password=self.cleaned_data.get("password")
#         if not authenticate(username=username,password=password):
#             raise forms.ValidationError("ログイン名かパスワードが違います")
#         return self.cleaned_data
