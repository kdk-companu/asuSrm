from django import forms

from apps.workers.models import Subdivision, Department, Chief


class Form_Subdivision_Control(forms.ModelForm):
    """Управление."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Subdivision
        fields = ['name', 'abbreviation', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Управление/Подразделение', 'id': 'name'}),
            'abbreviation': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Сокращенное название', 'id': 'abbreviation'}),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Описание', 'id': 'description'})
        }


class Form_Department_Control(forms.ModelForm):
    """Управление."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Department
        fields = ['name', 'abbreviation', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Отдел', 'id': 'name'}),
            'abbreviation': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Сокращенное название', 'id': 'abbreviation'}),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Описание', 'id': 'description'})
        }


class Form_Chief_Control(forms.ModelForm):
    """Должность."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Chief
        fields = ['name', 'abbreviation', 'rights']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Должность', 'id': 'name'}),
            'abbreviation': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Сокращенное название', 'id': 'abbreviation'}),
            'rights': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'По старшинству', 'id': 'rights'})
        }
