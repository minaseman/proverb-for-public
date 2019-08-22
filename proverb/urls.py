from django.urls import path,include

from .view import about
from .views import *
from .view.article import *
from .view.account import *
from .view.mylist import *
from .view.badge import *
from django.contrib import admin
from .forms import *
from django_registration.backends.activation.views import RegistrationView
from django.conf.urls import url
user_urls=[
    path("",user,name="user_information"),
    path("update/",UserUpdateView.as_view(),name="user_update"),
]
reviews_urls=[
    path("list/",ReviewListView.as_view(),name="review_list"),
    path("<int:article_pk>/list/",ReviewListViewArticle.as_view(),name="review_list_article"),
    path("<int:article_pk>/create/",ReviewCreateView.as_view(),name="review_create"),
    path("<int:pk>",ReviewDetailView.as_view(),name="review_details"),
    path("<int:pk>/delete/",ReviewDeleteView.as_view(),name="review_delete"),
    path("<int:pk>/update/",ReviewUpdateView.as_view(),name="review_update"),
]

articles_urls=[
    path("list/",ArticleListView.as_view(),name="article_list"),
    path("create/",ArticleCreateView.as_view(),name="article_create"),
    path("<int:pk>/",ArticleDetailView.as_view(),name="article_details"),
    path("<int:pk>/delete/",ArticleDeleteView.as_view(),name="article_delete"),
    path("<int:pk>/update/",ArticleUpdateView.as_view(),name="article_update"),
    path('reviews/', include(reviews_urls)),
]

profile_urls=[
    path("<int:pk>/",ProfileDetailView.as_view(),name="profile_details"),
    path("",MyProfileDetailView.as_view(),name="myprofile_details"),
    # path("list/",ProfileListView.as_view(),name="profile_list"),
    path("create/",ProfileCreateView.as_view(),name="profile_create"),
    path("update/",ProfileUpdateView.as_view(),name="profile_update"),
    path("<int:pk>/update/",ProfileUpdateView.as_view(),name="profile_update"),
    path("follow/",follow,name="follow"),
    path("follows/my/",MyFollowListView.as_view(),name="my_follow_list"),
    path("followers/my/",MyFollowerListView.as_view(),name="my_follower_list"),
    path("follows/<int:pk>/",FollowListView.as_view(),name="follow_list"),
    path("followers/<int:pk>/",FollowerListView.as_view(),name="follower_list"),
    path("follow/cancel/",cancel_follow,name="cancel_follow"),
    path("withdrawal/",withdrawal,name="withdrawal"),
    path("badgebox/my/",mybadgebox,name="my_badgebox"),
    path("badgebox/<int:pk>/",badgebox,name="badgebox"),
]

mylist_urls=[
    path("list/my/",MyMylistListView.as_view(),name="my_mylist_list"),
    path("list/<int:pk>/",MylistListView.as_view(),name="mylist_list"),
    path("create/",MylistCreateView.as_view(),name="mylist_create"),
    path("<int:pk>/",MylistDetailView.as_view(),name="mylist_details"),
    path("<int:pk>/delete/",MylistDeleteView.as_view(),name="mylist_delete"),
    path("<int:pk>/update/",MylistUpdateView.as_view(),name="mylist_update"),
]

about_urls=[
    path("us/",about.us,name="about_us"),
    path("how_to_use/",about.how_to_use,name="about_how_to_use"),
    path("writing_policy/",about.writing_policy,name="about_writing_policy"),
    path("proverb/",about.proverb,name="about_proverb"),
    path("what_is_proverb/",about.what_is_proverb,name="about_what_is_proverb"),
    path("privacy_policy/",about.privacy_policy,name="about_privacy_policy"),
    path("copyright/",about.copyright,name="about_copyright"),
    path("developped_by/",about.developped_by,name="about_developped_by"),
]

urlpatterns = [
    path('', index, name='index'),
    path('user/', include(user_urls)),
    # path('accounts/register/',
    #     RegistrationView.as_view(
    #         form_class=RegistrationForm
    #     ),
    #     name='django_registration_register',
    # ),
    #path('accounts/', include('django_registration.backends.activation.urls')),
    #Django Registration
    url(r'^accounts/register/$',
        RegistrationView.as_view(
            form_class=RegistrationForm
        ),
        name='django_registration_register',
    ),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('auth/', include('social_django.urls', namespace='social')), # <- 追記
    # AllAuth #
    #path('accounts/', include('allauth.urls')),
    # path('before accounts/', include('django.contrib.auth.urls')),
    # path("before accounts/create/",UserRegistration.as_view(),name="account_create"),
    path('profile/', include(profile_urls)),
    path('articles/', include(articles_urls)),
    path('mylist/', include(mylist_urls)),
    path('about/', include(about_urls)),
]

    #path('accounts/', include('django.contrib.auth.urls')),
    #this means
    # accounts/login/ [name='login'] accounts/logout/ [name='logout']
    # accounts/password_change/ [name='password_change']
    # accounts/password_change/done/ [name='password_change_done']
    # accounts/password_reset/ [name='password_reset']
    # accounts/password_reset/done/ [name='password_reset_done']
    # accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # accounts/reset/done/ [name='password_reset_complete']

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
