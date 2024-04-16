import os

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Permission, Group
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Q
from django.forms import SelectMultiple, CheckboxInput, CheckboxSelectMultiple
from transliterate.utils import _
from apps.workers.models import User, User_Basic, User_Closed
from library.archive import Archive
from library.files import Files


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


class Workers_Form_PasswordChange(SetPasswordForm):
    error_messages = {
        **SetPasswordForm.error_messages,
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    }
    old_password = forms.CharField(
        label=_("Старый пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password', 'autofocus': True,
            'class': 'form-control', 'placeholder': 'Старый пароль', 'id': 'old_password'}),
    )
    new_password1 = forms.CharField(
        label=_("Новый пароль"),
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control', 'placeholder': 'Новый пароль',
                   'id': 'new_password1'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control', 'placeholder': 'Подтверждение пароля',
                   'id': 'old_password'}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


class Workers_Form_Change(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].empty_label = "Статус не выбран."

    class Meta:
        model = User
        fields = ('surname', 'name', 'patronymic', 'phone', 'email', 'employee')
        widgets = {
            'surname': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Фамилия', 'id': 'surname'}),
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Имя', 'id': 'name'}),
            'patronymic': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Отчество', 'id': 'patronymic'}),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'data-mask': "+7(000)000-0000"}),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'type': 'text', 'placeholder': 'Почта', 'id': 'email'}),
            'employee': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
        }


class Workers_Form_Basic_Change(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization_subdivision'].empty_label = "Управление не выбрано."
        self.fields['organization_department'].empty_label = "Отдел не выбран."
        self.fields['actual_subdivision'].empty_label = "Управление не выбрано."
        self.fields['actual_department'].empty_label = "Отдел не выбран."
        self.fields['chief'].empty_label = "Должность не выбрана."

    class Meta:
        model = User_Basic
        fields = (
            'organization_subdivision', 'organization_department', 'actual_subdivision', 'actual_department', 'chief',
            'date_employment', 'date_chief',
            'employee_date', 'number_ga', 'date_birth', 'home_address', 'home_metro', 'gender')
        widgets = {
            'organization_subdivision': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'organization_department': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'actual_subdivision': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'actual_department': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'chief': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'number_ga': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Номер табеля', 'id': 'number_ga', 'type': 'number'}),
            'home_address': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Домашний адрес', 'id': 'home_address'}),
            'home_metro': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ближайшее метро', 'id': 'home_metro'}),

            'gender': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),

        }

    date_employment = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата трудоустройства",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_chief = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата в должности",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    employee_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата увольнения",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата рождения",
        input_formats=('%d.%m.%Y',),
        required=False
    )


class Workers_Form_Closed_Change(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['organization_subdivision'].empty_label = "Управление не выбрано."
        # self.fields['organization_department'].empty_label = "Отдел не выбран."
        # self.fields['actual_subdivision'].empty_label = "Управление не выбрано."
        # self.fields['actual_department'].empty_label = "Отдел не выбран."
        # self.fields['chief'].empty_label = "Должность не выбрана."

    class Meta:
        model = User_Closed
        fields = (
            'organization_order_of_employment', 'organization_labor_contract', 'passport_serial', 'passport_number',
            'passport_passport_issued', 'passport_passport_issued_date', 'passport_place_of_issue',
            'passport_registration', 'passport_of_residence',
            'snils_number', 'inn_number')
        widgets = {
            'organization_order_of_employment': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Приказ о трудоустройстве',
                       'id': 'organization_order_of_employment'}),
            'organization_labor_contract': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Трудовой договор',
                       'id': 'organization_labor_contract'}),
            'passport_serial': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Паспорт Серия', 'id': 'passport_serial',
                       'type': 'number'}),
            'passport_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Паспорт Номер', 'id': 'passport_number',
                       'type': 'number'}),
            'passport_passport_issued': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Паспорт Выдан',
                       'id': 'passport_passport_issued'}),
            'passport_place_of_issue': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Паспорт Код подразделения',
                       'id': 'passport_place_of_issue'}),
            'passport_registration': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Паспорт Место выдачи',
                       'id': 'passport_registration'}),
            'passport_of_residence': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Паспорт Прописка',
                       'id': 'passport_of_residence'}),
            'snils_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'СНИЛС номер',
                       'id': 'snils_number'}),
            'inn_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Инн номер',
                       'id': 'inn_number'}),
        }

    passport_passport_issued_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата трудоустройства",
        input_formats=('%d.%m.%Y',),
        required=False
    )


class Workers_Form_Upload_Images(forms.ModelForm):
    ALLOWED_TYPES = ['jpg', 'jpeg', 'png', 'gif']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if not image:
            raise forms.ValidationError('Изображение отсутствует.')
        if str(image).find("/") != -1:
            raise forms.ValidationError('Вы не выбрали изображение.')
        try:
            extension = os.path.splitext(image.name)[1][1:].lower()
            if extension not in self.ALLOWED_TYPES:
                raise forms.ValidationError('Изображения не соответствует типу.')
        except Exception as e:
            raise forms.ValidationError('Неизвестная ошибка. Выберите другое изображение.')
        try:
            if image:
                if image.size > 3 * 1024 * 1024:
                    raise ValidationError("Максимальный размер изображения 3мб")
                if image.image.size[0] < 300 or image.image.size[1] < 300:
                    raise ValidationError("Маленькое разрешение изображения.( минимальное 300x300 pixels )")
                return image
            else:
                raise ValidationError("Не удалось прочитать загруженное изображение")
        except:
            raise ValidationError("Пустое изображение.")

    class Meta:
        model = User
        fields = ('image',)
        widgets = {
            'image': forms.FileInput(
                attrs={'class': 'custom-file-input', 'id': 'exampleInputFile', 'accept': ".jpg,.jpeg"}
            ),
        }


