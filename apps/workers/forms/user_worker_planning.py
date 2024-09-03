from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.workers.models import InformationMissing, InformationWeekendsHolidays, WorkerBasic, WorkersMissing, \
    WorkersMission, WorkersWeekendWork, Department, Subdivision
from apps.workobjects.models import OrganizationsObjects


class InformationMissing_Form(forms.ModelForm):
    class Meta:
        model = InformationMissing
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}),
        }


class InformationWeekendsHolidays_Form(forms.ModelForm):
    class Meta:
        model = InformationWeekendsHolidays
        fields = ['date', 'description', 'work', 'work_time']
        widgets = {
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Описание', 'id': 'description'}),
            'work': forms.CheckboxInput(
                attrs={'id': 'work', 'class': 'custom-control-input'}),
            'work_time': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Время работы', 'id': 'work_time'}),
        }

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата",
        input_formats=('%d.%m.%Y',),
        required=False
    )


class WorkersMissingManagement_Filter(forms.Form):
    date_in = forms.DateField(required=False,
                              widget=forms.DateInput(
                                  attrs={'class': 'form-control datepicker-input',
                                         'data-target': '#date_in_form',
                                         'data-inputmask-alias': 'datetime',
                                         'data-inputmask-inputformat': 'dd.mm.yyyy',
                                         'data-mask': "00.00.0000",
                                         'inputmode': "numeric"
                                         }, format='%d.%m.%Y'
                              ), label="Дата от",
                              input_formats=('%d.%m.%Y',))
    date_out = forms.DateField(required=False,
                               widget=forms.DateInput(
                                   attrs={'class': 'form-control datepicker-input',
                                          'data-target': '#date_out_form',
                                          'data-inputmask-alias': 'datetime',
                                          'data-inputmask-inputformat': 'dd.mm.yyyy',
                                          'data-mask': "00.00.0000",
                                          'inputmode': "numeric"
                                          }, format='%d.%m.%Y'
                               ), label="Дата до",
                               input_formats=('%d.%m.%Y',))

    def __init__(self, *args, **kwargs):
        user = kwargs.get('initial')['user']  # Текущий пользователь
        super().__init__(*args, **kwargs)
        # # Сортировка по управлению
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие

        filters &= Q(**{f'{"employee"}': 'employee_current'})
        QUERY_WORKERS = [(i.user.slug, i.user) for i in
                         WorkerBasic.objects.filter(filters).select_related('user',
                                                                            'actual_subdivision',
                                                                            'actual_department').only(
                             'user', 'employee', 'actual_subdivision', 'actual_department').order_by('user')]

        QUERY_WORKERS.insert(0, ('own', 'Все сотрудники'))
        self.fields['workers'] = forms.ChoiceField(label='Сотрудники',
                                                   required=False,
                                                   choices=QUERY_WORKERS,
                                                   widget=forms.Select(
                                                       attrs={'class': 'select2', 'style': 'width: 100%'}))

    def clean(self):
        try:
            self.cleaned_data['date_in']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')
        try:
            self.cleaned_data['date_out']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')

        if self.cleaned_data['date_in'] and self.cleaned_data['date_out']:
            if self.cleaned_data['date_in'] > self.cleaned_data['date_out']:
                raise ValidationError('Неправильно задан диапазон дат.')
        return self.cleaned_data['date_in']


class WorkersMissing_Subdivision_Filter(forms.Form):
    date_in = forms.DateField(required=False,
                              widget=forms.DateInput(
                                  attrs={'class': 'form-control datepicker-input',
                                         'data-target': '#date_in_form',
                                         'data-inputmask-alias': 'datetime',
                                         'data-inputmask-inputformat': 'dd.mm.yyyy',
                                         'data-mask': "00.00.0000",
                                         'inputmode': "numeric"
                                         }, format='%d.%m.%Y'
                              ), label="Дата от",
                              input_formats=('%d.%m.%Y',))
    date_out = forms.DateField(required=False,
                               widget=forms.DateInput(
                                   attrs={'class': 'form-control datepicker-input',
                                          'data-target': '#date_out_form',
                                          'data-inputmask-alias': 'datetime',
                                          'data-inputmask-inputformat': 'dd.mm.yyyy',
                                          'data-mask': "00.00.0000",
                                          'inputmode': "numeric"
                                          }, format='%d.%m.%Y'
                               ), label="Дата до",
                               input_formats=('%d.%m.%Y',))

    def __init__(self, *args, **kwargs):

        workerBasic = kwargs.get('initial')['workerBasic']  # Текущий пользователь
        user = kwargs.pop('initial')['user']  # Текущий пользователь
        super().__init__(*args, **kwargs)

        # Сортировка по управлению
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        filters &= Q(**{f'{"actual_subdivision"}': workerBasic.actual_subdivision})
        # filters &= Q(**{f'{"actual_department"}': workerBasic.actual_department})

        filters &= Q(**{f'{"employee"}': 'employee_current'})
        QUERY_WORKERS = [(i.user.slug, i.user) for i in
                         WorkerBasic.objects.filter(filters).select_related('user',
                                                                            'actual_subdivision',
                                                                            'actual_department').only(
                             'user', 'employee', 'actual_subdivision', 'actual_department').order_by('user')]

        QUERY_WORKERS.insert(0, ('own', 'Все сотрудники'))
        self.fields['workers'] = forms.ChoiceField(label='Сотрудники',
                                                   required=False,
                                                   choices=QUERY_WORKERS,
                                                   widget=forms.Select(
                                                       attrs={'class': 'select2', 'style': 'width: 100%'}))

        QUERY_DEPARTMENT = [(i.slug, i.name) for i in
                            Department.objects.all().order_by('name')]

        QUERY_DEPARTMENT.insert(0, ('own', 'Все отделы'))
        self.fields['department'] = forms.ChoiceField(label='Отделы',
                                                      required=False,
                                                      choices=QUERY_DEPARTMENT,
                                                      widget=forms.Select(
                                                          attrs={'class': 'select2', 'style': 'width: 100%'}))

    def clean(self):
        try:
            self.cleaned_data['date_in']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')
        try:
            self.cleaned_data['date_out']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')

        if self.cleaned_data['date_in'] and self.cleaned_data['date_out']:
            if self.cleaned_data['date_in'] > self.cleaned_data['date_out']:
                raise ValidationError('Неправильно задан диапазон дат.')
        return self.cleaned_data['date_in']


