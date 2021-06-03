from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import Model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
import inspect
from . import models
from django.contrib.auth.forms import UserCreationForm

# стандартные вьюхи админки регают юзера в обход менеджера обьектов юзера из-за чего не хешериуется пароль и
# авторизация невозможна - необходимо переопределить формы админа для базового юзера !
"""class UserCreationForm(forms.ModelForm):
    A form for creating new users. Includes all the required
    fields, plus a repeated password
    email = forms.EmailInput()
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    role = forms.ChoiceField(label='Role',choices=models.ROLES_CHOICES)
    class Meta:
        model = models.UserProfile
        fields = ('email','password','role')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.UserProfile
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


# Now register the new UserAdmin...

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email',)
    list_filter = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password','role')}),

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2','role')}
         ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    exclude = ("username",)
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()"""

for name, obj in inspect.getmembers(models):
    if inspect.isclass(obj) and issubclass(obj, Model) and not obj._meta.abstract:
        admin.site.register(obj)
        # if obj is not models.UserProfile:

# admin.site.register(models.UserProfile, UserAdmin)

# Register your models here.
