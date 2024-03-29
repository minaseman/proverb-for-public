from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.conf import settings
from proverb.models import *
from proverb.forms import *
from django.contrib.sites.models import Site

# Register your models here.

class AdminUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = AdminUserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_superuser',"is_admin","is_active")
    list_filter = ('is_superuser',"is_admin",)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        #('Personal info', {'fields': ('date_of_birth',"gender",)}),
        ('Permissions', {'fields': ("is_admin",)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

class LogAdmin(admin.ModelAdmin):
    list_display = ('path', 'user',"ip_address","created_at")
    #fields = ["user","ip_address","path","func_name","method","created_at"]

admin.site.register(Log,LogAdmin)

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)

proverb_models=[Profile, HashTag,
 Badge, Review,Article,Mylist,ArticleOfMylist,Epitaph]
admin.site.register(proverb_models)
