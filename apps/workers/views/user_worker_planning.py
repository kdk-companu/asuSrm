from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.defaultfilters import addslashes
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, CreateView, TemplateView
from dateutil.relativedelta import relativedelta
from transliterate.utils import _

from apps.workers.forms import InformationMissing_Form, Planning_Filter, InformationWeekendsHolidays_Form, \
    WorkersMissing_Control, WorkersMissing_Filter, WorkersWeekendWork_Control, WorkersWeekendWork_Time_Control, \
    WorkersMission_Form_Filter, WorkersMission_Form_Add, Planning_Department_Filter, Planning_Subdivision_Filter, \
    WorkersMissing_userHis_Filter, WorkersMissing_UserHis_Control, WorkersMissing_Department_Control, \
    WorkersMissing_Department_Filter, WorkersMissing_Subdivision_Filter
from apps.workers.models import InformationMissing, InformationWeekendsHolidays, WorkerBasic, WorkersMissing, Worker, \
    Subdivision, WorkersWeekendWork, WorkersMission
import datetime

from library.table import Table
from mixin.workers_right import WorkerPermissionsBased, WorkerPlaningPermissionsViewMixin, \
    WorkerPlaningSubdivisionPermissionsViewMixin, WorkerPlaningDepartmentPermissionsViewMixin, \
    WorkerMissingPermissionsViewMixin, WorkerMissingSubdivisionPermissionsViewMixin, \
    WorkerMissingDepartmentPermissionsViewMixin, WorkerMissingUpdateDepartmentPermissionsViewMixin, \
    WorkerMissingHisPermissionsUpdateMixin

#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class InformationMissing_View(LoginRequiredMixin, WorkerPermissionsBased, ListView):
    """Причины отсутствия на работе."""
    model = InformationMissing
    template_name = 'user/worker/planning/informationmissing_view.html'
    context_object_name = 'informationMissings'
    login_url = 'login'
    permission_required = 'workers.InformationMissing_view'

    def get(self, *args, **kwargs):
        if self.request.user.has_perm('workers.InformationMissing_delete'):
            query = self.request.GET.get('remove')
            if query != None:
                try:
                    remove = InformationMissing.objects.get(slug=query)
                    remove.delete()
                except:
                    pass
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Причина отсутствия на работе'
        return context

#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class InformationMissing_Add(LoginRequiredMixin, WorkerPermissionsBased, CreateView):
    """Причины отсутствия на работе."""
    model = InformationMissing
    template_name = 'user/worker/planning/informationmissing_control.html'
    form_class = InformationMissing_Form
    success_url = reverse_lazy('informationmissing')
    login_url = 'login'
    permission_required = 'workers.InformationMissing_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить причину отсутствия на работе'
        context['title_page'] = 'Добавить'
        return context

