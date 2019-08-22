from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth import get_user_model
import re
from django.db.models import Avg,Max,Q
from django.shortcuts import get_object_or_404
from proverb import utils
from django.forms.models import model_to_dict
import json
from datetime import date, datetime
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
import os
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.contrib.auth.models import AnonymousUser as DjangoAnonymousUser
from django.http import Http404

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        #user.is_superuser = True
        user.is_admin = True
        #user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    information=models.ForeignKey("Profile",on_delete=models.CASCADE,related_name="owner",null=True)
    is_active = models.BooleanField(default=True)
    #is_staff = models.BooleanField(default=False)
    #is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['date_of_birth']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def has_profile(self):
        return Profile.objects.filter(user=self).exists()

    def get_profile(self):
        return get_object_or_404(Profile, user=self)

    @property
    def is_staff(self):
        return self.is_superuser or self.is_admin

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_staff
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

#https://torina.top/detail/233/
def get_avatar_upload_to(instance, filename):
    return os.path.join("avatars",str(instance.pk), filename)

#https://qiita.com/kojionilk/items/da20c732642ee7377a78
def delete_profile_previous_file(function):
    """不要となる古いファイルを削除する為のデコレータ実装.

    :param function: メイン関数
    :return: wrapper
    """
    def wrapper(*args, **kwargs):
        """Wrapper 関数.

        :param args: 任意の引数
        :param kwargs: 任意のキーワード引数
        :return: メイン関数実行結果
        """
        self = args[0]

        # 保存前のファイル名を取得
        result = Profile.objects.filter(pk=self.pk)
        previous = result[0] if len(result) else None
        super(Profile, self).save()

        # 関数実行
        result = function(*args, **kwargs)

        # 保存前のファイルがあったら削除
        #filepath=os.path.join(settings.MEDIA_ROOT,"avatars",str(previous.pk), previous.avatar.name)

        # if previous and previous.avatar:
        #     filepath=previous.avatar.path
        #     if os.path.exists(filepath):
        #         os.remove(filepath)
        try:
            if previous and previous.avatar:
                filepath=previous.avatar.path
                if os.path.exists(filepath):
                    os.remove(filepath)
        except:
            ### For google storage ###
            if previous and previous.avatar:
                filepath=previous.avatar.name
                if default_storage.exists(filepath):
                    default_storage.delete(filepath)

        return result
    return wrapper

class AnonymousUser(DjangoAnonymousUser):
    ip = None

    def __init__(self, request):
        self.ip = request.META.get('REMOTE_ADDR')
        super(AnonymousUser, self).__init__()

    def has_profile(self):
        return False

    def get_profile(self):
        raise Http404

    @property
    def is_staff(self):
        return False

