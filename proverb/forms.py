from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm
)
from .models import *
import re
from django.shortcuts import get_object_or_404
from betterforms.multiform import MultiForm
from django_registration.forms import RegistrationForm as DjangoRegistrationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=["screenname","gender",'date_of_birth',"description","mail_magazine","is_public"]

class ThumbnailForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=["avatar"]

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

class RegistrationForm(DjangoRegistrationForm):
    class Meta(DjangoRegistrationForm.Meta):
        model = User

class ArticleForm(forms.ModelForm):
    class Meta:
        model=Article
        fields=["title","description","type","is_public"]
        #localized_fields=["hashTags",]
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget=forms.Textarea(attrs={"rows":1,"cols":40})
        self.fields['description'].widget=forms.Textarea(attrs={"rows":30,"cols":40,})

    def clean(self):
        title=self.cleaned_data["title"]
        description=self.cleaned_data["description"]

        if not title or not description:
            raise forms.ValidationError(u"Please correct title or description")

        title=HashTag.convert_string_to_name(title)
        if HashTag.check_string("#"+title)==None:
            raise forms.ValidationError(u"This title is invalid. Please correct it.")
        hash_tags=self.extract_tags(description)
        if self.cleaned_data["type"] == "Original":
            hash_tags.append("#"+title)
        hash_tags=list(set(hash_tags))
        for t in hash_tags:
            if HashTag.check_string(t)==False:
                raise forms.ValidationError("There are invalid hash tags.\
                Please confirm your hash tags again")
        if 5<len(hash_tags):
            #form.add_error(None,u"Please reduce hash tags less than 5")
            raise forms.ValidationError(u"Please reduce hash tags less than 5.\
             If this article is set as original article, the title is inputed into hash tags automatically.\
             In this case, please reduce hash tags less than 4.")
        return self.cleaned_data

    def save(self, commit=True, *args, **kwargs):
        m = super(ArticleForm, self).save(commit=True, *args, **kwargs)

        title=self.instance.title.replace(" ","_")
        description=self.instance.description

        hash_tags=self.extract_tags(description)
        if self.instance.type == "Original":
            hash_tags.append("#"+title)
        hash_tags=list(set(hash_tags))

        self.instance.hashTags.clear()
        for tag in hash_tags:
            t,result=HashTag.objects.get_or_create(name=tag)
            if result==True:
                t.save()
            self.instance.hashTags.add(t)
        return m

    def extract_tags(self,description):
        hash_tags=[i for i in re.split(r"\n|\s",description) if re.compile(r"^#[a-zA-Z0-9_\,\.]+$").match(i)!=None and i!="#"]
        return hash_tags

class ReviewForm(forms.ModelForm):
    class Meta:
        model=Review
        fields=["title","description","score","is_public"]
        #localized_fields=["hashTags",]
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget=forms.Textarea(attrs={"rows":1,"cols":40,})
        self.fields['description'].widget=forms.Textarea(attrs={"rows":30,"cols":40,})

    def save(self, commit=True, *args, **kwargs):
        m = super(ReviewForm, self).save(commit=True, *args, **kwargs)
        article=get_object_or_404(Article,pk=m.target.pk)
        article.reviews.add(m)
        return m

class MylistForm(forms.ModelForm):
    class Meta:
        model=Mylist
        fields=["title","description","is_public"]

class AddMylistForm(forms.Form):
    manipulation=forms.CharField(max_length=20)
    article=forms.ModelChoiceField(label="Article",queryset=None)
    mylist=forms.ModelChoiceField(label="Mylist",queryset=None)

    def __init__(self,*args, **kwargs):
        #super().__init__(*args, **kwargs)
        user=kwargs.pop('user', None)
        profile=user.get_profile()
        article=kwargs.pop('article', None)
        super(AddMylistForm,self).__init__(*args, **kwargs)
        self.fields["article"].queryset=Article.objects.filter(pk=article.pk)
        self.fields["mylist"].queryset=Mylist.objects.filter(author=profile)

class ManipulationForm(forms.Form):
    manipulation=forms.CharField(max_length=20)

class DeleteMylistArticleForm(forms.Form):
    manipulation=forms.CharField(max_length=20)
    article=forms.ModelChoiceField(label="Article",queryset=None)
    def __init__(self,*args, **kwargs):
        mylist=kwargs.pop('mylist', None)
        super(DeleteMylistArticleForm,self).__init__(*args, **kwargs)
        self.fields["article"].queryset=mylist.articles.all()

class FollowForm(forms.Form):
    profile=forms.ModelChoiceField(label="Profile",queryset=Profile.objects.filter(user__is_admin=False,user__is_active=True))

class ArticleSearchForm(forms.Form):
    title = forms.CharField(
        initial='',
        label='Title',
        required = False,
    )
    description = forms.CharField(
        initial='',
        label='Description',
        required = False,
    )
    author = forms.CharField(
        initial='',
        label='Author',
        required = False,
    )
    hashTags = forms.CharField(
        initial='',
        label='Hash Tag',
        required = False,
    )

class WithdrawalForm(forms.Form):
    confirm=forms.BooleanField(
        label='read terms',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'check'}),
    )
# class NumOrderForm(forms.Form):
#     num = forms.IntegerField()
#     order = forms.CharField(max_length=20)
#
# class OrderForm(forms.Form):
#     order = forms.CharField(max_length=20)
#
# class AddMylistForm(forms.Form):
#     #query of mylist must be inputed
#     article=forms.ModelChoiceField(label="Article",queryset=None)
#     mylist=forms.ModelChoiceField(label="Mylist",queryset=None)

# class ArticleDetailForm(MultiForm):
#     form_classes={
#         "order":OrderForm,
#         "addMylist":AddMylistForm,
#     }
#     def __init__(self,*args, **kwargs):
#         #super().__init__(*args, **kwargs)
#         user=kwargs.pop('user', None)
#         profile=user.get_profile()
#         article=kwargs.pop('article', None)
#         super(ArticleDetailForm,self).__init__(*args, **kwargs)
#
#
#         #self.fields['choice'].queryset = question.choice_set.all()
#         self["addMylist"].fields["article"].queryset=Article.objects.filter(pk=article.pk)
#         self["addMylist"].fields["mylist"].queryset=Mylist.objects.filter(author=profile)