class WorkersMissing_Department_Filter(forms.Form):
    date_in = forms.DateField(required=False,
                              widget=forms.DateInput(
                                  attrs={'class': 'form-control datepicker-input',
                                         'data-target': '#date_in_form',
                                         'data-inputmask-alias': 'datetime',
                                         'data-inputmask-inputformat': 'dd.mm.yyyy',
                                         'data-mask': "00.00.0000",
                                         'inputmode': "numeric"
                                         }, format='%d.%m.%Y'
                              ), label="Дата от",
                              input_formats=('%d.%m.%Y',))
    date_out = forms.DateField(required=False,
                               widget=forms.DateInput(
                                   attrs={'class': 'form-control datepicker-input',
                                          'data-target': '#date_out_form',
                                          'data-inputmask-alias': 'datetime',
                                          'data-inputmask-inputformat': 'dd.mm.yyyy',
                                          'data-mask': "00.00.0000",
                                          'inputmode': "numeric"
                                          }, format='%d.%m.%Y'
                               ), label="Дата до",
                               input_formats=('%d.%m.%Y',))

    def __init__(self, *args, **kwargs):

        workerBasic = kwargs.get('initial')['workerBasic']  # Текущий пользователь
        user = kwargs.pop('initial')['user']  # Текущий пользователь
        super().__init__(*args, **kwargs)

        # Сортировка по управлению
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        filters &= Q(**{f'{"actual_subdivision"}': workerBasic.actual_subdivision})
        filters &= Q(**{f'{"actual_department"}': workerBasic.actual_department})

        filters &= Q(**{f'{"employee"}': 'employee_current'})
        QUERY_WORKERS = [(i.user.slug, i.user) for i in
                         WorkerBasic.objects.filter(filters).select_related('user',
                                                                            'actual_subdivision',
                                                                            'actual_department').only(
                             'user', 'employee', 'actual_subdivision', 'actual_department').order_by('user')]

        QUERY_WORKERS.insert(0, ('own', 'Все сотрудники'))
        self.fields['workers'] = forms.ChoiceField(label='Сотрудники',
                                                   required=False,
                                                   choices=QUERY_WORKERS,
                                                   widget=forms.Select(
                                                       attrs={'class': 'select2', 'style': 'width: 100%'}))

    def clean(self):
        try:
            self.cleaned_data['date_in']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')
        try:
            self.cleaned_data['date_out']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')

        if self.cleaned_data['date_in'] and self.cleaned_data['date_out']:
            if self.cleaned_data['date_in'] > self.cleaned_data['date_out']:
                raise ValidationError('Неправильно задан диапазон дат.')
        return self.cleaned_data['date_in']


class WorkersMissing_userHis_Filter(forms.Form):
    date_in = forms.DateField(required=False,
                              widget=forms.DateInput(
                                  attrs={'class': 'form-control datepicker-input',
                                         'data-target': '#date_in_form',
                                         'data-inputmask-alias': 'datetime',
                                         'data-inputmask-inputformat': 'dd.mm.yyyy',
                                         'data-mask': "00.00.0000",
                                         'inputmode': "numeric"
                                         }, format='%d.%m.%Y'
                              ), label="Дата от",
                              input_formats=('%d.%m.%Y',))
    date_out = forms.DateField(required=False,
                               widget=forms.DateInput(
                                   attrs={'class': 'form-control datepicker-input',
                                          'data-target': '#date_out_form',
                                          'data-inputmask-alias': 'datetime',
                                          'data-inputmask-inputformat': 'dd.mm.yyyy',
                                          'data-mask': "00.00.0000",
                                          'inputmode': "numeric"
                                          }, format='%d.%m.%Y'
                               ), label="Дата до",
                               input_formats=('%d.%m.%Y',))

    def clean(self):
        try:
            self.cleaned_data['date_in']
        except:
            raise ValidationError('Неправильный формат даты.')
        try:
            self.cleaned_data['date_out']
        except:
            raise ValidationError('Неправильный формат даты.')

        if self.cleaned_data['date_in'] and self.cleaned_data['date_out']:
            if self.cleaned_data['date_in'] > self.cleaned_data['date_out']:
                raise ValidationError('Неправильно задан диапазон дат.')
        return self.cleaned_data['date_in']


