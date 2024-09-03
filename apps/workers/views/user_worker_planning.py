from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.template.defaultfilters import addslashes
from django.urls import reverse_lazy

from django.views.generic import ListView, UpdateView, CreateView, TemplateView
from dateutil.relativedelta import relativedelta

from apps.workers.forms import Planning_Managment_Filter, InformationWeekendsHolidays_Form, WorkersWeekendWork_Control, \
    WorkersWeekendWork_Time_Control, Planning_Department_Filter, Planning_Subdivision_Filter, Planning_His_Filter
from apps.workers.models import InformationMissing, InformationWeekendsHolidays, WorkerBasic, WorkersMissing, \
    WorkersWeekendWork, WorkersMission
import datetime

from library.table import Table
from mixin.access.access import AccessProjectMixin
from mixin.access.workers.workers_access import UserAccessMixin, UserAccessMixin_PlaningManagement


class InformationWeekendsHolidays_View(LoginRequiredMixin, AccessProjectMixin, ListView):
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


class InformationWeekendsHolidays_Add(LoginRequiredMixin, AccessProjectMixin, CreateView):
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


class InformationWeekendsHolidays_Update(LoginRequiredMixin, AccessProjectMixin, UpdateView):
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


class Workers_Work_Planning(LoginRequiredMixin, TemplateView):
    """Планирование работ. Базовый класс"""
    login_url = 'login'
    permission_management = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_department = None  # права отдел
    permission_his = None  # права на самостоятельное редактирование

    def get_Workers(self, subdivision=None, department=None):
        None

    def get_WorkersMissing(self, date_begin, date_end, subdivision=None, department=None):
        None

    def get_WorkersMission(self, date_begin, date_end, subdivision=None, department=None):
        None

    def get_UserForm(self):
        None

    def get_UserForfUpdate(self):
        None

    def get_FormPaginationUp(self):
        None

    def get_FormPaginationDown(self):
        None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Планирование работ'
        """Выборка"""
        in_date_month = datetime.datetime.now().month  # Месяц просмотра
        in_date_year = datetime.datetime.now().year  # год просмотра
        in_month_see = 2  #
        """Верхняя часть календаря"""
        subdivision = None
        department = None
        # Обработка get Запроса
        if self.request.GET:
            unpuck = self.get_UserForfUpdate()
            if unpuck:
                if unpuck.get('in_date_year'):
                    in_date_year = unpuck.get('in_date_year')
                if unpuck.get('in_date_month'):
                    in_date_month = unpuck.get('in_date_month')
                if unpuck.get('in_month_see'):
                    in_month_see = unpuck.get('in_month_see')
                subdivision = unpuck.get('subdivision_filter')
                department = unpuck.get('department_filter')

        date_begin = datetime.date(in_date_year, in_date_month, 1)
        date_end = date_begin + relativedelta(months=in_month_see)
        #
        weekends_holidays = InformationWeekendsHolidays.objects.filter(date__gte=date_begin, date__lte=date_end)
        calendar = Table.calendar_up(in_date_month, in_date_year, lasting=in_month_see,
                                     weekends_holidays=weekends_holidays)
        context['calendar'] = calendar

        # Получение основной таблицы
        workers = WorkerBasic.objects.filter(
            self.get_Workers(subdivision=subdivision, department=department)).select_related('actual_subdivision',
                                                                                             'actual_department',
                                                                                             'chief',
                                                                                             'user').order_by(
            '-actual_subdivision')

        missings = WorkersMissing.objects.filter(
            self.get_WorkersMissing(date_begin, date_end, subdivision=subdivision,
                                    department=department)).select_related('user', 'information_missing')
        missions = WorkersMission.objects.filter(self.get_WorkersMission(date_begin, date_end, subdivision=subdivision,
                                                                         department=department)).select_related('user',
                                                                                                                'organizations_objects')
        context['calendar_workers'] = Table.planing(in_date_month, in_date_year, calendar, workers, missings, missions,
                                                    lasting=in_month_see)

        """форма поиска"""
        context['form_filter'] = self.get_UserForm()
        """Переходы"""
        context['up_month'] = self.get_FormPaginationUp(in_date_year, in_date_month, in_month_see, subdivision,
                                                        department)
        context['down_month'] = self.get_FormPaginationDown(in_date_year, in_date_month, in_month_see, subdivision,
                                                            department)
        """возврат текущего пользователя"""
        context['worker'] = self.user
        """Описание цвета"""
        information_missing = InformationMissing.objects.all()
        information_missing_lists = [(i.name, i.color) for i in information_missing]
        information_missing_lists.append(['Командировка итоговая', '#E75A67'])
        information_missing_lists.append(['Командировка планируемая', '#ffff66'])
        context['information_missings'] = information_missing_lists
        return context


