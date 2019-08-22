from ..models import *
from ..forms import *
from django.shortcuts import render,redirect
from django.views.generic import (CreateView, UpdateView,
 ListView, UpdateView,DetailView,DeleteView)
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse,reverse_lazy
from django.contrib.auth import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout

class UserRegistration(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user
        return HttpResponseRedirect(self.get_success_url())

class UserUpdateView(LoginRequiredMixin,UpdateView):
    model = User
    fields=['email', "screenname","gender",'date_of_birth']
    template_name = 'account/update_user.html'
    success_url = reverse_lazy('user_information')
    def get_object(self, queryset=None):
        return self.request.user

@login_required
def user(request):
    object=get_object_or_404(User,pk=request.user.pk)
    return render(request,"account/details_user.html",locals())

@login_required
def follow(request):
    if request.method=="POST":
        form=FollowForm(request.POST)
        if form.is_valid():
            profile=request.user.get_profile()
            target=form.cleaned_data["profile"]
            if target.pk==profile.pk:
                return redirect("myprofile_details")
            profile.add_follow(target.pk)
            return redirect("profile_details",pk=target.pk)
        return redirect("myprofile_details")
    #profile.add_follow(pk)
    form=FollowForm()
    return render(request,"account/follow.html",locals())

@login_required
def cancel_follow(request):
    profile=request.user.get_profile()
    if request.method=="POST":
        form=FollowForm(request.POST)
        form.fields["profile"].queryset=profile.follow.all()
        if form.is_valid():
            target=form.cleaned_data["profile"]
            if target.pk==profile.pk:
                return redirect("myprofile_details")
            profile.cancel_follow(target.pk)
            return redirect("profile_details",pk=target.pk)
        return redirect("myprofile_details")
    #profile.add_follow(pk)
    form=FollowForm()
    form.fields["profile"].queryset=profile.follow.all()
    return render(request,"account/cancel_follow.html",locals())

@login_required
def withdrawal(request):
    if request.method=="POST":
        form=WithdrawalForm(request.POST)
        if form.is_valid() and form.cleaned_data["confirm"]==True:
            user=request.user
            epitaph=Epitaph.create(user)
            epitaph.write()
            epitaph.kill()
            return redirect("index")
    form=WithdrawalForm()
    return render(request,"account/withdrawal.html",locals())

class ProfileCreateView(LoginRequiredMixin,CreateView):
    model=Profile
    template_name = 'account/create_profile.html'
    form_class=ProfileForm
    success_url=reverse_lazy("myprofile_details")
    def get(self, request, *args, **kwargs):
        if request.user.has_profile():
            return HttpResponseRedirect(self.success_url)
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_active=True
        return super(ProfileCreateView, self).form_valid(form)

class ProfileDetailView(DetailView):
    template_name = 'account/details_profile.html'
    model=Profile
    queryset = Profile.objects.filter(is_active=True)
    def get_object(self, queryset=None):
        if "pk" in self.kwargs:
            return get_object_or_404(Profile,pk=self.kwargs['pk'])
        return self.request.user.get_profile()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            target=self.request.user.get_profile()
            context['following'] = target.is_following(self.object)
        return context

class MyProfileDetailView(DetailView):
    template_name = 'account/details_myprofile.html'
    model=Profile
    queryset = Profile.objects.filter(is_active=True)
    def get_object(self, queryset=None):
        return self.request.user.get_profile()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"]="my"
        if self.request.user.is_authenticated:
            target=self.request.user.get_profile()
            context['following'] = target.is_following(self.object)
        return context

class ProfileListView(LoginRequiredMixin,ListView):
    template_name = 'account/list_profile.html'
    paginate_by=10

    def get_queryset(self):
        queryset=Profile.objects.filter(is_active=True)
        return queryset

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'account/update_profile.html'
    model=Profile
    fields=("screenname","gender",'date_of_birth',"description","avatar","mail_magazine","is_public")
    #form_class=ProfileForm
    #success_url = reverse_lazy('userprofile_update', kwargs={'pk': self.pk})

    def get_object(self, queryset=None):
        return self.request.user.get_profile()

    # def get_queryset(self):
    #     queryset=Profile.objects.filter(user=self.request.user)
    #     return queryset

    def get_success_url(self):
        return reverse('myprofile_details')

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     return super(ProfileUpdateView, self).form_valid(form)

class ProfileDeleteView(LoginRequiredMixin,DeleteView):
    template_name = 'account/delete_profile.html'
    success_url="index"
    def get_success_url(self):
        return reverse(self.success_url)

    def get_queryset(self):
        if(not (self.request.user.is_staff)):
            queryset=Profile.objects.filter(user=self.request.user)
            return queryset
        queryset=Profile.objects.all()
        return queryset

    def dispatch(self, *args, **kwargs):
        # Custom user permission check
        self.object=self.get_object()
        if self.request.user.is_authenticated and \
         self.object.author!=self.request.user.get_profile():
                return HttpResponseForbidden()
        return super(ProfileDeleteView, self).dispatch(*args, **kwargs)

class MyFollowListView(LoginRequiredMixin,ListView):
    template_name = 'account/list_follow.html'
    paginate_by=10

    def get_queryset(self):
        profile=self.request.user.get_profile()
        queryset=profile.follow.all()
        #queryset=Profile.objects.all()
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"]="my"
        profile=self.request.user.get_profile()
        context["profile"]=profile
        return context

class FollowListView(LoginRequiredMixin,ListView):
    template_name = 'account/list_follow.html'
    paginate_by=10

    def get_queryset(self,**kwargs):
        profile=get_object_or_404(Profile,pk=self.kwargs.get("pk"))
        queryset=profile.follow.all()
        #queryset=Profile.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"]="user"
        profile=get_object_or_404(Profile,pk=self.kwargs.get("pk"))
        context["profile"]=profile
        return context

class MyFollowerListView(LoginRequiredMixin,ListView):
    template_name = 'account/list_follow.html'
    paginate_by=10

    def get_queryset(self):
        profile=self.request.user.get_profile()
        queryset=profile.get_followers()
        #queryset=Profile.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"]="my"
        profile=self.request.user.get_profile()
        context["profile"]=profile
        return context

class FollowerListView(LoginRequiredMixin,ListView):
    template_name = 'account/list_follow.html'
    paginate_by=10

    def get_queryset(self):
        profile=get_object_or_404(Profile,pk=self.kwargs.get("pk"))
        queryset=profile.get_followers()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"]="user"
        profile=get_object_or_404(Profile,pk=self.kwargs.get("pk"))
        context["profile"]=profile
        return context