class WorkersMissing_Control(forms.ModelForm):
    workerBasic = None
    userRight = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['user'].empty_label = "Сотрудник"
        # self.fields['information_missing'].empty_label = "Причина отсутствия"
        # self.workerBasic = kwargs['initial']['workerBasic']
        # self.userRight = kwargs['initial']['userRight']
        # self.fields['user'].queryset = WorkerBasic.objects.filter(
        #     actual_subdivision=self.workerBasic.actual_subdivision,
        #     actual_department=self.workerBasic.actual_department, employee='employee_current').order_by('user')

    class Meta:
        model = WorkersMissing
        fields = ['user', 'information_missing', 'date_start', 'date_end', 'comments']
        widgets = {
            'user': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'information_missing': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'comments': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Коментарии', 'id': 'comments'}),
        }

    date_start = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата от",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата до",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end_save = None
    #
    # def clean_date_end(self):
    #     date_start = self.cleaned_data['date_start']
    #     date_end = self.cleaned_data['date_end']
    #     self.date_end_save = date_end  # Ошибка передачи поля в clean
    #     if date_start > date_end:
    #         raise ValidationError('Дата начала отсутствия не может быть больше даты окончания отсутствия.')
    #     """Максимальный срок отсутствия"""
    #     if (date_end - date_start).days > 90:
    #         raise ValidationError('Максимальный срок отсутствия 90 дней.')
    #     return date_end
    #
    # def clean(self):
    #     date_start = self.cleaned_data['date_start']
    #     date_end = self.cleaned_data['date_end']
    #     workers = self.cleaned_data['user']
    #
    #     """ Проверка на Отсутствие"""
    #     missings = WorkersMissing.objects.filter(date_start__gte=date_start - relativedelta(months=6),
    #                                              date_end__lte=date_end + relativedelta(months=6), user=workers)
    #
    #     for missing in missings:
    #         """Если даты попадают в диапазон"""
    #         if date_start >= missing.date_start and date_start <= missing.date_end or date_end >= missing.date_start and date_end <= missing.date_end:
    #             raise ValidationError(
    #                 '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
    #                                                                         missing.date_end,
    #                                                                         missing.information_missing))
    #         if date_start < missing.date_start and date_end > missing.date_end:
    #             raise ValidationError(
    #                 '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
    #                                                                         missing.date_end,
    #                                                                         missing.information_missing))
    #     """ Проверка на командировки"""
    #     missions = WorkersMission.objects.filter(date_start__gte=date_start - relativedelta(months=6),
    #                                              date_end__lte=date_end + relativedelta(months=6), user=workers)
    #     for mission in missions:
    #         """Если даты попадают в диапазон"""
    #         if date_start >= mission.date_departure and date_start <= mission.date_arrival or date_end >= mission.date_departure and date_start <= mission.date_arrival:
    #             raise ValidationError(
    #                 '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
    #                                                                             mission.date_arrival,
    #                                                                             mission.organizations_objects))
    #         if date_start < mission.date_departure and date_end > mission.date_arrival:
    #             raise ValidationError(
    #                 '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
    #                                                                             mission.date_arrival,
    #                                                                             mission.organizations_objects))
    #


class WorkersMissing_Subdivision_Control(forms.ModelForm):
    workerBasic = None
    pk = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user'].empty_label = "Сотрудник"
        self.fields['information_missing'].empty_label = "Причина отсутствия"
        self.workerBasic = kwargs['initial']['workerBasic']
        try:
            self.pk = kwargs['initial']['pk']
        except:
            pass
        self.fields['user'].queryset = WorkerBasic.objects.filter(
            actual_subdivision=self.workerBasic.actual_subdivision, employee='employee_current').order_by('user')

    class Meta:
        model = WorkersMissing
        fields = ['user', 'information_missing', 'date_start', 'date_end', 'comments']
        widgets = {
            'user': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'information_missing': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'comments': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Коментарии', 'id': 'comments'}),
        }

    date_start = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата от",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата до",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end_save = None

    def clean_date_end(self):
        date_start = self.cleaned_data['date_start']
        date_end = self.cleaned_data['date_end']
        self.date_end_save = date_end  # Ошибка передачи поля в clean
        if date_start > date_end:
            raise ValidationError('Дата начала отсутствия не может быть больше даты окончания отсутствия.')
        """Максимальный срок отсутствия"""
        if (date_end - date_start).days > 90:
            raise ValidationError('Максимальный срок отсутствия 90 дней.')
        return date_end

    def clean(self):
        date_start = self.cleaned_data['date_start']
        date_end = self.date_end_save
        workers = self.cleaned_data['user']
        """ Проверка на Отсутствие"""
        if self.pk:
            queriesMissings = Q(date_start__gte=date_start - relativedelta(months=6)) & \
                              Q(date_end__lte=date_end + relativedelta(months=6)) & Q(user=workers) & ~Q(pk=self.pk)
        else:
            queriesMissings = Q(date_start__gte=date_start - relativedelta(months=6)) & \
                              Q(date_end__lte=date_end + relativedelta(months=6)) & Q(user=workers)
        missings = WorkersMissing.objects.filter(queriesMissings)

        for missing in missings:
            """Если даты попадают в диапазон"""
            if date_start >= missing.date_start and date_start <= missing.date_end or date_end >= missing.date_start and date_end <= missing.date_end:
                raise ValidationError(
                    '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
                                                                            missing.date_end,
                                                                            missing.information_missing))
            if date_start < missing.date_start and date_end > missing.date_end:
                raise ValidationError(
                    '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
                                                                            missing.date_end,
                                                                            missing.information_missing))
        """ Проверка на командировки"""
        missions = WorkersMission.objects.filter(date_start__gte=date_start - relativedelta(months=6),
                                                 date_end__lte=date_end + relativedelta(months=6), user=workers)
        for mission in missions:
            """Если даты попадают в диапазон"""
            if date_start >= mission.date_departure and date_start <= mission.date_arrival or date_end >= mission.date_departure and date_start <= mission.date_arrival:
                raise ValidationError(
                    '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
                                                                                mission.date_arrival,
                                                                                mission.organizations_objects))
            if date_start < mission.date_departure and date_end > mission.date_arrival:
                raise ValidationError(
                    '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
                                                                                mission.date_arrival,
                                                                                mission.organizations_objects))