#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class InformationMissing_Update(LoginRequiredMixin, WorkerPermissionsBased, UpdateView):
    """Причины отсутствия на работе."""
    model = InformationMissing
    template_name = 'user/worker/planning/informationmissing_control.html'
    form_class = InformationMissing_Form
    success_url = reverse_lazy('informationmissing')
    login_url = 'login'
    permission_required = 'workers.InformationMissing_change'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = InformationMissing.objects.get(slug=self.kwargs.get('informationmissing_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Причина отсутствия на работе'
        context['title_page'] = 'Редактировать'

        return context

#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class InformationWeekendsHolidays_View(LoginRequiredMixin, WorkerPermissionsBased, ListView):
    """Информация о выходных днях и праздниках."""
    model = InformationWeekendsHolidays
    template_name = 'user/worker/planning/informationweekendsholidays_view.html'
    context_object_name = 'informationWeekendsHolidays'
    login_url = 'login'
    permission_required = 'workers.InformationWeekendsHolidays_view'
    paginate_by = 40

    def get(self, *args, **kwargs):
        if self.request.user.has_perm('workers.InformationWeekendsHolidays_delete'):
            query = self.request.GET.get('remove')
            if query != None:
                try:
                    remove = InformationWeekendsHolidays.objects.get(pk=query)
                    remove.delete()
                except:
                    pass
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        return InformationWeekendsHolidays.objects.all().order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Информация о выходных днях и праздниках'
        return context

#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class InformationWeekendsHolidays_Add(LoginRequiredMixin, WorkerPermissionsBased, CreateView):
    """Информация о выходных днях и праздниках."""
    model = InformationWeekendsHolidays
    template_name = 'user/worker/planning/informationweekendsholidays_control.html'
    form_class = InformationWeekendsHolidays_Form
    success_url = reverse_lazy('informationweekendsholidays')
    login_url = 'login'
    permission_required = 'workers.InformationWeekendsHolidays_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить информацию о выходных днях и праздниках'
        context['title_page'] = 'Добавить'
        return context

#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class InformationWeekendsHolidays_Update(LoginRequiredMixin, WorkerPermissionsBased, UpdateView):
    """Причины отсутствия на работе."""
    model = InformationWeekendsHolidays
    template_name = 'user/worker/planning/informationweekendsholidays_control.html'
    form_class = InformationWeekendsHolidays_Form
    success_url = reverse_lazy('informationweekendsholidays')
    login_url = 'login'
    permission_required = 'workers.InformationWeekendsHolidays_change'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать информацию о выходных днях и праздниках'
        context['title_page'] = 'Редактировать'
        return context
    # Управление по slug


class WorkersMissing_View(LoginRequiredMixin, WorkerMissingPermissionsViewMixin, ListView):
    paginate_by = 40
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing.html'
    context_object_name = 'workers_missings'
    workerBasic = None
    worker = None
    login_url = 'login'

    permission = 'workers.WorkersMissing_view_all'  # права высшее руководство
    permission_subdivision = 'workers.WorkersMissing_view_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkersMissing_view'  # права Управление и отдел

    def get_queryset(self):
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        if self.request.GET:
            """Проверка формы для запроса"""
            form = WorkersMissing_Filter(self.request.GET,
                                         initial={'workerBasic': self.workerBasic, 'user': self.request.user})
            if form.is_valid():
                if not self.request.GET.get('date_in') == '' and self.request.GET.get('date_in'):
                    get_date_in = self.request.GET.get('date_in').split('.')
                    date_start = datetime.date(int(get_date_in[2]), int(get_date_in[1]), int(get_date_in[0]))
                if not self.request.GET.get('date_out') == '' and self.request.GET.get('date_out'):
                    get_date_out = self.request.GET.get('date_out').split('.')
                    date_end = datetime.date(int(get_date_out[2]), int(get_date_out[1]), int(get_date_out[0]))
                get_workers = 'own'
                if self.request.GET.get('workers'):
                    get_workers = addslashes(self.request.GET.get('workers'))
                if not get_workers == 'own':
                    filters &= Q(**{f'{"user__user__slug"}': get_workers})
        """Фильтр в базу данных"""
        filters &= Q(**{f'{"date_start__gte"}': date_start})
        filters &= Q(**{f'{"date_start__lte"}': date_end})
        if self.workerBasic:
            filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})
            filters &= Q(**{f'{"user__actual_department"}': self.workerBasic.actual_department})

        return WorkersMissing.objects.filter(filters).order_by('-date_start')

    def get(self, request, *args, **kwargs):
        try:
            self.workerBasic = WorkerBasic.objects.get(user=self.request.user)
        except:
            pass
        if self.request.user.has_perm('workers.WorkersMissing_delete') and self.request.GET.get('remove'):
            # Проверка разрешения удаления
            try:
                remove = WorkersMissing.objects.get(pk=self.request.GET.get('remove'))
                if remove.user.actual_subdivision == self.workerBasic.actual_subdivision and remove.user.actual_department == self.workerBasic.actual_department:
                    remove.delete()
            except Exception:
                pass
        return super(WorkersMissing_View, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Отсутствие сотрудников'
        context['form_filter'] = WorkersMissing_Filter(self.request.GET, initial={'workerBasic': self.workerBasic,
                                                                                  'user': self.request.user})
        context['workerBasic'] = self.workerBasic
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            workers = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except Exception as e:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except Exception as e:
                pass
            try:
                workers = self.request.GET['workers']
            except:
                pass
            context['url_filter'] = "?&workers={2}&date_in={0}&date_out={1}".format((dateIn), dateOut, workers)
        return context


class WorkersMissing_Subdivision_View(LoginRequiredMixin, WorkerMissingSubdivisionPermissionsViewMixin, ListView):
    paginate_by = 40
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_subdivision.html'
    context_object_name = 'workers_missings'
    workerBasic = None

    login_url = 'login'
    permission = 'workers.WorkersMissing_view_all'  # права высшее руководство
    permission_subdivision = 'workers.WorkersMissing_view_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkersMissing_view'  # права Управление и отдел

    def get_queryset(self):
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        if self.request.GET:
            """Проверка формы для запроса"""
            form = WorkersMissing_Subdivision_Filter(self.request.GET,
                                         initial={'workerBasic': self.workerBasic, 'user': self.request.user})
            if form.is_valid():
                if not self.request.GET.get('date_in') == '' and self.request.GET.get('date_in'):
                    get_date_in = self.request.GET.get('date_in').split('.')
                    date_start = datetime.date(int(get_date_in[2]), int(get_date_in[1]), int(get_date_in[0]))
                if not self.request.GET.get('date_out') == '' and self.request.GET.get('date_out'):
                    get_date_out = self.request.GET.get('date_out').split('.')
                    date_end = datetime.date(int(get_date_out[2]), int(get_date_out[1]), int(get_date_out[0]))

                get_department = 'own'
                if self.request.GET.get('department'):
                    get_department = addslashes(self.request.GET.get('department'))
                if not get_department == 'own':
                    filters &= Q(**{f'{"user__actual_department__slug"}': get_department})

                get_workers = 'own'
                if self.request.GET.get('workers'):
                    get_workers = addslashes(self.request.GET.get('workers'))
                if not get_workers == 'own':
                    filters &= Q(**{f'{"user__user__slug"}': get_workers})

        """Фильтр в базу данных"""
        filters &= Q(**{f'{"date_start__gte"}': date_start})
        filters &= Q(**{f'{"date_start__lte"}': date_end})
        if self.workerBasic:
            filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})

        return WorkersMissing.objects.filter(filters).select_related('user__user', 'information_missing').order_by(
            '-date_start')

    def get(self, request, *args, **kwargs):
        try:
            self.workerBasic = WorkerBasic.objects.select_related('user', 'actual_subdivision','actual_department').get(
                user=self.request.user)
        except:
            pass

        if self.request.user.has_perm('workers.WorkersMissing_delete_subdivision') and self.request.GET.get('remove'):
            # Проверка разрешения удаления
            try:
                remove = WorkersMissing.objects.get(pk=self.request.GET.get('remove'))
                if remove.user.actual_subdivision == self.workerBasic.actual_subdivision:
                    remove.delete()
            except Exception:
                pass
        return super(WorkersMissing_Subdivision_View, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Отсутствие сотрудников'
        context['form_filter'] = WorkersMissing_Subdivision_Filter(self.request.GET, initial={'workerBasic': self.workerBasic,
                                                                                  'user': self.request.user})
        context['workerBasic'] = self.workerBasic
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            workers = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except Exception as e:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except Exception as e:
                pass
            try:
                workers = self.request.GET['workers']
            except Exception as e:
                pass
            context['url_filter'] = "?&workers={2}&date_in={0}&date_out={1}".format((dateIn), dateOut, workers)
        return context


#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class WorkersMissing_Department_View(LoginRequiredMixin, WorkerMissingDepartmentPermissionsViewMixin, ListView):
    paginate_by = 40
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_deparment.html'
    context_object_name = 'workers_missings'
    workerBasic = None

    login_url = 'login'
    permission = 'workers.WorkersMissing_view_all'  # права высшее руководство
    permission_subdivision = 'workers.WorkersMissing_view_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkersMissing_view'  # права Управление и отдел

    def get_queryset(self):
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        if self.request.GET:
            """Проверка формы для запроса"""
            form = WorkersMissing_Filter(self.request.GET,
                                         initial={'workerBasic': self.workerBasic, 'user': self.request.user})
            if form.is_valid():
                if not self.request.GET.get('date_in') == '' and self.request.GET.get('date_in'):
                    get_date_in = self.request.GET.get('date_in').split('.')
                    date_start = datetime.date(int(get_date_in[2]), int(get_date_in[1]), int(get_date_in[0]))
                if not self.request.GET.get('date_out') == '' and self.request.GET.get('date_out'):
                    get_date_out = self.request.GET.get('date_out').split('.')
                    date_end = datetime.date(int(get_date_out[2]), int(get_date_out[1]), int(get_date_out[0]))
                get_workers = 'own'
                if self.request.GET.get('workers'):
                    get_workers = addslashes(self.request.GET.get('workers'))
                if not get_workers == 'own':
                    filters &= Q(**{f'{"user__user__slug"}': get_workers})
        """Фильтр в базу данных"""
        filters &= Q(**{f'{"date_start__gte"}': date_start})
        filters &= Q(**{f'{"date_start__lte"}': date_end})
        if self.workerBasic:
            filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})
            filters &= Q(**{f'{"user__actual_department"}': self.workerBasic.actual_department})

        return WorkersMissing.objects.filter(filters).select_related('user__user', 'information_missing').order_by(
            '-date_start')

    def get(self, request, *args, **kwargs):
        try:
            self.workerBasic = WorkerBasic.objects.select_related('user', 'actual_subdivision',
                                                                  'actual_department').get(
                user=self.request.user)
        except:
            pass
        if self.request.user.has_perm('workers.WorkersMissing_delete') and self.request.GET.get('remove'):
            # Проверка разрешения удаления
            try:
                remove = WorkersMissing.objects.get(pk=self.request.GET.get('remove'))
                if remove.user.actual_subdivision == self.workerBasic.actual_subdivision and \
                        remove.user.actual_department == self.workerBasic.actual_department:
                    remove.delete()
            except Exception:
                pass
        return super(WorkersMissing_Department_View, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Отсутствие сотрудников'
        context['form_filter'] = WorkersMissing_Department_Filter(self.request.GET,
                                                                  initial={'workerBasic': self.workerBasic,
                                                                           'user': self.request.user})
        context['workerBasic'] = self.workerBasic
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            workers = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except Exception as e:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except Exception as e:
                pass
            try:
                workers = self.request.GET['workers']
            except Exception as e:
                pass
            context['url_filter'] = "?&workers={2}&date_in={0}&date_out={1}".format((dateIn), dateOut, workers)
        return context


# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class WorkersMissing_UserHis_View(LoginRequiredMixin, WorkerMissingHisPermissionsUpdateMixin, ListView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_userhis.html'
    context_object_name = 'workers_missings'
    paginate_by = 40

    login_url = 'login'
    permission = 'workers.WorkersMissing_his_view'  #
    workerBasic = None

    def get_queryset(self):
        print('1')
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        if self.request.GET:
            """Проверка формы для запроса"""
            form = WorkersMissing_userHis_Filter(self.request.GET)
            if form.is_valid():
                if not self.request.GET.get('date_in') == '' and self.request.GET.get('date_in'):
                    get_date_in = self.request.GET.get('date_in').split('.')
                    date_start = datetime.date(int(get_date_in[2]), int(get_date_in[1]), int(get_date_in[0]))
                if not self.request.GET.get('date_out') == '' and self.request.GET.get('date_out'):
                    get_date_out = self.request.GET.get('date_out').split('.')
                    date_end = datetime.date(int(get_date_out[2]), int(get_date_out[1]), int(get_date_out[0]))
        """Фильтр в базу данных"""
        filters &= Q(**{f'{"date_start__gte"}': date_start})
        filters &= Q(**{f'{"date_start__lte"}': date_end})
        filters &= Q(**{f'{"user__user__slug"}': self.kwargs.get('workers_slug')})

        return WorkersMissing.objects.filter(filters).select_related('user__user', 'information_missing').order_by(
            '-date_start')

    def get(self, request, *args, **kwargs):
        if self.request.user.has_perm('workers.WorkersMissing_his_delete') and self.kwargs.get(
                'workers_slug') == self.request.user.slug and self.request.GET.get('remove'):
            # Проверка разрешения удаления
            try:
                remove = WorkersMissing.objects.get(pk=self.request.GET.get('remove'))
                remove.delete()
            except:
                pass
        return super(WorkersMissing_UserHis_View, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            if not self.workerBasic:
                self.workerBasic = WorkerBasic.objects.select_related('user').get(user=self.request.user)
        except:
            pass
        context['title'] = 'Отсутствие сотрудника "' + str(self.workerBasic) + '"'
        context['title_page'] = 'Отсутствие сотрудника'
        context['form_filter'] = WorkersMissing_userHis_Filter(self.request.GET)
        context['permission_change'] = self.request.user.has_perm(
            'workers.WorkersMissing_his_change') and self.kwargs.get('workers_slug') == self.request.user.slug
        context['permission_remove'] = self.request.user.has_perm(
            'workers.WorkersMissing_his_delete') and self.kwargs.get('workers_slug') == self.request.user.slug
        context['workerBasic'] = self.workerBasic
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            workers = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except:
                pass
            context['url_filter'] = "?date_in={0}&date_out={1}".format((dateIn), dateOut)
        return context

    # def get_form_kwargs(self):
    #     kwargs = super(WorkersMissing_UserHis_View, self).get_form_kwargs()
    #     self.workerBasic = WorkerBasic.objects.select_related('user').get(user=self.request.user)
    #     kwargs['initial']['workerBasic'] = self.workerBasic
    #     return kwargs


class WorkersMissing_Add(CreateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_control.html'
    form_class = WorkersMissing_Control
    success_url = reverse_lazy('workers_missing')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить отсутствие сотрудника'
        context['title_page'] = 'Добавить'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMissing_Add, self).get_form_kwargs()
        kwargs['initial']['workerBasic'] = WorkerBasic.objects.get(user=self.request.user)
        kwargs['initial']['userRight'] = self.request.user
        return kwargs


class WorkersMissing_Subdivision_Add(CreateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_control.html'
    form_class = WorkersMissing_Control
    success_url = reverse_lazy('workers_missing')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить отсутствие сотрудника'
        context['title_page'] = 'Добавить'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMissing_Add, self).get_form_kwargs()
        kwargs['initial']['workerBasic'] = WorkerBasic.objects.get(user=self.request.user)
        kwargs['initial']['userRight'] = self.request.user
        return kwargs


#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class WorkersMissing_Department_Add(LoginRequiredMixin, WorkerMissingDepartmentPermissionsViewMixin, CreateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_department_control.html'
    form_class = WorkersMissing_Department_Control
    success_url = reverse_lazy('workers_missing')

    login_url = 'login'
    permission = 'workers.WorkersMissing_add_all'  # права высшее руководство
    permission_subdivision = 'workers.WorkersMissing_add_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkersMissing_add'  # права Управление и отдел

    workerBasic = None

    def get_context_data(self, *, object_list=None, **kwargs):
        self.workerBasic = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
            user=self.request.user)
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить отсутствие сотрудника'
        context['title_page'] = 'Добавить'
        context['workerBasic'] = self.workerBasic

        return context

    def get_form_kwargs(self):
        if not self.workerBasic:
            # При сохранение не передается  workerBasic в форму
            self.workerBasic = WorkerBasic.objects.select_related('user', 'actual_subdivision',
                                                                  'actual_department').get(user=self.request.user)
        kwargs = super(WorkersMissing_Department_Add, self).get_form_kwargs()
        kwargs['initial']['workerBasic'] = self.workerBasic
        return kwargs


# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class WorkersMissing_UserHis_Add(LoginRequiredMixin, WorkerMissingHisPermissionsUpdateMixin, CreateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_userhis_control.html'
    form_class = WorkersMissing_UserHis_Control

    login_url = 'login'
    permission = 'workers.WorkersMissing_his_add'

    workerBasic = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить отсутствие сотрудника'
        context['title_page'] = 'Добавить'
        context['workerBasic'] = self.workerBasic
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMissing_UserHis_Add, self).get_form_kwargs()
        self.workerBasic = WorkerBasic.objects.select_related('user').get(user=self.request.user)
        kwargs['initial']['workerBasic'] = self.workerBasic
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.workerBasic
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workers_missing_userHis', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkersMissing_Update(UpdateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_control.html'
    form_class = WorkersMissing_Control
    success_url = reverse_lazy('workers_missing')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать отсутствие сотрудника'
        context['title_page'] = 'Редактировать'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMissing_Update, self).get_form_kwargs()
        kwargs['initial']['user_current'] = WorkerBasic.objects.get(user=self.request.user)
        return kwargs