class Profile(models.Model):
    PROFILE_GENDER_STATUSES = (("None","None"),
    ("Man",'Man'),
    ("Woman",'Woman'),)
    user=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    screenname = models.CharField('username (for display)', max_length=50, unique=True)
    date_of_birth = models.DateField(blank=True,null=True)
    gender=models.CharField("gender",choices=PROFILE_GENDER_STATUSES,max_length=10,default="None")
    follow=models.ManyToManyField("Profile",blank=True,verbose_name="follow")
    #follower=models.ManyToManyField("Profile",blank=True,verbose_name="follower")
    interesting_tag=models.ManyToManyField("HashTag",blank=True)
    description=models.TextField("Description",blank=True)
    mylists=models.ManyToManyField("Mylist",blank=True)
    mail_magazine=models.BooleanField("mail magazine is accepted",default=True)
    badges=models.ManyToManyField("Badge",blank=True)
    avatar = models.ImageField(upload_to=get_avatar_upload_to,blank=True,null=True)
    thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(100, 100)],
                                      format='JPEG',
                                      options={'quality': 60})
    is_active=models.BooleanField(default=False,verbose_name="this is active")
    is_public=models.BooleanField(default=False,verbose_name="this is public")
    #premium_period=models.DateTimeField(default=(datetime.date.now()-datetime.timedelta(years=100)))
    premium_period=models.DateTimeField(default=date(2002, 3, 11))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'

    @delete_profile_previous_file
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Profile, self).save()

    @delete_profile_previous_file
    def delete(self, using=None, keep_parents=False):
        super(Profile, self).delete()

    def add_follow(self,pk):
        target=get_object_or_404(Profile,pk=pk)
        self.follow.add(target)

    def cancel_follow(self,pk):
        target=get_object_or_404(Profile,pk=pk)
        self.follow.remove(target)

    def get_followers(self):
        followers=Profile.objects.filter(follow=self)
        return followers

    def count_follows(self):
        return self.follow.all().count()

    def count_followers(self):
        return Profile.objects.filter(follow=self).count()

    def count_articles(self):
        return Article.objects.filter(author=self,is_active=True,is_public=True).count()

    def count_positive_reviews(self):
        return Review.objects.filter(target__author=self,is_active=True,is_public=True,score__gte=4).count()

    def count_badges(self):
        return self.badges.all().count()

    def get_articles(self):
        return Article.objects.filter(author=self)

    def is_following(self,target):
        return self.follow.filter(pk=target.pk).exists()

    @property
    def is_premium(self):
        dt=self.premium_period-timezone.datetime.now(timezone.get_current_timezone())
        if dt.days>=0:
            return True
        return False

    def __unicode__(self):
        return str(self.pk)+"_"+self.screenname

    def __str__(self):
        return str(self.pk)+"_"+self.screenname

    def get_description(self):
        #return utils.bleach_value(self.description)
        return self.description

    def get_representative(self):
        qs=Article.objects.filter(author=self,is_public=True)
        unsorted_results = qs.all()
        sorted_results = sorted(unsorted_results, key= lambda t: t.get_score(),reverse=True)
        return sorted_results

    def get_mylists(self):
        queryset=Mylist.objects.filter(Q(author=self)|Q(is_active=True))
        return queryset

    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        #return os.path.join("static","images","thumbnail.jpg")
        return static("images/thumbnail.jpg")

class Mylist(models.Model):
    author=models.ForeignKey("Profile",on_delete=models.DO_NOTHING,)
    title=models.CharField('title', max_length=300)
    description=models.TextField("description",max_length=300,blank=True)
    articles=models.ManyToManyField("ArticleOfMylist",blank=True)
    is_active=models.BooleanField(default=True,verbose_name="this is active")
    is_public=models.BooleanField(default=True,verbose_name="this is public")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def normalization(self):
        counter=10
        original=self.articles.order_by('number')
        for article in self.articles.all():
            article.number=counter
            article.save()
            counter+=10

    def insert_before(self,article_pk,target_pk):
        #article_pk is inserted article's pk
        #target_pk is the target
        pass

    # def insert_article(self,user,article_pk):
    #     article=get_object_or_404(Article,pk=article_pk)
    #     memory,results=ArticleOfMylist.objects.get_or_create(user=user,
    #                                                  target=article,
    #                                                  target_mylist=self)
    #     max_number=self.articles.aggregate(Max('number'))["number__max"]
    #     memory.number=max_number+10
    #     memory.save()
    #     self.normalization()

    def add_article(self,article):
        #article=get_object_or_404(Article,pk=article_pk)
        memory,results=ArticleOfMylist.objects.get_or_create(author=self.author,
            target=article,target_mylist=self)
        max_number=self.articles.aggregate(Max('number'))["number__max"]
        if max_number==None:
            max_number=0
        memory.number=max_number+10
        memory.save()
        self.articles.add(memory)
        self.normalization()

    def __unicode__(self):
        return str(self.pk)+"_"+self.title

    def __str__(self):
        return str(self.pk)+"_"+self.title

    def get_description(self):
        return utils.bleach_value(self.description)

    def count_memories(self):
        return self.articles.all().count()

