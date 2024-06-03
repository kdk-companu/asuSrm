from django import forms
from django.core.exceptions import ValidationError

from apps.workobjects.models import OrganizationsObjects


class OrganizationsObjects_Form_Filter(forms.ModelForm):
    """Объекты. Форма поиска. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].empty_label = "Эксплуатирующая организация"

    class Meta:
        model = OrganizationsObjects
        fields = ['organization', ]
        widgets = {
            'organization': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%', 'id': 'organization'}),
        }


class OrganizationsObjects_Form_Control(forms.ModelForm):
    """Объекты. Форма заполнения."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].empty_label = "Выберите эксплуатирующую организацию*"

    class Meta:
        model = OrganizationsObjects
        fields = ['organization', 'name', 'name_tables', 'short_names', 'city', 'property_location',
                  'pay_weekend', 'pay_processing', 'description']
        widgets = {
            'organization': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%', 'id': 'organization'}),
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Название объекта*', 'id': 'name'}),
            'name_tables': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Название для табеля', 'id': 'name_tables'}),
            'short_names': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Обиходные', 'id': 'short_names'}),
            'city': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ближайший город', 'id': 'city'}),
            'property_location': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Расположение объекта. Транспорт.',
                       'id': 'property_location'}),
            'pay_weekend': forms.CheckboxInput(
                attrs={'class': 'custom-control-input', 'id': 'pay_weekend'}),
            'pay_processing': forms.CheckboxInput(
                attrs={'class': 'custom-control-input', 'id': 'pay_processing'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Описание объекта', 'id': 'description'}),

        }