class Workers_Form_Upload_Passport(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['passport_scan'].empty_label = ""

    def clean_passport_scan(self):
        file = self.cleaned_data.get('passport_scan', False)
        # Проверка на повторное нажатие
        if '/' in str(file):
            raise ValidationError("Вы не выбрали файл.")
        try:
            file.size
        except:
            raise ValidationError("Пустой файл.")

        if file:
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("Максимальный размер файла 5мб")
        else:
            raise ValidationError("Не удалось прочитать загруженный файл")

        if not Files.check_pdf(file):
            raise ValidationError("Ошибка чтения pdf")
        return file

    class Meta:
        model = User_Closed
        fields = ('passport_scan',)
        widgets = {
            'passport_scan': forms.FileInput(
                attrs={'class': 'custom-file-input', 'id': 'customFile', 'accept': ".pdf"}
            ),
        }


class Workers_Form_Upload_Snils(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['snils_scan'].empty_label = ""

    def clean_passport_scan(self):
        file = self.cleaned_data.get('snils_scan', False)
        # Проверка на повторное нажатие
        if '/' in str(file):
            raise ValidationError("Вы не выбрали файл.")
        try:
            file.size
        except:
            raise ValidationError("Пустой файл.")

        if file:
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("Максимальный размер файла 5мб")
        else:
            raise ValidationError("Не удалось прочитать загруженный файл")

        if not Files.check_pdf(file):
            raise ValidationError("Ошибка чтения pdf")
        return file

    class Meta:
        model = User_Closed
        fields = ('snils_scan',)
        widgets = {
            'snils_scan': forms.FileInput(
                attrs={'class': 'custom-file-input', 'id': 'customFile', 'accept': ".pdf"}
            ),
        }


class Workers_Form_Upload_Inn(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inn_scan'].empty_label = ""

    def clean_passport_scan(self):
        file = self.cleaned_data.get('inn_scan', False)
        # Проверка на повторное нажатие
        if '/' in str(file):
            raise ValidationError("Вы не выбрали файл.")
        try:
            file.size
        except:
            raise ValidationError("Пустой файл.")

        if file:
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("Максимальный размер файла 5мб")
        else:
            raise ValidationError("Не удалось прочитать загруженный файл")

        if not Files.check_pdf(file):
            raise ValidationError("Ошибка чтения pdf")
        return file

    class Meta:
        model = User_Closed
        fields = ('inn_scan',)
        widgets = {
            'inn_scan': forms.FileInput(
                attrs={'class': 'custom-file-input', 'id': 'customFile', 'accept': ".pdf"}
            ),
        }


class Workers_Form_Upload_Archive(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archive_documents_employment'].empty_label = ""

    def clean_archive_documents_employment(self):
        file = self.cleaned_data.get('archive_documents_employment', False)
        # Проверка на повторное нажатие
        if '/' in str(file):
            raise ValidationError("Вы не выбрали файл.")
        try:
            file.size
        except:
            raise ValidationError("Пустой файл.")

        if file:
            if file.size > 30 * 1024 * 1024:
                raise ValidationError("Максимальный размер файла 30мб")
        else:
            raise ValidationError("Не удалось прочитать загруженный файл")

        # if not Archive.check_archive(file):
        #     raise ValidationError("Ошибка чтения архива")
        return file

    class Meta:
        model = User_Closed
        fields = ('archive_documents_employment',)
        widgets = {
            'archive_documents_employment': forms.FileInput(
                attrs={'class': 'custom-file-input', 'id': 'customFile', 'accept': ".rar"}
            ),
        }


class Workers_Form_Upload_Signature(forms.ModelForm):
    ALLOWED_TYPES = ['png', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_signature_example(self):
        image = self.cleaned_data.get('signature_example', False)
        if not image:
            raise forms.ValidationError('Изображение отсутствует.')
        if str(image).find("/") != -1:
            raise forms.ValidationError('Вы не выбрали изображение.')
        try:
            extension = os.path.splitext(image.name)[1][1:].lower()
            if extension not in self.ALLOWED_TYPES:
                raise forms.ValidationError('Изображения не соответствует типу.')
        except Exception as e:
            raise forms.ValidationError('Неизвестная ошибка. Выберите другое изображение.')
        try:
            if image:
                if image.size > 1 * 1024 * 1024:
                    raise ValidationError("Максимальный размер изображения 1мб")
                if image.image.size[0] < 300 or image.image.size[1] < 300:
                    raise ValidationError("Маленькое разрешение изображения.( минимальное 300x300 pixels )")
                return image
            else:
                raise ValidationError("Не удалось прочитать загруженное изображение")
        except:
            raise ValidationError("Пустое изображение.")

    class Meta:
        model = User_Closed
        fields = ('signature_example',)
        widgets = {
            'signature_example': forms.FileInput(
                attrs={'class': 'custom-file-input', 'id': 'exampleInputFile', 'accept': ".png"}
            ),
        }


class Workers_Form_UpdatePassword(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Пароль', 'id': 'password1'}))
    password2 = forms.CharField(label='Подвержение пароля', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Подвержение пароля', 'id': 'password2'}))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        return password2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ['password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password2"]
        user.set_password(password)
        if commit:
            user.save()
        return user

class Group_Form_Permissions(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Group
        fields = (
            'permissions',)
        widgets = {
            'permissions': CheckboxSelectMultiple(attrs={'class': 'checkbox-select-multiple'}),
        }