class WorkersMissing_Subdivision_Update(UpdateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_control.html'
    form_class = WorkersMissing_Control
    success_url = reverse_lazy('workers_missing')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать отсутствие сотрудника'
        context['title_page'] = 'Редактировать'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMissing_Update, self).get_form_kwargs()
        kwargs['initial']['user_current'] = WorkerBasic.objects.get(user=self.request.user)
        return kwargs


#####
# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class WorkersMissing_Department_Update(LoginRequiredMixin, WorkerMissingUpdateDepartmentPermissionsViewMixin,
                                       UpdateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_department_control.html'
    form_class = WorkersMissing_Department_Control
    success_url = reverse_lazy('workers_missing')

    login_url = 'login'
    permission = 'workers.WorkersMissing_change_all'  # права высшее руководство
    permission_subdivision = 'workers.WorkersMissing_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkersMissing_change'  # права Управление и отдел

    workerBasic = None

    def get_context_data(self, *, object_list=None, **kwargs):
        self.workerBasic = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
            user=self.request.user)
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать отсутствие сотрудника'
        context['title_page'] = 'Редактировать'
        context['workerBasic'] = self.workerBasic
        return context

    def get_form_kwargs(self):
        if not self.workerBasic:
            # При сохранение не передается  workerBasic в форму
            self.workerBasic = WorkerBasic.objects.select_related('user', 'actual_subdivision',
                                                                  'actual_department').get(user=self.request.user)
        kwargs = super(WorkersMissing_Department_Update, self).get_form_kwargs()
        kwargs['initial']['workerBasic'] = self.workerBasic
        kwargs['initial']['pk'] = self.kwargs['pk']

        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('user', 'user__actual_subdivision', 'user__actual_department')
        return queryset


# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class WorkersMissing_UserHis_Update(LoginRequiredMixin, WorkerMissingHisPermissionsUpdateMixin, UpdateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_userhis_control.html'
    form_class = WorkersMissing_UserHis_Control

    login_url = 'login'
    permission = 'workers.WorkersMissing_his_change'

    workerBasic = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать отсутствие сотрудника'
        context['title_page'] = 'Редактировать'
        context['workerBasic'] = self.workerBasic

        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMissing_UserHis_Update, self).get_form_kwargs()
        self.workerBasic = WorkerBasic.objects.select_related('user').get(user=self.request.user)
        kwargs['initial']['workerBasic'] = self.workerBasic
        kwargs['initial']['pk'] = self.kwargs['pk']
        return kwargs

    def get_success_url(self):
        return reverse('workers_missing_userHis', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkersMission_Add(CreateView):
    model = WorkersMission
    template_name = 'user/worker/planning/workersmission_control.html'
    form_class = WorkersMission_Form_Add
    success_url = reverse_lazy('workersMission')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить командировку'
        context['title_page'] = 'Добавить'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMission_Add, self).get_form_kwargs()
        kwargs['initial']['user_current'] = self.request.user
        try:
            kwargs['initial']['workerBasic_current'] = WorkerBasic.objects.get(user=self.request.user)
        except:
            kwargs['initial']['workerBasic_current'] = None
        return kwargs


