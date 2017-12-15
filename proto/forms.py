from django import forms
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django_select2.forms import ModelSelect2TagWidget
from django.conf import settings
from .models import Photographer, Photo, Category
from .widgets import DatePickerInput


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password', 'email']


class UserPanelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserPanelForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = "Business email"


class PhotographerForm(forms.ModelForm):
    birth_date = forms.DateField(widget=DatePickerInput, input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Photographer
        # TODO: migrate to using explicit field inclusion
        fields = '__all__'
        exclude = ['user', 'categories', 'vat_number', 'disabled', 'deleted',
                   'email_notification_code', 'is_mock']

    def __init__(self, *args, **kwargs):
        super(PhotographerForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].help_text = "International format"
        self.fields['mobile_number'].help_text = "International format"


class UserLoginForm(forms.ModelForm):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password']


class CategoryWidget(ModelSelect2TagWidget):
    search_fields = ['name__icontains']
    model = Category
    queryset = Category.objects.all()

    def value_from_datadict(self, data, files, name):
        values = data.getlist('categories')
        pks = list(map(str,
                  self.queryset.filter(
                      pk__in=filter(lambda v: force_text(v).isdigit(), values)
                  ).values_list('pk', flat=True)))
        cleaned_values = []

        for val in values:
            if str(val) not in pks:
                instance, c = self.queryset.get_or_create(name=val)
                val = instance.pk
            cleaned_values.append(val)
        return cleaned_values


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = ['deleted', 'disabled', 'photographer']
        widgets = {
            'categories': CategoryWidget(
                attrs={'class': 'mb0 input-md'}
            )
        }


class PhotoUpdateForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = ['image', 'deleted', 'disabled', 'photographer']
        widgets = {
            'categories': CategoryWidget(
                attrs={'class': 'form-control input-md'}
            )
        }