class WorkersMissing_Department_Control(forms.ModelForm):
    workerBasic = None
    pk = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user'].empty_label = "Сотрудник"
        self.fields['information_missing'].empty_label = "Причина отсутствия"
        self.workerBasic = kwargs['initial']['workerBasic']
        try:
            self.pk = kwargs['initial']['pk']
        except:
            pass
        self.fields['user'].queryset = WorkerBasic.objects.filter(
            actual_subdivision=self.workerBasic.actual_subdivision,
            actual_department=self.workerBasic.actual_department, employee='employee_current').order_by('user')

    class Meta:
        model = WorkersMissing
        fields = ['user', 'information_missing', 'date_start', 'date_end', 'comments']
        widgets = {
            'user': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'information_missing': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'comments': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Коментарии', 'id': 'comments'}),
        }

    date_start = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата от",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата до",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end_save = None

    def clean_date_end(self):
        date_start = self.cleaned_data['date_start']
        date_end = self.cleaned_data['date_end']
        self.date_end_save = date_end  # Ошибка передачи поля в clean
        if date_start > date_end:
            raise ValidationError('Дата начала отсутствия не может быть больше даты окончания отсутствия.')
        """Максимальный срок отсутствия"""
        if (date_end - date_start).days > 90:
            raise ValidationError('Максимальный срок отсутствия 90 дней.')
        return date_end

    def clean(self):
        date_start = self.cleaned_data['date_start']
        date_end = self.date_end_save
        workers = self.cleaned_data['user']
        """ Проверка на Отсутствие"""
        if self.pk:
            queriesMissings = Q(date_start__gte=date_start - relativedelta(months=6)) & \
                              Q(date_end__lte=date_end + relativedelta(months=6)) & Q(user=workers) & ~Q(pk=self.pk)
        else:
            queriesMissings = Q(date_start__gte=date_start - relativedelta(months=6)) & \
                              Q(date_end__lte=date_end + relativedelta(months=6)) & Q(user=workers)
        missings = WorkersMissing.objects.filter(queriesMissings)

        for missing in missings:
            """Если даты попадают в диапазон"""
            if date_start >= missing.date_start and date_start <= missing.date_end or date_end >= missing.date_start and date_end <= missing.date_end:
                raise ValidationError(
                    '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
                                                                            missing.date_end,
                                                                            missing.information_missing))
            if date_start < missing.date_start and date_end > missing.date_end:
                raise ValidationError(
                    '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
                                                                            missing.date_end,
                                                                            missing.information_missing))
        """ Проверка на командировки"""
        missions = WorkersMission.objects.filter(date_start__gte=date_start - relativedelta(months=6),
                                                 date_end__lte=date_end + relativedelta(months=6), user=workers)
        for mission in missions:
            """Если даты попадают в диапазон"""
            if date_start >= mission.date_departure and date_start <= mission.date_arrival or date_end >= mission.date_departure and date_start <= mission.date_arrival:
                raise ValidationError(
                    '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
                                                                                mission.date_arrival,
                                                                                mission.organizations_objects))
            if date_start < mission.date_departure and date_end > mission.date_arrival:
                raise ValidationError(
                    '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
                                                                                mission.date_arrival,
                                                                                mission.organizations_objects))


class WorkersMissing_UserHis_Control(forms.ModelForm):
    workerBasic = None
    date_start_save = None
    date_end_save = None
    pk = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workerBasic = kwargs['initial']['workerBasic']
        self.fields['information_missing'].empty_label = "Причина отсутствия"
        try:
            self.pk = kwargs['initial']['pk']
        except:
            pass

    class Meta:
        model = WorkersMissing
        fields = ['information_missing', 'date_start', 'date_end', 'comments']
        widgets = {
            'information_missing': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'comments': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Коментарии', 'id': 'comments'}),
        }

    date_start = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата от",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата до",
        input_formats=('%d.%m.%Y',),
        required=False
    )

    def clean_date_start(self):
        self.date_start_save = self.cleaned_data['date_start']
        if not self.date_start_save:
            raise ValidationError('Дата начала отсутствия.')
        return self.date_start_save

    def clean_date_end(self):
        date_start = self.date_start_save
        self.date_end_save = self.cleaned_data['date_end']
        if self.date_end_save:
            if date_start:
                self.date_end_save = self.date_end_save  # Ошибка передачи поля в clean
                if date_start > self.date_end_save:
                    raise ValidationError('Дата начала отсутствия не может быть больше даты окончания отсутствия.')
                """Максимальный срок отсутствия"""
                if (self.date_end_save - date_start).days > 90:
                    raise ValidationError('Максимальный срок отсутствия 90 дней.')
        else:
            raise ValidationError('Дата окончания не указана.')
        return self.date_end_save

    def clean(self):
        date_start = self.date_start_save
        date_end = self.date_end_save
        if date_start and date_end:
            """ Проверка на Отсутствие"""
            if self.pk:
                queriesMissings = Q(date_start__gte=date_start - relativedelta(months=6)) & \
                                  Q(date_end__lte=date_end + relativedelta(months=6)) & Q(user=self.workerBasic) & ~Q(
                    pk=self.pk)
            else:
                queriesMissings = Q(date_start__gte=date_start - relativedelta(months=6)) & \
                                  Q(date_end__lte=date_end + relativedelta(months=6)) & Q(user=self.workerBasic)
            missings = WorkersMissing.objects.filter(queriesMissings)
            for missing in missings:
                """Если даты попадают в диапазон"""
                if date_start >= missing.date_start and date_start <= missing.date_end or \
                        date_end >= missing.date_start and date_end <= missing.date_end:
                    raise ValidationError(
                        '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(str(self.workerBasic.user),
                                                                                missing.date_start,
                                                                                missing.date_end,
                                                                                missing.information_missing))
                if date_start < missing.date_start and date_end > missing.date_end:
                    raise ValidationError(
                        '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(str(self.workerBasic.user),
                                                                                missing.date_start,
                                                                                missing.date_end,
                                                                                missing.information_missing))
            """ Проверка на командировки"""
            missions = WorkersMission.objects.filter(date_start__gte=date_start - relativedelta(months=6),
                                                     date_end__lte=date_end + relativedelta(months=6),
                                                     user=self.workerBasic)
            for mission in missions:
                """Если даты попадают в диапазон"""
                if date_start >= mission.date_departure and date_start <= mission.date_arrival or \
                        date_end >= mission.date_departure and date_start <= mission.date_arrival:
                    raise ValidationError(
                        '{0} уже в командировке с {1} по {2} на объекте {3}'.format(str(self.workerBasic.user),
                                                                                    mission.date_departure,
                                                                                    mission.date_arrival,
                                                                                    mission.organizations_objects))
                if date_start < mission.date_departure and date_end > mission.date_arrival:
                    raise ValidationError(
                        '{0} уже в командировке с {1} по {2} на объекте {3}'.format(str(self.workerBasic.user),
                                                                                    mission.date_departure,
                                                                                    mission.date_arrival,
                                                                                    mission.organizations_objects))
        else:
            raise ValidationError('Проблема с датами.')


