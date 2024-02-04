from django import forms
from django.core.exceptions import ValidationError

from apps.workers.models import User, User_Basic


class Search_Filter(forms.Form):
    """Форма поиска. Общая"""
    search = forms.CharField(label='Поиск в базе',
                             max_length=150,
                             required=False,
                             widget=forms.TextInput(
                                 attrs={'type': 'search', 'class': 'form-control form-control-lg', 'placeholder': ''}))


class Search_User_Filter(forms.ModelForm):
    """Форма поиска. пользователь расширенная."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization_subdivision'].empty_label = "Выберите управление"
        self.fields['organization_department'].empty_label = "Выберите отдел"
        self.fields['chief'].empty_label = "Выберите должность"

    class Meta:
        model = User_Basic
        fields = ['organization_subdivision', 'organization_department', 'chief']
        widgets = {
            'organization_subdivision': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%', 'id': 'organization_subdivision'}),
            'organization_department': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%', 'id': 'organization_department'}),
            'chief': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%', 'id': 'chief'}),
        }


class Workers_Add_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Пароль', 'id': 'password1'}))
    password2 = forms.CharField(label='Подверженнее пароля', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Подверженнее пароля', 'id': 'password2'}))

    class Meta:
        model = User
        fields = ('surname', 'name', 'patronymic', 'phone')
        widgets = {
            'surname': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Фамилия', 'id': 'surname'}),
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Имя', 'id': 'name'}),
            'patronymic': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Отчество', 'id': 'patronymic'}),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Телефон', 'id': 'phone'}),
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароль не совпадает.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class Workers_Form_Add_Workers(Workers_Add_Form):
    pass
