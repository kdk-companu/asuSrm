from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.template.defaultfilters import addslashes

from apps.workers.forms import WorkersMissingManagement_Filter, WorkersMissing_Subdivision_Filter, \
    WorkersMissing_userHis_Filter, \
    WorkersMissing_Department_Control, WorkersMissing_UserHis_Control, InformationMissing_Form, WorkersMissing_Control, \
    WorkersMissing_Subdivision_Control, WorkersMissing_Department_Filter
from apps.workers.models import InformationMissing, WorkersMissing, WorkerBasic
from mixin.access.access import AccessProjectMixin
from mixin.access.workers.workers_access import UserAccessMixin
from mixin.workers_right import WorkerMissingPermissionsViewMixin, \
    WorkerMissingSubdivisionPermissionsViewMixin, WorkerMissingDepartmentPermissionsViewMixin, \
    WorkerMissingHisPermissionsUpdateMixin, WorkerMissingUpdateDepartmentPermissionsViewMixin
from django.views.generic import ListView, UpdateView, CreateView, TemplateView
import datetime
from django.urls import reverse_lazy, reverse


class InformationMissing_View(LoginRequiredMixin, AccessProjectMixin, ListView):
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


class InformationMissing_Add(LoginRequiredMixin, AccessProjectMixin, CreateView):
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


class InformationMissing_Update(LoginRequiredMixin, AccessProjectMixin, UpdateView):
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


class WorkersMissingTemplate(LoginRequiredMixin, ListView):
    paginate_by = 40
    model = WorkersMissing
    context_object_name = 'workers_missings'

    permission_management = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_department = None  # права отдел
    permission_his = None  # права на самостоятельное редактирование

    login_url = 'login'

    def get_queryset(self):
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        if self.request.GET:
            """Проверка формы для запроса"""
            form = WorkersMissingManagement_Filter(self.request.GET, initial={'user': self.user, })
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

        return WorkersMissing.objects.filter(filters).select_related('user', 'user__user',
                                                                     'information_missing').order_by('-date_start')

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
        return super(WorkersMissingTemplate, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Отсутствие сотрудников'
        context['form_filter'] = WorkersMissingManagement_Filter(self.request.GET, initial={'user': self.user, })
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


class WorkersMissingManagement_View(UserAccessMixin, WorkersMissingTemplate):
    template_name = 'user/worker/planning/workersmissing_managment_view.html'

    permission_management = 'workers.WorkersMissing_management_view'  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_department = None  # права отдел
    permission_his = None  # права на самостоятельное редактирование


class WorkersMissing_View(LoginRequiredMixin, WorkerMissingPermissionsViewMixin, ListView):
    paginate_by = 40
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_managment_view.html'
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
            form = WorkersMissingManagement_Filter(self.request.GET,
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
        context['form_filter'] = WorkersMissingManagement_Filter(self.request.GET,
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
                                                     initial={'workerBasic': self.workerBasic,
                                                              'user': self.request.user})
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
            self.workerBasic = WorkerBasic.objects.select_related('user', 'actual_subdivision',
                                                                  'actual_department').get(
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

        context['form_filter'] = WorkersMissing_Subdivision_Filter(self.request.GET,
                                                                   initial={'workerBasic': self.workerBasic,
                                                                            'user': self.request.user})
        context['workerBasic'] = self.workerBasic
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            workers = 'own'
            department = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except Exception as e:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except Exception as e:
                pass
            try:
                department = self.request.GET['department']
            except Exception as e:
                pass
            try:
                workers = self.request.GET['workers']
            except Exception as e:
                pass
            context['url_filter'] = "?department={3}&workers={2}&date_in={0}&date_out={1}".format((dateIn), dateOut,
                                                                                                  workers, department)
        return context


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
            form = WorkersMissingManagement_Filter(self.request.GET,
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


class WorkersMissing_UserHis_View(LoginRequiredMixin, WorkerMissingHisPermissionsUpdateMixin, ListView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_userhis.html'
    context_object_name = 'workers_missings'
    paginate_by = 40

    login_url = 'login'
    permission = 'workers.WorkersMissing_his_view'
    workerBasic = None

    def get_queryset(self):
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
        # Разрешение редактирования
        context['permission_change'] = self.request.user.has_perm(
            'workers.WorkersMissing_his_change') and self.kwargs.get('workers_slug') == self.request.user.slug
        # Разрешение удаления
        context['permission_remove'] = self.request.user.has_perm(
            'workers.WorkersMissing_his_delete') and self.kwargs.get('workers_slug') == self.request.user.slug
        context['workerBasic'] = self.workerBasic
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
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
    template_name = 'user/worker/planning/workersmissing_subdivision_control.html'
    form_class = WorkersMissing_Subdivision_Control

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
        kwargs = super(WorkersMissing_Subdivision_Add, self).get_form_kwargs()
        kwargs['initial']['workerBasic'] = self.workerBasic
        return kwargs

    def get_success_url(self):
        return reverse('workers_missing_subdivision', kwargs={'subdivision_slug': self.kwargs['subdivision_slug']})


class WorkersMissing_Department_Add(LoginRequiredMixin, WorkerMissingDepartmentPermissionsViewMixin, CreateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_department_control.html'
    form_class = WorkersMissing_Department_Control

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

    def get_success_url(self):
        return reverse('workers_missing_subdivision_department',
                       kwargs={'subdivision_slug': self.kwargs['subdivision_slug'],
                               'department_slug': self.kwargs['department_slug']})


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
    template_name = 'user/worker/planning/workersmissing_subdivision_control.html'
    form_class = WorkersMissing_Control

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать отсутствие сотрудника'
        context['title_page'] = 'Редактировать'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMissing_Subdivision_Update, self).get_form_kwargs()
        kwargs['initial']['user_current'] = WorkerBasic.objects.get(user=self.request.user)
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('user', 'user__actual_subdivision', 'user__actual_department')
        return queryset

    def get_success_url(self):
        return reverse('workers_missing_subdivision', kwargs={'subdivision_slug': self.kwargs['subdivision_slug']})


class WorkersMissing_Department_Update(LoginRequiredMixin, WorkerMissingUpdateDepartmentPermissionsViewMixin,
                                       UpdateView):
    model = WorkersMissing
    template_name = 'user/worker/planning/workersmissing_department_control.html'
    form_class = WorkersMissing_Department_Control

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

    def get_success_url(self):
        return reverse('workers_missing_userHis', kwargs={'workers_slug': self.kwargs['workers_slug']})


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