class WorkersWeekendWork_Control(forms.ModelForm):
    user_current = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].empty_label = "Сотрудник"
        self.user_current = kwargs['initial']['user_current']
        self.fields['user'].queryset = WorkerBasic.objects.filter(
            actual_subdivision=self.user_current.actual_subdivision,
            actual_department=self.user_current.actual_department, employee='employee_current').order_by('user')

    class Meta:
        model = WorkersWeekendWork
        fields = ['user', 'planning', 'date', ]
        widgets = {
            'user': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'planning': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Планирование работ', 'id': 'planning'}),
        }

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_save = None

    def clean_date(self):
        date = self.cleaned_data['date']
        self.date_save = date
        try:
            weekend = InformationWeekendsHolidays.objects.get(date=date)
            if not weekend.work:
                return date
        except:
            pass
        print(date.weekday())
        if date.weekday() < 5 or date.weekday() > 6:
            raise ValidationError('{0} Данный день не является выходным или праздником '.format(date))
        return date

    def clean(self):
        date = self.date_save
        workers = self.cleaned_data['user']

        """ Проверка на Отсутствие"""
        missings = WorkersMissing.objects.filter(date_start__gte=date - relativedelta(months=6),
                                                 date_end__lte=date + relativedelta(months=6), user=workers)

        for missing in missings:
            """Если даты попадают в диапазон"""
            if date >= missing.date_start and date <= missing.date_end:
                raise ValidationError(
                    '{0} уже отсутствует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
                                                                             missing.date_end,
                                                                             missing.information_missing))

        """ Проверка на командировки"""
        missions = WorkersMission.objects.filter(date_start__gte=date - relativedelta(months=6),
                                                 date_end__lte=date + relativedelta(months=6), user=workers)
        for mission in missions:
            """Если даты попадают в диапазон"""
            if date >= mission.date_departure and date <= mission.date_arrival:
                raise ValidationError(
                    '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
                                                                                mission.date_arrival,
                                                                                mission.organizations_objects))
        """Проверка на аналогичную запись"""

        weekendWork = WorkersWeekendWork.objects.filter(user=workers, date=date)
        if weekendWork.exists():
            raise ValidationError(
                '{0} данный сотрудник {1} уже записан'.format(workers, date))


class WorkersWeekendWork_Time_Control(forms.ModelForm):
    class Meta:
        model = WorkersWeekendWork
        fields = ['hours_working', ]
        widgets = {
            'hours_working': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Отработанное время', 'id': 'hours_working'}),
        }

    def clean_hours_working(self):
        hours_working = self.cleaned_data['hours_working']
        print(type(hours_working))
        if hours_working < -1 or hours_working > 8.25:
            print(hours_working)
            raise ValidationError('Рабочее время не должно превышать 8.25. -1 Сотрудник не вышел.')

        return hours_working


class WorkersMission_Form_Filter(forms.Form):
    date_in = forms.DateField(required=False,
                              widget=forms.DateInput(
                                  attrs={'class': 'form-control datepicker-input',
                                         'data-target': '#date_in_form',
                                         'data-inputmask-alias': 'datetime',
                                         'data-inputmask-inputformat': 'dd.mm.yyyy',
                                         'data-mask': "00.00.0000",
                                         'inputmode': "numeric"
                                         }, format='%d.%m.%Y'
                              ), label="Дата от",
                              input_formats=('%d.%m.%Y',))
    date_out = forms.DateField(required=False,
                               widget=forms.DateInput(
                                   attrs={'class': 'form-control datepicker-input',
                                          'data-target': '#date_out_form',
                                          'data-inputmask-alias': 'datetime',
                                          'data-inputmask-inputformat': 'dd.mm.yyyy',
                                          'data-mask': "00.00.0000",
                                          'inputmode': "numeric"
                                          }, format='%d.%m.%Y'
                               ), label="Дата до",
                               input_formats=('%d.%m.%Y',))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial')['user']  # Текущий пользователь
        super().__init__(*args, **kwargs)

        ORGANIZATION = [(i.organization.slug, "{1}. {0}.".format(i.name, i.organization)) for i in
                        OrganizationsObjects.objects.all().select_related('organization')]
        ORGANIZATION.insert(0, ('own', 'Все объекты'))
        self.fields['objects'] = forms.ChoiceField(label='Объекты',
                                                   required=False,
                                                   choices=ORGANIZATION,
                                                   widget=forms.Select(
                                                       attrs={'class': 'select2', 'style': 'width: 100%'}))

        # Сортировка по управлению
        if user:

            QUERY_WORKERS = [(i.user.slug, i.user) for i in
                             WorkerBasic.objects.filter(employee='employee_current',
                                                        actual_subdivision=user.actual_subdivision,
                                                        actual_department=user.actual_department).select_related('user',
                                                                                                                 'actual_subdivision',
                                                                                                                 'actual_department').only(
                                 'user', 'employee', 'actual_subdivision', 'actual_department').order_by('user')]
        else:
            QUERY_WORKERS = [(i.user.slug, i.user) for i in
                             WorkerBasic.objects.filter(employee='employee_current', ).select_related('user',
                                                                                                      'actual_subdivision',
                                                                                                      'actual_department').only(
                                 'user', 'employee', 'actual_subdivision', 'actual_department').order_by('-user')]

        QUERY_WORKERS.insert(0, ('own', 'Все сотрудники'))
        self.fields['workers'] = forms.ChoiceField(label='Сотрудники',
                                                   required=False,
                                                   choices=QUERY_WORKERS,
                                                   widget=forms.Select(
                                                       attrs={'class': 'select2', 'style': 'width: 100%'}))

    def clean(self):
        try:
            self.cleaned_data['date_in']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')
        try:
            self.cleaned_data['date_out']
        except Exception as e:
            raise ValidationError('Неправильный формат даты.')

        if self.cleaned_data['date_in'] and self.cleaned_data['date_out']:
            if self.cleaned_data['date_in'] > self.cleaned_data['date_out']:
                raise ValidationError('Неправильно задан диапазон дат.')
        return self.cleaned_data['date_in']


