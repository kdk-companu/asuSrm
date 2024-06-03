from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView

from apps.workers.forms import Form_Department_Control, Form_Subdivision_Control, Form_Chief_Control, \
    Group_Form_Permissions
from apps.workers.models import Department, Subdivision, Chief
from mixin.workers_right import WorkerPermissionsBased


class Subdivision_View(LoginRequiredMixin, WorkerPermissionsBased, ListView):
    """Управление/Подразделение"""
    model = Subdivision
    template_name = 'user/worker/structure/subdivision.html'
    login_url = 'login'
    permission_required = 'workers.subdivision_view'

    def get(self, *args, **kwargs):
        if self.request.user.has_perm('workers.subdivision_delete'):
            query = self.request.GET.get('remove')
            if query is not None:
                try:
                    remove = Subdivision.objects.get(slug=query)
                    remove.delete()
                except:
                    pass
        subdivisions = Subdivision.objects.all()  # Запрос
        context = {'subdivisions': subdivisions, 'title': 'Управление/Подразделение'}

        return render(self.request, self.template_name, context)


class Subdivision_Update(LoginRequiredMixin, WorkerPermissionsBased, UpdateView):
    """Управление/Подразделение"""
    model = Subdivision
    template_name = 'user/worker/structure/subdivision_control.html'
    form_class = Form_Subdivision_Control
    success_url = reverse_lazy('subdivision')
    login_url = 'login'
    permission_required = 'workers.subdivision_change'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = Subdivision.objects.get(slug=self.kwargs.get('subdivision_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать управление/подразделение'
        context['title_page'] = 'Редактировать'
        return context


class Subdivision_Add(LoginRequiredMixin, WorkerPermissionsBased, CreateView):
    """Управление/Подразделение"""
    model = Subdivision
    template_name = 'user/worker/structure/subdivision_control.html'
    form_class = Form_Subdivision_Control
    success_url = reverse_lazy('subdivision')
    login_url = 'login'
    permission_required = 'workers.subdivision_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить управление/подразделение'
        context['title_page'] = 'Добавить'

        return context


class Department_View(LoginRequiredMixin, WorkerPermissionsBased, ListView):
    """Департамент/Управление"""
    model = Department
    template_name = 'user/worker/structure/department.html'
    login_url = 'login'
    permission_required = 'workers.department_view'

    def get(self, *args, **kwargs):
        if self.request.user.has_perm('workers.department_delete'):
            query = self.request.GET.get('remove')
            if query is not None:
                try:
                    remove = Department.objects.get(slug=query)
                    remove.delete()
                except:
                    pass
        departments = Department.objects.all()  # Запрос
        context = {'departments': departments, 'title': 'Структура/Отдел'}

        return render(self.request, self.template_name, context)


class Department_Update(LoginRequiredMixin, WorkerPermissionsBased, UpdateView):
    """Департамент. Изменение"""
    model = Department
    template_name = 'user/worker/structure/department_control.html'
    form_class = Form_Department_Control
    success_url = reverse_lazy('department')
    login_url = 'login'
    permission_required = 'workers.department_change'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = Department.objects.get(slug=self.kwargs.get('department_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать структуру/отдел'
        context['title_page'] = 'Редактировать'

        return context


class Department_Add(LoginRequiredMixin, WorkerPermissionsBased, CreateView):
    """Департамент. Добавление"""
    model = Department
    template_name = 'user/worker/structure/department_control.html'
    form_class = Form_Department_Control
    success_url = reverse_lazy('department')
    login_url = 'login'
    permission_required = 'workers.department_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить структуру/отдел'
        context['title_page'] = 'Добавить'
        return context


class Chief_View(LoginRequiredMixin, WorkerPermissionsBased, ListView):
    """Должность"""
    model = Chief
    template_name = 'user/worker/structure/chief.html'
    login_url = 'login'
    permission_required = 'workers.chief_view'

    def get(self, *args, **kwargs):
        if self.request.user.has_perm('workers.chief_delete'):
            query = self.request.GET.get('remove')
            if query is not None:
                try:
                    remove = Chief.objects.get(slug=query)
                    remove.delete()
                except:
                    pass
        chiefs = Chief.objects.all()  # Запрос
        context = {'chiefs': chiefs, 'title': 'Должности'}

        return render(self.request, self.template_name, context)


class Chief_Update(LoginRequiredMixin, WorkerPermissionsBased, UpdateView):
    """Должность. Изменение"""
    model = Chief
    template_name = 'user/worker/structure/chief_control.html'
    form_class = Form_Chief_Control
    success_url = reverse_lazy('chief')
    login_url = 'login'
    permission_required = 'workers.chief_change'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = Chief.objects.get(slug=self.kwargs.get('chief_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать должность'
        context['title_page'] = 'Редактировать'
        return context


class Chief_Add(LoginRequiredMixin, WorkerPermissionsBased, CreateView):
    """Должность. Добавление"""
    model = Chief
    template_name = 'user/worker/structure/chief_control.html'
    form_class = Form_Chief_Control
    success_url = reverse_lazy('chief')
    login_url = 'login'
    permission_required = 'workers.chief_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить должность'
        context['title_page'] = 'Добавить'
        return context


class Group_Permissions(LoginRequiredMixin, WorkerPermissionsBased,UpdateView):
    """Управление группами"""
    model = Group
    form_class = Group_Form_Permissions
    template_name = 'user/worker/structure/chief_perrmision.html'

    login_url = 'login'
    permission_required = 'workers.chief_permissions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Настройка прав должности'
        context['group'] = Group.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse("chief_permissions", kwargs={"pk": self.kwargs['pk']})
