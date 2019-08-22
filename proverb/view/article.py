from ..models import *
from ..forms import *
from django.views.generic import (CreateView, UpdateView,
 ListView, UpdateView,DetailView,DeleteView)
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse,reverse_lazy
#from django.contrib.auth import forms
from django.shortcuts import get_object_or_404,render,redirect
import operator
from django.db.models import Q
from functools import reduce
from django.http import (
    HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound,
    HttpResponseServerError,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ArticleCreateView(LoginRequiredMixin,CreateView):
    model=Article
    template_name = 'article/create.html'
    form_class=ArticleForm
    success_url=reverse_lazy("article_list")

    def form_valid(self, form):
        form.instance.author = self.request.user.get_profile()
        return super(ArticleCreateView, self).form_valid(form)

class ArticleDetailView(DetailView):
    template_name = 'article/details.html'
    model=Article
    queryset = Article.objects.filter(is_active=True,is_public=True)
    success_url=reverse_lazy("article_details")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            form=AddMylistForm(user=self.request.user,article=self.object)
            form.fields["manipulation"].initial="Add Mylist"
            context['form'] =form
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object=get_object_or_404(Article,pk=self.kwargs.get('pk'))
        #forms=ArticleDetailForm(request.POST,user=self.request.user,article=self.object)
        profile=self.request.user.get_profile()
        form=ManipulationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["manipulation"]=="Add Mylist":
                add_form=AddMylistForm(request.POST,user=self.request.user,article=self.object)
                if add_form.is_valid():
                    mylist=add_form.cleaned_data["mylist"]
                    article=add_form.cleaned_data["article"]
                    mylist.add_article(article)
        return HttpResponseRedirect(reverse_lazy("article_details",kwargs={"pk":self.object.pk}))
        # if form.is_valid():
        #     return self.form_valid(form)
        # else:
        #     return self.form_invalid(form)

class ArticleListView(ListView):
    template_name='article/list.html'
    paginate_by=1

    def post(self, request, *args, **kwargs):
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method=="POST":
            search_form=ArticleSearchForm(self.request.POST)
        else:
            search_form=ArticleSearchForm(self.request.GET)
        if search_form.is_valid():
            urlparams=search_form.cleaned_data
        context["urlparams"]=urlparams
        search_form=ArticleSearchForm(initial=urlparams)
        context['search_form'] = search_form
        params = {k: v for k, v in urlparams.items() if v != ''}
        context["searched"]=params!={}
        return context

    def get_queryset(self):
        if self.request.method=="POST":
            search_form=ArticleSearchForm(self.request.POST)
        else:
            search_form=ArticleSearchForm(self.request.GET)
        if search_form.is_valid():
            data={}
            for key,value in search_form.cleaned_data.items():
                if not value=="":
                    data[key]=value.split(" ")
            query=Q()
            if "title" in data:
                q = reduce(operator.and_, (Q(title__contains = item) for item in data["title"]))
                query=reduce(operator.and_,[query,q])
            if "description" in data:
                q = reduce(operator.and_, (Q(description__contains = item) for item in data["description"]))
                query=reduce(operator.and_,[query,q])
            if "author" in data:
                q = reduce(operator.and_, (Q(author__screenname__contains = item) for item in data["author"]))
                query=reduce(operator.and_,[query,q])
            if "hashTags" in data:
                q = reduce(operator.and_, (Q(hashTags__name = "#"+item) for item in data["hashTags"]))
                query=reduce(operator.and_,[query,q])
            query=reduce(operator.and_,[query,Q(is_active=True)])
            queryset=Article.objects.filter(query)
        else:
            queryset=Article.objects.filter(is_active=True,is_public=True)
        return queryset

class ArticleUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'article/update.html'
    form_class=ArticleForm
    #success_url = reverse_lazy('article_update', kwargs={'pk': self.pk})

    def get_queryset(self):
        queryset=Article.objects.filter(author=self.request.user.get_profile())
        return queryset

    def get_success_url(self):
        return reverse('article_details', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user.get_profile()
        return super(ArticleUpdateView, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        # Custom user permission check
        self.object=self.get_object()
        if self.request.user.is_authenticated and \
         self.object.author!=self.request.user.get_profile():
                return HttpResponseForbiden()
        return super(ArticleUpdateView, self).dispatch(*args, **kwargs)

class ArticleDeleteView(LoginRequiredMixin,DeleteView):
    template_name="article/delete.html"
    success_url="index"
    def get_success_url(self):
        return reverse(self.success_url)

    def get_queryset(self):
        if(not (self.request.user.is_staff)):
            queryset=Article.objects.filter(author=self.request.user.get_profile())
            return queryset
        queryset=Article.objects.all()
        return queryset

    def dispatch(self, *args, **kwargs):
        # Custom user permission check
        self.object=self.get_object()
        if self.request.user.is_authenticated and \
         self.object.author!=self.request.user.get_profile():
                return HttpResponseForbidden()
        return super(ArticleDeleteView, self).dispatch(*args, **kwargs)

class ReviewCreateView(LoginRequiredMixin,CreateView):
    model=Review
    template_name = 'review/create.html'
    form_class=ReviewForm
    success_url=reverse_lazy("review_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article_pk'] = self.kwargs.get('article_pk')
        return context

    def get(self, request, *args, **kwargs):
        article=get_object_or_404(Article,pk=self.kwargs.get('article_pk'))
        if article.author==request.user.get_profile():
            return redirect("myprofile_details")
        form = self.form_class()
        return render(request, self.template_name, {'form': form,"article_pk":self.kwargs.get('article_pk')})

    def form_valid(self, form):
        article=get_object_or_404(Article,pk=self.kwargs.get('article_pk'))
        if article.author==self.request.user.get_profile:
            return redirect("myprofile_details")
        form.instance.author = self.request.user.get_profile()
        form.instance.target=article
        return super(ReviewCreateView, self).form_valid(form)

class ReviewDetailView(DetailView):
    template_name = 'review/details.html'
    model=Review
    queryset = Review.objects.filter(is_active=True,is_public=True)

class ReviewListView(ListView):
    template_name='review/list.html'
    paginate_by=10

    def get_queryset(self):
        # if(not (self.request.user.is_staff)):
        #     queryset=Review.objects.filter(is_active=True)
        #     return queryset
        queryset=Review.objects.filter(is_active=True,is_public=True)
        return queryset

class ReviewListViewArticle(ListView):
    template_name='review/list.html'
    paginate_by=10

    def get_queryset(self):
        # if(not (self.request.user.is_staff)):
        #     queryset=Review.objects.filter(is_active=True)
        #     return queryset
        queryset=Review.objects.filter(is_active=True)
        return queryset

class ReviewUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'review/update.html'
    form_class=ReviewForm
    #success_url = reverse_lazy('review_update', kwargs={'pk': self.pk})

    def get_queryset(self):
        queryset=Review.objects.filter(author=self.request.user.get_profile())
        return queryset

    def get_success_url(self):
        """
        更処理完了時の戻り先URL
        https://docs.djangoproject.com/ja/2.0/ref/class-based-views/generic-editing/
        :return:
        """
        return reverse('review_details', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user.get_profile()
        return super(ReviewUpdateView, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        # Custom user permission check
        self.object=self.get_object()
        if self.request.user.is_authenticated and \
         self.object.author!=self.request.user.get_profile():
                return HttpResponseForbidden()
        return super(ReviewUpdateView, self).dispatch(*args, **kwargs)


class ReviewDeleteView(LoginRequiredMixin,DeleteView):
    template_name="review/delete.html"
    success_url="index"
    def get_success_url(self):
        return reverse(self.success_url)

    def get_queryset(self):
        queryset=Review.objects.filter(author=self.request.user.get_profile())
        return queryset

    def dispatch(self, *args, **kwargs):
        # Custom user permission check
        self.object=self.get_object()
        if self.request.user.is_authenticated and \
         self.object.author!=self.request.user.get_profile():
                return HttpResponseForbidden()
        return super(ReviewDeleteView, self).dispatch(*args, **kwargs)