class ArticleOfMylist(models.Model):
    author=models.ForeignKey("Profile",on_delete=models.DO_NOTHING,)
    target=models.ForeignKey("Article",on_delete=models.CASCADE,)
    target_mylist=models.ForeignKey("Mylist",on_delete=models.CASCADE,)
    description=models.TextField("description",max_length=200)
    number=models.IntegerField("number of mylist",default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return str(self.target.pk)+"_"+self.target.title

    def __str__(self):
        return str(self.target.pk)+"_"+self.target.title

class HashTag(models.Model):
    name=models.CharField("the title",max_length=100,null=False)

    def check_existing_or_delete(self):
        #checking whether there are any article which has the tag or not
        #if there is nothing, this tag is deleted
        if self.count_articles()<=0:
            self.delete()
            return False
        return True

    def check_string(string):
        result=re.compile(r"^#[a-zA-Z0-9_\,\.\!\?]+$").match(string)
        if result==None:
            return False
        if HashTag._meta.get_field("name").max_length<=len(string):
            return False
        return True

    def convert_string_to_name(string):
        string=string.replace(" ","_")
        return string

    def count_articles(self):
        return Article.objects.filter(hashTags__name=self.name).count()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_wordname(self):
        #the name without "#"
        return self.name.lstrip("#")

class Badge(models.Model):
    name=models.CharField("the title",max_length=150,null=False)
    description=models.TextField("description",max_length=1000)
    proposed_at= models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Review(models.Model):
    title=models.CharField("the title",max_length=250,null=False)
    author=models.ForeignKey("Profile",on_delete=models.DO_NOTHING,)
    target=models.ForeignKey("Article",on_delete=models.CASCADE,)
    description=models.TextField("description",max_length=2000)
    score=models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_active=models.BooleanField(default=True,verbose_name="this is active")
    is_public=models.BooleanField(default=True,verbose_name="this is public")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return str(self.pk)+"_"+self.title

    def __str__(self):
        return str(self.pk)+"_"+self.title

class Article(models.Model):
    TYPE_OF_ARTICLE_CHOICES = (
    ('Original', 'Original'),
    ('Quote', 'Quote'))
    title=models.CharField("the title",max_length=50,null=False)
    description=models.TextField("Description")
    hashTags=models.ManyToManyField(HashTag)
    author=models.ForeignKey("Profile",on_delete=models.DO_NOTHING,)
    type=models.CharField("Type of article",choices=TYPE_OF_ARTICLE_CHOICES,max_length=20)
    reviews=models.ManyToManyField(Review)
    number_of_views=models.IntegerField("number of views",default=0)
    is_active=models.BooleanField(default=True,verbose_name="this is active")
    is_public=models.BooleanField(default=True,verbose_name="this is public")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __unicode__(self):
        return str(self.pk)+"_"+self.title

    def __str__(self):
        return str(self.pk)+"_"+self.title

    def get_score(self):
        result=self.reviews.aggregate(Avg('score'))
        if result["score__avg"]==None:
            return 0
        return result["score__avg"]

    def get_description(self):
        return utils.bleach_value(self.description)

    def count_good_reviews(self):
        return Review.objects.filter(target=self).filter(score__gte=4).count()

    def plus_one_views(self):
        self.number_of_views+=1
        self.save()


    @property
    def count_views(self):
        return self.number_of_views

class Log(models.Model):
    user=models.ForeignKey(get_user_model(),on_delete=models.CASCADE,null=True,blank=True)
    ip_address=models.CharField(max_length=100,null=True)
    path=models.CharField(max_length=300)
    func_name=models.CharField(max_length=100)
    method=models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    #request_meta = utils.get_json_model_field()

class Epitaph(models.Model):
    email = models.EmailField(max_length=255,)
    data = utils.get_json_model_field()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.email
    def __str__(self):
        return self.email

    # def __init__(self, user, *args, **kwargs):
    #     super(models.Model, self).__init__(self, *args, **kwargs)
    #     self.email=user.email

    @classmethod
    def create(cls,user):
        epitaph=cls(email=user.email)
        return epitaph

    def write(self):
        user=get_object_or_404(User,email=self.email,is_staff=False)
        profile=user.get_profile()
        articles=Article.objects.filter(author=profile)
        reviews=Review.objects.filter(author=profile)
        data={}
        data["user"]=model_to_dict(user)
        data["profile"]=model_to_dict(profile)
        data["articles"]=list(articles.values())
        data["reviews"]=list(reviews.values())
        self.data=json.dumps(data,default=self.json_serial)
        self.save()

    def kill(self):
        self.write()
        user=get_object_or_404(User,email=self.email,is_staff=False)
        profile=user.get_profile()
        articles=Article.objects.filter(author=profile)
        reviews=Review.objects.filter(author=profile)
        reviews.delete()
        articles.delete()
        profile.delete()
        user.delete()

    def json_serial(self,obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))