class WorkersMission_Form_Add(forms.ModelForm):
    user_current = None
    workerBasic_current = None
    pk = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].empty_label = "Сотрудник"
        self.fields['organizations_objects'].empty_label = "Объект командировки"
        self.user_current = kwargs['initial']['user_current']
        self.workerBasic_current = kwargs['initial']['workerBasic_current']

        print(self.user_current)
        # if self.user_current.has_perm('workers.WorkersMission_view_all'):
        #     self.fields['user'].queryset = WorkerBasic.objects.filter(employee='employee_current').order_by('user')
        # else:
        #     if self.user_current:
        #         subdivision = False
        #         department = False
        #         if self.request.user.has_perm('workers.WorkersMission_view_subdivision'):
        #             subdivision = True
        #         if not subdivision and self.request.user.has_perm('workers.WorkersMission_view') :
        #             department = True
        #         if department and not subdivision:
        #             self.fields['user'].queryset = WorkerBasic.objects.filter(
        #                 actual_subdivision=self.user_current.actual_subdivision,
        #                 actual_department=self.user_current.actual_department, employee='employee_current').order_by(
        #                 'user')
        #         if subdivision:
        #             self.fields['user'].queryset = WorkerBasic.objects.filter(
        #                 actual_subdivision=self.user_current.actual_subdivision, employee='employee_current').order_by(
        #                 'user')
        #     else:
        #         self.fields['user'].queryset = WorkerBasic.objects.filter(
        #             actual_subdivision=self.user_current.actual_subdivision,
        #             actual_department=self.user_current.actual_department, employee='employee_current').order_by('user')

    class Meta:
        model = WorkersMission

        fields = ['user', 'organizations_objects', 'date_departure', 'date_start', 'date_end', 'date_arrival', 'status']
        widgets = {
            'user': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'organizations_objects': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'status': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
        }

    date_departure = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата выезда",
        input_formats=('%d.%m.%Y',),
        required=False
    )

    date_start = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата начала работы",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата окончание работы",
        input_formats=('%d.%m.%Y',),
        required=False
    )

    date_arrival = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата прибытия",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_departure_save = None
    date_start_save = None
    date_end_save = None
    date_arrival_save = None

    def clean_date_start(self):
        self.date_start_save = self.cleaned_data['date_start']
        self.date_departure_save = self.cleaned_data['date_departure']
        if type(self.date_start_save) == date:
            if self.date_departure_save > self.date_start_save:
                raise ValidationError('Дата выезда не должна раньше начала работ ')
        return self.date_start_save

    def clean_date_end(self):
        self.date_end_save = self.cleaned_data['date_end']
        if self.date_start_save and self.date_end_save:
            if type(self.date_start_save) == date:
                if self.date_start_save > self.date_end_save:
                    raise ValidationError('Дата окончание работы не должна быть раньше даты начала работ.')
        if self.date_end_save:
            if type(self.date_end_save) == date:
                if self.date_departure_save > self.date_end_save:
                    raise ValidationError('Дата окончание работы не должна быть раньше дате окончание работ.')
        return self.date_end_save

    def clean_date_arrival(self):
        self.date_arrival_save = self.cleaned_data['date_arrival']
        if type(self.date_end_save) == date:
            if self.date_end_save > self.date_arrival_save:
                raise ValidationError('Дата прибытия не должна быть раньше дате окончание работ.')
        if type(self.date_start_save) == date:
            if self.date_start_save > self.date_arrival_save:
                raise ValidationError('Дата начала работ не должна быть раньше дате окончание работ.')
        if self.date_departure_save > self.date_arrival_save:
            raise ValidationError('Дата выезда не должна быть раньше дате окончание работ.')
        return self.date_arrival_save

    def clean(self):
        workers = self.cleaned_data['user']
        """ Проверка на Отсутствие"""
        # missings = WorkersMissing.objects.filter(date_start__gte=self.date_departure_save - relativedelta(months=6),
        #                                          date_end__lte=self.date_arrival_save + relativedelta(months=6),
        #                                          user=workers)
        # for missing in missings:
        #     """Если даты попадают в диапазон"""
        #     if self.date_departure_save >= missing.date_start and self.date_departure_save <= missing.date_end or self.date_arrival_save >= missing.date_start and self.date_arrival_save <= missing.date_end:
        #         raise ValidationError(
        #             '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
        #                                                                     missing.date_end,
        #                                                                     missing.information_missing))
        #
        #     if self.date_departure_save < missing.date_start and self.date_arrival_save > missing.date_end:
        #         raise ValidationError(
        #             '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
        #                                                                     missing.date_end,
        #                                                                     missing.information_missing))
        # """ Проверка на командировки"""
        # missions = WorkersMission.objects.filter(date_departure__gte=self.date_departure_save - relativedelta(months=6),
        #                                          date_arrival__lte=self.date_arrival_save + relativedelta(months=6),
        #                                          user=workers).exclude(pk=self.pk)
        #
        # for mission in missions:
        #     """Если даты попадают в диапазон"""
        #     if self.date_departure_save >= mission.date_departure and self.date_departure_save <= mission.date_arrival or \
        #             self.date_arrival_save >= mission.date_departure and self.date_arrival_save <= mission.date_arrival:
        #         raise ValidationError(
        #             '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
        #                                                                         mission.date_arrival,
        #                                                                         mission.organizations_objects))
        #     if self.date_departure_save < mission.date_start and self.date_arrival_save > mission.date_end:
        #         print('error')
        #         raise ValidationError(
        #             '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
        #                                                                         mission.date_arrival,
        #                                                                         mission.organizations_objects))


