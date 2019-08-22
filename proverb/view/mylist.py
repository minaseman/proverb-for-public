from ..models import *
from ..forms import *
from django.shortcuts import render,redirect
from django.views.generic import (CreateView, UpdateView,
 ListView, UpdateView,DetailView,DeleteView)
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse,reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.db.models import Q
from proverb.utils import *
from django.utils.decorators import method_decorator

class MylistDetailView(DetailView):
    template_name = 'mylist/details.html'
    model=Mylist
    # def get_queryset(self, **kwargs):
    #     #queryset=Mylist.objects.filter(Q(author=self.request.user.get_profile())|Q(is_public=True,is_active=True))
    #     queryset=Mylist.objects.filter(Q(author=self.request.user.get_profile())|Q(is_public=True,is_active=True))
    #     return queryset

    def get_context_data(self, **kwargs):
        object=self.object
        context = super().get_context_data(**kwargs)
        context["mode"]="user"
        if self.request.user.is_authenticated:
            form=DeleteMylistArticleForm(mylist=object)
            form.fields["manipulation"].initial="Delete Article"
            context['form'] =form
            if self.request.user.get_profile()==object.author:
                context["mode"]="my"

            #context["mylist"]=profile.get_mylists()

        #context["page_obj"] = paginate_query(self.request, self.get_queryset(), 10)

        queryset=object.articles.all()
        context["page_obj"] = paginate_query(self.request, queryset, 10)

        #profile=self.request.user.get_profile()
        profile=object.author
        context["profile"]=profile


        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object=get_object_or_404(Mylist,pk=self.kwargs.get("pk"))
        form=ManipulationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["manipulation"]=="Delete Article":
                delete_form=DeleteMylistArticleForm(request.POST,mylist=self.object)
                if delete_form.is_valid():
                    memory=delete_form.cleaned_data["article"]
                    memory.delete()
        return HttpResponseRedirect(reverse_lazy("mylist_details",kwargs={"pk":self.object.pk}))

class MylistCreateView(LoginRequiredMixin,CreateView):
    model=Mylist
    template_name = 'mylist/create.html'
    form_class=MylistForm
    success_url=reverse_lazy("my_mylist_list")

    def form_valid(self, form):
        form.instance.author = self.request.user.get_profile()
        return super(MylistCreateView, self).form_valid(form)

class MylistListView(ListView):
    template_name='mylist/list.html'
    paginate_by=10
    def get_queryset(self,**kwargs):
        queryset=Mylist.objects.filter(Q(author__pk=self.kwargs.get("pk"))|Q(is_public=True,is_active=True))
        #queryset=Mylist.objects.filter(is_public=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"]="user"
        profile=get_object_or_404(Profile,pk=self.kwargs.get("pk"))
        context["profile"]=profile
        return context

class MyMylistListView(ListView):
    template_name='mylist/list.html'
    paginate_by=10
    def get_queryset(self):
        queryset=Mylist.objects.filter(Q(author=self.request.user.get_profile())|Q(is_public=True,is_active=True))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"]="my"
        profile=self.request.user.get_profile()
        context["profile"]=profile
        return context

class MylistUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'mylist/update.html'
    success_url=reverse_lazy("my_mylist_list")
    form_class=MylistForm
    def get_queryset(self):
        queryset=Mylist.objects.filter(author=self.request.user.get_profile())
        return queryset

    def get_success_url(self):
        return reverse('mylist_details', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user.get_profile()
        return super(MylistUpdateView, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        # Custom user permission check
        self.object=self.get_object()
        if self.request.user.is_authenticated and \
         self.object.author!=self.request.user.get_profile():
                return HttpResponseForbidden()
        return super(MylistUpdateView, self).dispatch(*args, **kwargs)

class MylistDeleteView(LoginRequiredMixin,DeleteView):
    template_name="mylist/delete.html"
    success_url=reverse_lazy("my_mylist_list")
    def get_success_url(self):
        return reverse(self.success_url)

    def get_queryset(self):
        queryset=Mylist.objects.filter(author=self.request.user.get_profile())
        return queryset

    def dispatch(self, *args, **kwargs):
        # Custom user permission check
        self.object=self.get_object()
        if self.request.user.is_authenticated and \
         self.object.author!=self.request.user.get_profile():
                return HttpResponseForbidden()
        return super(MylistDeleteView, self).dispatch(*args, **kwargs)