class WorkersMission_Update(UpdateView):
    model = WorkersMission
    template_name = 'user/worker/planning/workersmission_control.html'
    form_class = WorkersMission_Form_Add
    success_url = reverse_lazy('workersMission')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать кокомандировку'
        context['title_page'] = 'Редактировать'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMission_Add, self).get_form_kwargs()
        kwargs['initial']['user_current'] = self.request.user
        try:
            kwargs['initial']['workerBasic_current'] = WorkerBasic.objects.get(user=self.request.user)
        except:
            kwargs['initial']['workerBasic_current'] = None
        return kwargs


class WorkersMission_View(ListView):
    paginate_by = 40
    model = WorkersMission
    template_name = 'user/worker/planning/workersmission.html'
    context_object_name = 'workersmissions'
    workerBasic = None

    def get_queryset(self):
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        if self.request.GET:
            """Проверка формы для запроса"""
            form = WorkersMission_Form_Filter(self.request.GET, initial={'user': self.workerBasic})
            if form.is_valid():
                if not self.request.GET.get('date_in') == '' and self.request.GET.get('date_in'):
                    get_date_in = self.request.GET.get('date_in').split('.')
                    date_start = datetime.date(int(get_date_in[2]), int(get_date_in[1]), int(get_date_in[0]))
                if not self.request.GET.get('date_out') == '' and self.request.GET.get('date_out'):
                    get_date_out = self.request.GET.get('date_out').split('.')
                    date_end = datetime.date(int(get_date_out[2]), int(get_date_out[1]), int(get_date_out[0]))
                get_objects = 'own'
                if self.request.GET.get('objects'):
                    get_objects = addslashes(self.request.GET.get('objects'))
                if not get_objects == 'own':
                    filters &= Q(**{f'{"organizations_objects__slug"}': get_objects})
                get_workers = 'own'
                if self.request.GET.get('workers'):
                    get_workers = addslashes(self.request.GET.get('workers'))
                if not get_workers == 'own':
                    filters &= Q(**{f'{"user__user__slug"}': get_workers})

        """Фильтр в базу данных"""
        filters &= Q(**{f'{"date_departure__gte"}': date_start})
        filters &= Q(**{f'{"date_arrival__lte"}': date_end})

        if not self.request.user.has_perm('workers.WorkersMission_view_all') or not self.workerBasic:
            if self.request.user.has_perm('workers.WorkersMission_view_subdivision') and self.workerBasic:
                filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})
            if self.request.user.has_perm(
                    'workers.WorkersMission_view') and self.workerBasic and not self.request.user.has_perm(
                'workers.WorkersMission_view_subdivision'):
                filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})
                filters &= Q(**{f'{"user__actual_department"}': self.workerBasic.actual_department})

        return WorkersMission.objects.filter(filters).order_by('-date_departure')

    def get(self, request, *args, **kwargs):
        try:
            self.workerBasic = WorkerBasic.objects.get(user=self.request.user)
        except:
            pass
        if self.request.user.has_perm('workers.WorkersMission_delete') and self.request.GET.get('remove'):
            # Проверка разрешения удаления
            try:
                remove = WorkersMission.objects.get(pk=self.request.GET.get('remove'))
                if remove.user.actual_subdivision == self.workerBasic.actual_subdivision and remove.user.actual_department == self.workerBasic.actual_department:
                    remove.delete()
            except Exception:
                pass
        return super(WorkersMission_View, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Командировки.'
        context['form_filter'] = WorkersMission_Form_Filter(self.request.GET, initial={'user': self.workerBasic})
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            objects = 'own'
            workers = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except Exception as e:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except Exception as e:
                pass
            try:
                objects = self.request.GET['objects']
            except Exception as e:
                pass
            try:
                workers = self.request.GET['workers']
            except Exception as e:
                pass
            context['url_filter'] = "?&objects={2}&workers={3}&date_in={0}&date_out={1}".format((dateIn), dateOut,
                                                                                                objects, workers)
        return context


class Workers_Work_Planning_View(LoginRequiredMixin, WorkerPlaningPermissionsViewMixin, TemplateView):
    """Планирование работ"""
    template_name = 'user/worker/planning/workers_planning_view.html'

    login_url = 'login'

    permission = 'workers.WorkersPlanning_view_all'  # права высшее руководство
    permission_subdivision = 'workers.WorkersPlanning_view_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkersPlanning_view_department'  # права Управление и отдел
    user = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        """Пользовательская часть календаря"""
        user = None
        try:
            user = WorkerBasic.objects.select_related('user','actual_subdivision', 'actual_department').get(
                user=self.request.user)  #
            self.user = user
        except:
            pass
        context['title'] = 'Планирование работ'
        """Выборка"""
        in_date_month = datetime.datetime.now().month  # Месяц просмотра
        in_date_year = datetime.datetime.now().year  # год просмотра
        subdivision_filter = 'own'  # Управление
        department_filter = 'own'  # Отделы
        in_month_see = 2  #
        """get запросы выбора даты"""
        if self.request.GET:
            form = Planning_Filter(self.request.GET, initial={'user': user})
            if form.is_valid():
                try:
                    year = int(addslashes(str(self.request.GET.get('year'))))
                    if year > 1:
                        in_date_year = int(addslashes(str(self.request.GET.get('year'))))
                except Exception as e:
                    pass
                try:
                    month = int(addslashes(str(self.request.GET.get('month'))))
                    if month > 0 and month < 13:
                        in_date_month = int(addslashes(str(self.request.GET.get('month'))))
                except Exception as e:
                    pass
                try:
                    in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                    if in_month_see > 0 and in_month_see < 12:
                        in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                except Exception as e:
                    pass
                subdivision_filter = self.request.GET.get('subdivision')
                department_filter = self.request.GET.get('department')

        """Верхняя часть календаря"""
        date_begin = datetime.date(in_date_year, in_date_month, 1)
        weekends_holidays = InformationWeekendsHolidays.objects.filter(date__gte=date_begin,
                                                                       date__lte=date_begin + relativedelta(
                                                                           months=in_month_see))  # 2 запрос
        calendar = Table.calendar_up(in_date_month, in_date_year, lasting=in_month_see,
                                     weekends_holidays=weekends_holidays)
        context['calendar'] = calendar
        # # Получить всех пользователей отдела
        if subdivision_filter == 'own' or department_filter == 'own':  #
            workers = WorkerBasic.objects.filter(employee='employee_current').select_related('actual_subdivision',
                                                                                             'actual_department',
                                                                                             'chief', 'user').order_by(
                '-actual_subdivision')
            missings = WorkersMissing.objects.filter(user__employee='employee_current',
                                                     date_start__gte=date_begin - relativedelta(months=6),
                                                     date_end__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','information_missing')
            missions = WorkersMission.objects.filter(user__employee='employee_current',
                                                     date_departure__gte=date_begin - relativedelta(months=6),
                                                     date_arrival__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','organizations_objects')
        else:

            workers = WorkerBasic.objects.filter(employee='employee_current').select_related('actual_subdivision',
                                                                                             'actual_department',
                                                                                             'chief', 'user').order_by(
                '-chief__rights')
            missings = WorkersMissing.objects.filter(user__employee='employee_current',
                                                     date_start__gte=date_begin - relativedelta(months=6),
                                                     date_end__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','information_missing')
            missions = WorkersMission.objects.filter(user__employee='employee_current',
                                                     date_departure__gte=date_begin - relativedelta(months=6),
                                                     date_arrival__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','organizations_objects')

        context['title_user'] = workers
        context['calendar_workers'] = Table.planing(in_date_month, in_date_year, calendar, workers, missings, missions,
                                                    lasting=in_month_see)
        """форма поиска"""
        context['form_filter'] = Planning_Filter(self.request.GET, initial={'user': user})
        """Переходы"""
        date_begin = datetime.date(in_date_year, in_date_month, 1)
        date_up = date_begin + relativedelta(months=1)
        date_down = date_begin - relativedelta(months=1)
        context['up_month'] = "?workers={2}&length={3}&month={0}&year={1}".format(date_up.month, date_up.year,
                                                                                  department_filter, in_month_see)
        context['down_month'] = "?workers={2}&length={3}&month={0}&year={1}".format(date_down.month, date_down.year,
                                                                                    department_filter, in_month_see)
        """Описание цвета"""
        information_missing = InformationMissing.objects.all()
        information_missing_lists = [(i.name, i.color) for i in information_missing]
        information_missing_lists.append(['Командировка итоговая', '#E75A67'])
        information_missing_lists.append(['Командировка планируемая', '#ffff66'])
        context['information_missings'] = information_missing_lists
        return context


class Workers_Work_Planning_Subdivision_View(LoginRequiredMixin, WorkerPlaningSubdivisionPermissionsViewMixin,
                                             TemplateView):
    """Планирование работ Управления"""
    template_name = 'user/worker/planning/workers_planning_subdivision_view.html'

    login_url = 'login'

    permission = 'workers.WorkersPlanning_view_all'  # права высшее руководство
    permission_subdivision = 'workers.WorkersPlanning_view_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkersPlanning_view_department'  # права Управление и отдел
    user = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        slug_subdivision = self.kwargs.get('subdivision_slug')

        """Пользовательская часть календаря"""
        user = None
        try:
            user = WorkerBasic.objects.select_related('actual_subdivision', 'actual_department').get(
                user=self.request.user)  # 1 запрос. !!!!!Сократить запрос
        except:
            pass
        context['title'] = 'Планирование работ'
        """Выборка"""
        in_date_month = datetime.datetime.now().month  # Месяц просмотра
        in_date_year = datetime.datetime.now().year  # год просмотра
        department_filter = 'own'  # Отделы
        in_month_see = 2  #
        """get запросы выбора даты"""
        if self.request.GET:
            form = Planning_Subdivision_Filter(self.request.GET, initial={'user': user})
            if form.is_valid():
                try:
                    year = int(addslashes(str(self.request.GET.get('year'))))
                    if year > 1:
                        in_date_year = int(addslashes(str(self.request.GET.get('year'))))
                except Exception as e:
                    pass
                try:
                    month = int(addslashes(str(self.request.GET.get('month'))))
                    if month > 0 and month < 13:
                        in_date_month = int(addslashes(str(self.request.GET.get('month'))))
                except Exception as e:
                    pass
                try:
                    in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                    if in_month_see > 0 and in_month_see < 12:
                        in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                except Exception as e:
                    pass
                department_filter = self.request.GET.get('department')
        """Верхняя часть календаря"""
        date_begin = datetime.date(in_date_year, in_date_month, 1)
        weekends_holidays = InformationWeekendsHolidays.objects.filter(date__gte=date_begin,
                                                                       date__lte=date_begin + relativedelta(
                                                                           months=in_month_see))  # 2 запрос
        calendar = Table.calendar_up(in_date_month, in_date_year, lasting=in_month_see,
                                     weekends_holidays=weekends_holidays)
        context['calendar'] = calendar
        # Получить всех пользователей отдела
        if department_filter == 'own':  #
            workers = WorkerBasic.objects.filter(actual_subdivision__slug=slug_subdivision,
                                                 employee='employee_current').select_related('actual_subdivision',
                                                                                             'actual_department',
                                                                                             'chief', 'user').order_by(
                'actual_department')
            missings = WorkersMissing.objects.filter(user__actual_subdivision__slug=slug_subdivision,
                                                     user__employee='employee_current',
                                                     date_start__gte=date_begin - relativedelta(months=6),
                                                     date_end__lte=date_begin + relativedelta(months=7),
                                                     )
            missions = WorkersMission.objects.filter(user__actual_subdivision__slug=slug_subdivision,
                                                     user__employee='employee_current',
                                                     date_departure__gte=date_begin - relativedelta(months=6),
                                                     date_arrival__lte=date_begin + relativedelta(months=7),
                                                     )
        else:
            workers = WorkerBasic.objects.filter(actual_subdivision__slug=slug_subdivision,
                                                 actual_department__slug=department_filter,
                                                 employee='employee_current').select_related('actual_subdivision',
                                                                                             'actual_department',
                                                                                             'chief', 'user').order_by(
                'actual_department')
            missings = WorkersMissing.objects.filter(user__actual_subdivision__slug=slug_subdivision,
                                                     user__actual_department__slug=department_filter,
                                                     user__employee='employee_current',
                                                     date_start__gte=date_begin - relativedelta(months=6),
                                                     date_end__lte=date_begin + relativedelta(months=7),
                                                     )
            missions = WorkersMission.objects.filter(user__actual_subdivision__slug=slug_subdivision,
                                                     user__actual_department__slug=department_filter,
                                                     user__employee='employee_current',
                                                     date_departure__gte=date_begin - relativedelta(months=6),
                                                     date_arrival__lte=date_begin + relativedelta(months=7),
                                                     )
        context['title_user'] = workers
        context['calendar_workers'] = Table.planing(in_date_month, in_date_year, calendar, workers, missings, missions,
                                                    lasting=in_month_see)
        """форма поиска"""
        context['form_filter'] = Planning_Subdivision_Filter(self.request.GET, initial={'user': user})
        """Переходы"""
        date_begin = datetime.date(in_date_year, in_date_month, 1)
        date_up = date_begin + relativedelta(months=1)
        date_down = date_begin - relativedelta(months=1)
        context['up_month'] = "?workers={2}&length={3}&month={0}&year={1}".format(date_up.month, date_up.year,
                                                                                  department_filter, in_month_see)
        context['down_month'] = "?workers={2}&length={3}&month={0}&year={1}".format(date_down.month, date_down.year,
                                                                                    department_filter, in_month_see)
        """Описание цвета"""
        information_missing = InformationMissing.objects.all()
        information_missing_lists = [(i.name, i.color) for i in information_missing]
        information_missing_lists.append(['Командировка итоговая', '#E75A67'])
        information_missing_lists.append(['Командировка планируемая', '#ffff66'])
        context['information_missings'] = information_missing_lists
        return context

# Дизайн - ок
# Оптимизация - ОК
# Права доступа -ОК
class Workers_Work_Planning_Department_View(LoginRequiredMixin, WorkerPlaningDepartmentPermissionsViewMixin,
                                            TemplateView):
    """Планирование работ Управления и отдел"""
    template_name = 'user/worker/planning/workers_planning_department_view.html'
    login_url = 'login'

    permission = 'workers.WorkersPlanning_view_department'  # права Управление и отдел
    user = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        slug_subdivision = self.kwargs.get('subdivision_slug')
        slug_department = self.kwargs.get('department_slug')

        """Пользовательская часть календаря"""
        user = None
        try:
            user = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass
        context['title'] = 'Планирование работ'
        # """Выборка"""
        in_date_month = datetime.datetime.now().month  # Месяц просмотра
        in_date_year = datetime.datetime.now().year  # год просмотра
        workers_filter = 'own'  # Сотрудник
        in_month_see = 2  #
        """get запросы выбора даты"""
        if self.request.GET:
            form = Planning_Department_Filter(self.request.GET, initial={'user': user})
            if form.is_valid():
                try:
                    year = int(addslashes(str(self.request.GET.get('year'))))
                    if year > 1:
                        in_date_year = int(addslashes(str(self.request.GET.get('year'))))
                except Exception as e:
                    pass
                try:
                    month = int(addslashes(str(self.request.GET.get('month'))))
                    if month > 0 and month < 13:
                        in_date_month = int(addslashes(str(self.request.GET.get('month'))))
                except Exception as e:
                    pass
                try:
                    in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                    if in_month_see > 0 and in_month_see < 12:
                        in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                except Exception as e:
                    pass
                workers_filter = self.request.GET.get('workers')
        # """Верхняя часть календаря"""
        date_begin = datetime.date(in_date_year, in_date_month, 1)
        weekends_holidays = InformationWeekendsHolidays.objects.filter(date__gte=date_begin,
                                                                       date__lte=date_begin + relativedelta(
                                                                           months=in_month_see))  # 2 запрос
        calendar = Table.calendar_up(in_date_month, in_date_year, lasting=in_month_see,
                                     weekends_holidays=weekends_holidays)
        context['calendar'] = calendar
        # Получить всех пользователей отдела
        if workers_filter == 'own':
            workers = WorkerBasic.objects.filter(actual_subdivision__slug=slug_subdivision,
                                                 actual_department__slug=slug_department,
                                                 employee='employee_current').select_related('actual_subdivision',
                                                                                             'actual_department',
                                                                                             'chief', 'user').order_by(
                '-chief__rights')
            missings = WorkersMissing.objects.filter(user__actual_subdivision__slug=slug_subdivision,
                                                     user__actual_department__slug=slug_department,
                                                     user__employee='employee_current',
                                                     date_start__gte=date_begin - relativedelta(months=6),
                                                     date_end__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','information_missing')
            missions = WorkersMission.objects.filter(user__actual_subdivision__slug=slug_subdivision,
                                                     user__actual_department__slug=slug_department,
                                                     user__employee='employee_current',
                                                     date_departure__gte=date_begin - relativedelta(months=6),
                                                     date_arrival__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','organizations_objects')
        else:
            workers = WorkerBasic.objects.filter(user__slug=workers_filter,
                                                 employee='employee_current').select_related('actual_subdivision',
                                                                                             'actual_department',
                                                                                             'chief', 'user').order_by(
                '-chief__rights')
            missings = WorkersMissing.objects.filter(user__user__slug=workers_filter,
                                                     user__employee='employee_current',
                                                     date_start__gte=date_begin - relativedelta(months=6),
                                                     date_end__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','information_missing')
            missions = WorkersMission.objects.filter(user__user__slug=workers_filter,
                                                     user__employee='employee_current',
                                                     date_departure__gte=date_begin - relativedelta(months=6),
                                                     date_arrival__lte=date_begin + relativedelta(months=7),
                                                     ).select_related('user','organizations_objects')
        context['title_user'] = workers
        context['calendar_workers'] = Table.planing(in_date_month, in_date_year, calendar, workers, missings, missions,
                                                    lasting=in_month_see)
        """форма поиска"""
        context['form_filter'] = Planning_Department_Filter(self.request.GET, initial={'user': user})
        """Переходы"""
        date_begin = datetime.date(in_date_year, in_date_month, 1)
        date_up = date_begin + relativedelta(months=1)
        date_down = date_begin - relativedelta(months=1)
        context['up_month'] = "?workers={2}&length={3}&month={0}&year={1}".format(date_up.month, date_up.year,
                                                                                  workers_filter, in_month_see)
        context['down_month'] = "?workers={2}&length={3}&month={0}&year={1}".format(date_down.month, date_down.year,
                                                                                    workers_filter, in_month_see)
        """Описание цвета"""
        information_missing = InformationMissing.objects.all()
        information_missing_lists = [(i.name, i.color) for i in information_missing]
        information_missing_lists.append(['Командировка итоговая', '#E75A67'])
        information_missing_lists.append(['Командировка планируемая', '#ffff66'])
        context['information_missings'] = information_missing_lists

        return context


class WorkersWeekendWork_View(ListView):
    paginate_by = 40
    model = WorkersWeekendWork
    template_name = 'workers/worker/planning/workersweekendwork.html'
    context_object_name = 'workersweekendworks'
    workerBasic = None

    def get_queryset(self):
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        # if self.request.GET:
        #     """Проверка формы для запроса"""
        #     form = WorkersMissing_Filter(self.request.GET, initial={'user': self.workerBasic})
        #     if form.is_valid():
        #         if not self.request.GET.get('date_in') == '' and self.request.GET.get('date_in'):
        #             get_date_in = self.request.GET.get('date_in').split('.')
        #             date_start = datetime.date(int(get_date_in[2]), int(get_date_in[1]), int(get_date_in[0]))
        #         if not self.request.GET.get('date_out') == '' and self.request.GET.get('date_out'):
        #             get_date_out = self.request.GET.get('date_out').split('.')
        #             date_end = datetime.date(int(get_date_out[2]), int(get_date_out[1]), int(get_date_out[0]))
        #         get_workers = 'own'
        #         if self.request.GET.get('workers'):
        #             get_workers = addslashes(self.request.GET.get('workers'))
        #         if not get_workers == 'own':
        #             filters &= Q(**{f'{"user__user__slug"}': get_workers})
        # """Фильтр в базу данных"""
        filters &= Q(**{f'{"date__gte"}': date_start})
        filters &= Q(**{f'{"date__lte"}': date_end})
        filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})
        filters &= Q(**{f'{"user__actual_department"}': self.workerBasic.actual_department})

        return WorkersWeekendWork.objects.filter(filters).order_by('-date')

    def get(self, request, *args, **kwargs):
        self.workerBasic = WorkerBasic.objects.get(user=self.request.user)
        if self.request.user.has_perm('workers.WorkersWeekendWork_delete') and self.request.GET.get('remove'):
            # Проверка разрешения удаления
            try:
                remove = WorkersWeekendWork.objects.get(pk=self.request.GET.get('remove'))
                if remove.user.actual_subdivision == self.workerBasic.actual_subdivision and remove.user.actual_department == self.workerBasic.actual_department:
                    remove.delete()
            except Exception:
                pass
        return super(WorkersWeekendWork_View, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Работа в выходные в офисе.'
        # context['form_filter'] = WorkersMissing_Filter(self.request.GET, initial={
        #     'user': self.workerBasic})

        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            workers = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except Exception as e:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except Exception as e:
                pass
            try:
                workers = self.request.GET['workers']
            except Exception as e:
                pass
            context['url_filter'] = "?&workers={2}&date_in={0}&date_out={1}".format((dateIn), dateOut, workers)
        return context


class WorkersWeekendWork_Add(CreateView):
    model = WorkersWeekendWork
    template_name = 'workers/worker/planning/workersweekendwork_control.html'
    form_class = WorkersWeekendWork_Control
    success_url = reverse_lazy('workers_weekendwork')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить работу в выходные'
        context['title_page'] = 'Добавить'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersWeekendWork_Add, self).get_form_kwargs()
        kwargs['initial']['user_current'] = WorkerBasic.objects.get(user=self.request.user)
        return kwargs


class WorkersWeekendWork_Update(UpdateView):
    model = WorkersWeekendWork
    template_name = 'workers/worker/planning/workersweekendwork_control.html'
    form_class = WorkersWeekendWork_Control
    success_url = reverse_lazy('workers_weekendwork')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать отсутствие сотрудника'
        context['title_page'] = 'Редактировать'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersWeekendWork_Update, self).get_form_kwargs()
        kwargs['initial']['user_current'] = WorkerBasic.objects.get(user=self.request.user)
        return kwargs


class WorkersWeekendWork_Time_Update(UpdateView):
    model = WorkersWeekendWork
    template_name = 'workers/worker/planning/workersweekendwork_time_control.html'
    form_class = WorkersWeekendWork_Time_Control
    success_url = reverse_lazy('workers_missing')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Указать время работы в выходные'
        context['title_page'] = 'Указать'
        context['worker'] = WorkersWeekendWork.objects.get(pk=self.kwargs.get('pk', ''))

        return context