class WorkersMission_Form_Change(forms.ModelForm):
    user_current = None
    pk = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].empty_label = "Сотрудник"
        self.fields['organizations_objects'].empty_label = "Объект командировки"
        self.user_current = kwargs['initial']['user_current']

        self.fields['user'].queryset = WorkerBasic.objects.filter(
            actual_subdivision=self.user_current.actual_subdivision,
            actual_department=self.user_current.actual_department, employee='employee_current').order_by('user')
        try:
            self.pk = kwargs['initial']['pk']
        except Exception as e:
            pass

    class Meta:
        model = WorkersMission

        fields = ['user', 'organizations_objects', 'date_departure', 'date_start', 'date_end', 'date_arrival', 'status']
        widgets = {
            'user': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'organizations_objects': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
            'status': forms.Select(
                attrs={'class': 'select2', 'style': 'width: 100%'}),
        }

    date_departure = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата выезда",
        input_formats=('%d.%m.%Y',),
        required=False
    )

    date_start = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата начала работы",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_end = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата окончание работы",
        input_formats=('%d.%m.%Y',),
        required=False
    )

    date_arrival = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control datepicker-input',
                   'data-target': '#date_form',
                   'data-inputmask-alias': 'datetime',
                   'data-inputmask-inputformat': 'dd.mm.yyyy',
                   'data-mask': "00.00.0000",
                   'inputmode': "numeric"
                   }, format='%d.%m.%Y'
        ), label="Дата прибытия",
        input_formats=('%d.%m.%Y',),
        required=False
    )
    date_departure_save = None
    date_start_save = None
    date_end_save = None
    date_arrival_save = None

    def clean_date_start(self):
        self.date_start_save = self.cleaned_data['date_start']
        self.date_departure_save = self.cleaned_data['date_departure']
        if type(self.date_start_save) == date:
            if self.date_departure_save > self.date_start_save:
                raise ValidationError('Дата выезда не должна раньше начала работ ')
        return self.date_start_save

    def clean_date_end(self):
        self.date_end_save = self.cleaned_data['date_end']
        if self.date_start_save and self.date_end_save:
            if type(self.date_start_save) == date:
                if self.date_start_save > self.date_end_save:
                    raise ValidationError('Дата окончание работы не должна быть раньше даты начала работ.')
        if self.date_end_save:
            if type(self.date_end_save) == date:
                if self.date_departure_save > self.date_end_save:
                    raise ValidationError('Дата окончание работы не должна быть раньше дате окончание работ.')
        return self.date_end_save

    def clean_date_arrival(self):
        self.date_arrival_save = self.cleaned_data['date_arrival']
        if type(self.date_end_save) == date:
            if self.date_end_save > self.date_arrival_save:
                raise ValidationError('Дата прибытия не должна быть раньше дате окончание работ.')
        if type(self.date_start_save) == date:
            if self.date_start_save > self.date_arrival_save:
                raise ValidationError('Дата начала работ не должна быть раньше дате окончание работ.')
        if self.date_departure_save > self.date_arrival_save:
            raise ValidationError('Дата выезда не должна быть раньше дате окончание работ.')
        return self.date_arrival_save

    def clean(self):
        workers = self.cleaned_data['user']
        """ Проверка на Отсутствие"""
        # missings = WorkersMissing.objects.filter(date_start__gte=self.date_departure_save - relativedelta(months=6),
        #                                          date_end__lte=self.date_arrival_save + relativedelta(months=6),
        #                                          user=workers)
        # for missing in missings:
        #     """Если даты попадают в диапазон"""
        #     if self.date_departure_save >= missing.date_start and self.date_departure_save <= missing.date_end or self.date_arrival_save >= missing.date_start and self.date_arrival_save <= missing.date_end:
        #         raise ValidationError(
        #             '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
        #                                                                     missing.date_end,
        #                                                                     missing.information_missing))
        #
        #     if self.date_departure_save < missing.date_start and self.date_arrival_save > missing.date_end:
        #         raise ValidationError(
        #             '{0} уже отсутсвует с {1} по {2} по причине {3}'.format(workers, missing.date_start,
        #                                                                     missing.date_end,
        #                                                                     missing.information_missing))
        # """ Проверка на командировки"""
        # missions = WorkersMission.objects.filter(date_departure__gte=self.date_departure_save - relativedelta(months=6),
        #                                          date_arrival__lte=self.date_arrival_save + relativedelta(months=6),
        #                                          user=workers).exclude(pk=self.pk)
        #
        # for mission in missions:
        #     """Если даты попадают в диапазон"""
        #     if self.date_departure_save >= mission.date_departure and self.date_departure_save <= mission.date_arrival or \
        #             self.date_arrival_save >= mission.date_departure and self.date_arrival_save <= mission.date_arrival:
        #         raise ValidationError(
        #             '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
        #                                                                         mission.date_arrival,
        #                                                                         mission.organizations_objects))
        #     if self.date_departure_save < mission.date_start and self.date_arrival_save > mission.date_end:
        #         print('error')
        #         raise ValidationError(
        #             '{0} уже в командировке с {1} по {2} на объекте {3}'.format(workers, mission.date_departure,
        #                                                                         mission.date_arrival,
        #                                                                         mission.organizations_objects))