class Workers_Work_PlanningManagement_View(UserAccessMixin_PlaningManagement, Workers_Work_Planning):
    """Планирование работ. Базовый класс"""
    template_name = 'user/worker/planning/planning_managment_view.html'

    permission_management = 'workers.WorkersPlannig_management_view'  # права высшее руководство
    permission_subdivision = 'workers.WorkersPlannig_subdivision_view'  # права Управление
    permission_department = 'workers.WorkersPlannig_department_view'  # права отдел
    permission_his = 'workers.WorkersPlannig_his_view'  # права на самостоятельное редактирование

    def get_Workers(self, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"employee"}': 'employee_current'})
        if subdivision:
            if subdivision != 'own':
                query &= Q(**{f'{"actual_subdivision__slug"}': subdivision})
        if department:
            if department != 'own':
                query &= Q(**{f'{"actual_department__slug"}': department})
        return query

    def get_WorkersMissing(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        if subdivision:
            if subdivision != 'own':
                query &= Q(**{f'{"user__actual_subdivision__slug"}': subdivision})
        if department:
            if department != 'own':
                query &= Q(**{f'{"user__actual_department__slug"}': department})
        query &= Q(**{f'{"date_start__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_end__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_WorkersMission(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        if subdivision:
            if subdivision != 'own':
                query &= Q(**{f'{"user__actual_subdivision__slug"}': subdivision})
        if department:
            if department != 'own':
                query &= Q(**{f'{"user__actual_department__slug"}': department})
        query &= Q(**{f'{"date_departure__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_arrival__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_UserForm(self):
        return Planning_Managment_Filter(self.request.GET, initial={'user': self.user})

    def get_FormPaginationUp(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_up = date_begin + relativedelta(months=1)
        subdivisionOut = subdivision if subdivision else 'own'
        departmentOut = department if department else 'own'
        return "?subdivision={3}&department={4}&length={2}&month={0}&year={1}".format(date_up.month, date_up.year,
                                                                                      month_see, subdivisionOut,
                                                                                      departmentOut)

    def get_FormPaginationDown(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_down = date_begin - relativedelta(months=1)
        return "?subdivision={3}&department={4}&length={2}&month={0}&year={1}".format(date_down.month, date_down.year,
                                                                                      month_see, subdivision,
                                                                                      department)

    def get_UserForfUpdate(self):
        form = Planning_Managment_Filter(self.request.GET, initial={'user': self.user})
        out = dict()
        out['error'] = False
        if form.is_valid():
            try:
                year = int(addslashes(str(self.request.GET.get('year'))))
                if year > 1:
                    out['in_date_year'] = int(addslashes(str(self.request.GET.get('year'))))
            except Exception as e:
                out['error'] = True
            try:
                month = int(addslashes(str(self.request.GET.get('month'))))
                if month > 0 and month < 13:
                    out['in_date_month'] = int(addslashes(str(self.request.GET.get('month'))))
            except Exception as e:
                out['error'] = True
            try:
                in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                if in_month_see > 0 and in_month_see < 12:
                    out['in_month_see'] = int(addslashes(str(self.request.GET.get('length'))))
            except Exception as e:
                out['error'] = True
            out['subdivision_filter'] = self.request.GET.get('subdivision')
            out['department_filter'] = self.request.GET.get('department')
            return out


class Workers_Work_PlanningSubdivision_View(UserAccessMixin, Workers_Work_Planning):
    """Планирование работ. Базовый класс"""
    template_name = 'user/worker/planning/planning_subdivision_view.html'

    permission_management = None  # права высшее руководство
    permission_subdivision = 'workers.WorkersPlannig_subdivision_view'  # права Управление
    permission_department = None  # права отдел
    permission_his = None  # права на самостоятельное редактирование

    def get_Workers(self, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"employee"}': 'employee_current'})
        query &= Q(**{f'{"actual_subdivision__slug"}': self.kwargs.get('subdivision_slug')})
        if department:
            if department != 'own':
                query &= Q(**{f'{"actual_department__slug"}': department})
        return query

    def get_WorkersMissing(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        query &= Q(**{f'{"user__actual_subdivision__slug"}': self.kwargs.get('subdivision_slug')})
        if department:
            if department != 'own':
                query &= Q(**{f'{"user__actual_department__slug"}': department})
        query &= Q(**{f'{"date_start__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_end__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_WorkersMission(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        query &= Q(**{f'{"user__actual_subdivision__slug"}': self.kwargs.get('subdivision_slug')})
        if department:
            if department != 'own':
                query &= Q(**{f'{"user__actual_department__slug"}': department})
        query &= Q(**{f'{"date_departure__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_arrival__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_UserForm(self):
        return Planning_Subdivision_Filter(self.request.GET, initial={'user': self.user})

    def get_FormPaginationUp(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_up = date_begin + relativedelta(months=1)
        subdivisionOut = subdivision if subdivision else 'own'
        departmentOut = department if department else 'own'
        return "?department={4}&length={2}&month={0}&year={1}".format(date_up.month, date_up.year,
                                                                      month_see, subdivisionOut,
                                                                      departmentOut)

    def get_FormPaginationDown(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_down = date_begin - relativedelta(months=1)
        return "?department={4}&length={2}&month={0}&year={1}".format(date_down.month, date_down.year,
                                                                      month_see, subdivision,
                                                                      department)

    def get_UserForfUpdate(self):
        form = Planning_Subdivision_Filter(self.request.GET, initial={'user': self.user})
        out = dict()
        out['error'] = False
        if form.is_valid():
            try:
                year = int(addslashes(str(self.request.GET.get('year'))))
                if year > 1:
                    out['in_date_year'] = int(addslashes(str(self.request.GET.get('year'))))
            except Exception as e:
                out['error'] = True
            try:
                month = int(addslashes(str(self.request.GET.get('month'))))
                if month > 0 and month < 13:
                    out['in_date_month'] = int(addslashes(str(self.request.GET.get('month'))))
            except Exception as e:
                out['error'] = True
            try:
                in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                if in_month_see > 0 and in_month_see < 12:
                    out['in_month_see'] = int(addslashes(str(self.request.GET.get('length'))))
            except Exception as e:
                out['error'] = True
            out['department_filter'] = self.request.GET.get('department')
            return out


class Workers_Work_PlanningDepartment_View(UserAccessMixin, Workers_Work_Planning):
    """Планирование работ. Базовый класс"""
    template_name = 'user/worker/planning/planning_department_view.html'

    permission_management = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_department = 'workers.WorkersPlannig_department_view'  # права отдел
    permission_his = None  # права на самостоятельное редактирование

    def get_Workers(self, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"employee"}': 'employee_current'})
        query &= Q(**{f'{"actual_subdivision__slug"}': self.kwargs.get('subdivision_slug')})
        query &= Q(**{f'{"actual_department__slug"}': self.kwargs.get('department_slug')})
        return query

    def get_WorkersMissing(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        query &= Q(**{f'{"user__actual_subdivision__slug"}': self.kwargs.get('subdivision_slug')})
        query &= Q(**{f'{"user__actual_department__slug"}': self.kwargs.get('department_slug')})
        query &= Q(**{f'{"date_start__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_end__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_WorkersMission(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        query &= Q(**{f'{"user__actual_subdivision__slug"}': self.kwargs.get('subdivision_slug')})
        query &= Q(**{f'{"user__actual_department__slug"}': self.kwargs.get('department_slug')})
        query &= Q(**{f'{"date_departure__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_arrival__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_UserForm(self):
        return Planning_Department_Filter(self.request.GET, initial={'user': self.user})

    def get_FormPaginationUp(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_up = date_begin + relativedelta(months=1)
        return "?length={2}&month={0}&year={1}".format(date_up.month, date_up.year, month_see)

    def get_FormPaginationDown(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_down = date_begin - relativedelta(months=1)
        return "?length={2}&month={0}&year={1}".format(date_down.month, date_down.year, month_see)

    def get_UserForfUpdate(self):
        form = Planning_Department_Filter(self.request.GET, initial={'user': self.user})
        out = dict()
        out['error'] = False
        if form.is_valid():
            try:
                year = int(addslashes(str(self.request.GET.get('year'))))
                if year > 1:
                    out['in_date_year'] = int(addslashes(str(self.request.GET.get('year'))))
            except Exception as e:
                out['error'] = True
            try:
                month = int(addslashes(str(self.request.GET.get('month'))))
                if month > 0 and month < 13:
                    out['in_date_month'] = int(addslashes(str(self.request.GET.get('month'))))
            except Exception as e:
                out['error'] = True
            try:
                in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                if in_month_see > 0 and in_month_see < 12:
                    out['in_month_see'] = int(addslashes(str(self.request.GET.get('length'))))
            except Exception as e:
                out['error'] = True
            out['department_filter'] = self.request.GET.get('department')
            return out


class Workers_Work_PlanningHis_View(UserAccessMixin, Workers_Work_Planning):
    template_name = 'user/worker/planning/planning_his_view.html'

    permission_management = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_department = None  # права отдел
    permission_his = 'workers.WorkersPlannig_his_view'  # права на самостоятельное редактирование

    def get_Workers(self, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"employee"}': 'employee_current'})
        query &= Q(**{f'{"user__slug"}': self.request.user.slug})
        return query

    def get_WorkersMissing(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        query &= Q(**{f'{"user__user__slug"}': self.request.user.slug})
        query &= Q(**{f'{"date_start__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_end__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_WorkersMission(self, date_begin, date_end, subdivision=None, department=None):
        query = Q()
        query &= Q(**{f'{"user__employee"}': 'employee_current'})
        query &= Q(**{f'{"user__user__slug"}': self.request.user.slug})
        query &= Q(**{f'{"date_departure__gte"}': date_begin - relativedelta(months=4)})
        query &= Q(**{f'{"date_arrival__lte"}': date_end + relativedelta(months=4)})
        return query

    def get_UserForm(self):
        return Planning_His_Filter(self.request.GET, initial={'user': self.user})

    def get_FormPaginationUp(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_up = date_begin + relativedelta(months=1)
        return "?length={2}&month={0}&year={1}".format(date_up.month, date_up.year, month_see)

    def get_FormPaginationDown(self, year, month, month_see, subdivision, department):
        """Переходы"""
        date_begin = datetime.date(year, month, 1)
        date_down = date_begin - relativedelta(months=1)
        return "?length={2}&month={0}&year={1}".format(date_down.month, date_down.year, month_see)

    def get_UserForfUpdate(self):
        form = Planning_His_Filter(self.request.GET, initial={'user': self.user})
        out = dict()
        out['error'] = False
        if form.is_valid():
            try:
                year = int(addslashes(str(self.request.GET.get('year'))))
                if year > 1:
                    out['in_date_year'] = int(addslashes(str(self.request.GET.get('year'))))
            except Exception as e:
                out['error'] = True
            try:
                month = int(addslashes(str(self.request.GET.get('month'))))
                if month > 0 and month < 13:
                    out['in_date_month'] = int(addslashes(str(self.request.GET.get('month'))))
            except Exception as e:
                out['error'] = True
            try:
                in_month_see = int(addslashes(str(self.request.GET.get('length'))))
                if in_month_see > 0 and in_month_see < 12:
                    out['in_month_see'] = int(addslashes(str(self.request.GET.get('length'))))
            except Exception as e:
                out['error'] = True
            out['department_filter'] = self.request.GET.get('department')
            return out

#=======================================================
#=============
#=======================================================

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