class Planning_Filter(forms.Form):
    def clean_month(self):
        month = self.cleaned_data['month']
        try:
            if self.cleaned_data['month']:
                month = int(month)
                if month > 12:
                    raise ValidationError('Уменьшите месяц.')
                if month < 1:
                    raise ValidationError('Увеличьте месяц.')
        except Exception as e:
            raise ValidationError('Неправильный формат месяца.')
        return month

    def clean_length(self):
        length = self.cleaned_data['length']
        try:
            if length != None:
                length = int(length)
                if length > 12:
                    raise ValidationError('Очень большая протяженность месяцев. Максимум 12 месяцев.')
                if length < 1:
                    raise ValidationError('Очень маленькая протяженность месяцев. Минимум 1 месяц.')
        except Exception as e:
            raise ValidationError('Неправильный формат месяца. Доступный диапазон 1 - 12 месяцев.')
        return length

    def clean_year(self):
        year = self.cleaned_data['year']
        try:
            if self.cleaned_data['year']:
                year = int(year)
                if year > 2100:
                    raise ValidationError('Уменьшите год.')
                if year < 1980:
                    raise ValidationError('Увеличьте год.')
        except Exception as e:
            raise ValidationError('Неправильный формат года.')
        return year


class Planning_Managment_Filter(Planning_Filter):
    """Форма для поиска."""

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial')['user']  # Текущий пользователь
        super().__init__(*args, **kwargs)
        self.fields['length'] = forms.IntegerField(label='Протяженность месяцев', required=False,
                                                   widget=forms.NumberInput(
                                                       attrs={'class': 'form-control',
                                                              'placeholder': 'Протяженность месяцев', 'id': 'length'}))
        self.fields['year'] = forms.IntegerField(label='Год', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Год', 'id': 'year'}))
        self.fields['month'] = forms.IntegerField(label='Месяц', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Месяц', 'id': 'month'}))
        # Сортировка по управлению

        QUERY_SUBDIVISION = [(i.slug, i.abbreviation) for i in
                             Subdivision.objects.all().order_by('name')]

        QUERY_SUBDIVISION.insert(0, ('own', 'Все Управления'))
        self.fields['subdivision'] = forms.ChoiceField(label='Отделы',
                                                       required=False,
                                                       choices=QUERY_SUBDIVISION,
                                                       widget=forms.Select(
                                                           attrs={'class': 'select2', 'style': 'width: 100%'}))
        # Сортировка по отделам
        QUERY_DEPARTMENT = [(i.slug, i.abbreviation) for i in
                            Department.objects.all().order_by('name')]

        QUERY_DEPARTMENT.insert(0, ('own', 'Все отделы'))
        self.fields['department'] = forms.ChoiceField(label='Отделы',
                                                      required=False,
                                                      choices=QUERY_DEPARTMENT,
                                                      widget=forms.Select(
                                                          attrs={'class': 'select2', 'style': 'width: 100%'}))




class Planning_Subdivision_Filter(Planning_Filter):
    """Форма для поиска."""

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial')['user']  # Текущий пользователь
        super().__init__(*args, **kwargs)
        self.fields['length'] = forms.IntegerField(label='Протяженность месяцев', required=False,
                                                   widget=forms.NumberInput(
                                                       attrs={'class': 'form-control',
                                                              'placeholder': 'Протяженность месяцев', 'id': 'length'}))
        self.fields['year'] = forms.IntegerField(label='Год', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Год', 'id': 'year'}))
        self.fields['month'] = forms.IntegerField(label='Месяц', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Месяц', 'id': 'month'}))
        # Сортировка по управлению

        QUERY_DEPARTMENT = [(i.slug, i.name) for i in
                            Department.objects.all().order_by('name')]

        QUERY_DEPARTMENT.insert(0, ('own', 'Все отделы'))
        self.fields['department'] = forms.ChoiceField(label='Отделы',
                                                      required=False,
                                                      choices=QUERY_DEPARTMENT,
                                                      widget=forms.Select(
                                                          attrs={'class': 'select2', 'style': 'width: 100%'}))



class Planning_Department_Filter(Planning_Filter):
    """Форма для поиска."""

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial')['user']  # Текущий пользователь
        super().__init__(*args, **kwargs)
        self.fields['length'] = forms.IntegerField(label='Протяженность месяцев', required=False,
                                                   widget=forms.NumberInput(
                                                       attrs={'class': 'form-control',
                                                              'placeholder': 'Протяженность месяцев', 'id': 'length'}))
        self.fields['year'] = forms.IntegerField(label='Год', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Год', 'id': 'year'}))
        self.fields['month'] = forms.IntegerField(label='Месяц', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Месяц', 'id': 'month'}))

        # Сортировка по управлению
        if user:
            QUERY_WORKERS = [(i.user.slug, i.user) for i in
                             WorkerBasic.objects.filter(employee='employee_current',
                                                        actual_subdivision=user.actual_subdivision,
                                                        actual_department=user.actual_department).select_related('user',
                                                                                                                 'actual_subdivision',
                                                                                                                 'actual_department').only(
                                 'user', 'employee', 'actual_subdivision', 'actual_department').order_by('user')]


        else:
            QUERY_WORKERS = [(i.user.slug, i.user) for i in
                             WorkerBasic.objects.filter(employee='employee_current', ).select_related('user',
                                                                                                      'actual_subdivision',
                                                                                                      'actual_department').only(
                                 'user', 'employee', 'actual_subdivision', 'actual_department').order_by('user')]

        QUERY_WORKERS.insert(0, ('own', 'Все сотрудники'))
        self.fields['workers'] = forms.ChoiceField(label='Сотрудники',
                                                   required=False,
                                                   choices=QUERY_WORKERS,
                                                   widget=forms.Select(
                                                       attrs={'class': 'select2', 'style': 'width: 100%'}))


class Planning_His_Filter(Planning_Filter):
    """Форма для поиска."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['length'] = forms.IntegerField(label='Протяженность месяцев', required=False,
                                                   widget=forms.NumberInput(
                                                       attrs={'class': 'form-control',
                                                              'placeholder': 'Протяженность месяцев', 'id': 'length'}))
        self.fields['year'] = forms.IntegerField(label='Год', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Год', 'id': 'year'}))
        self.fields['month'] = forms.IntegerField(label='Месяц', required=False, widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Месяц', 'id': 'month'}))
