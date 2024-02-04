from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView

from apps.workers.forms import Form_Department_Control, Form_Subdivision_Control, Form_Chief_Control
from apps.workers.models import Department, Subdivision, Chief
from mixin.user_right import ViewsPermissionsMixin


class Subdivision_View(LoginRequiredMixin, ViewsPermissionsMixin, ListView):
    """Управление/Подразделение"""
    model = Subdivision
    template_name = 'workers/organization_structure/subdivision.html'
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


class Subdivision_Update(LoginRequiredMixin, ViewsPermissionsMixin, UpdateView):
    """Управление/Подразделение"""
    model = Subdivision
    template_name = 'workers/organization_structure/subdivision_control.html'
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
        return context


class Subdivision_Add(LoginRequiredMixin, ViewsPermissionsMixin, CreateView):
    """Управление/Подразделение"""
    model = Subdivision
    template_name = 'workers/organization_structure/subdivision_control.html'
    form_class = Form_Subdivision_Control
    success_url = reverse_lazy('subdivision')
    login_url = 'login'
    permission_required = 'workers.subdivision_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить управление/подразделение'

        return context


class Department_View(LoginRequiredMixin, ViewsPermissionsMixin, ListView):
    """Департамент/Управление"""
    model = Department
    template_name = 'workers/organization_structure/department.html'
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


class Department_Update(LoginRequiredMixin, ViewsPermissionsMixin, UpdateView):
    """Департамент. Изменение"""
    model = Department
    template_name = 'workers/organization_structure/department_control.html'
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
        return context


class Department_Add(LoginRequiredMixin, ViewsPermissionsMixin, CreateView):
    """Департамент. Добавление"""
    model = Department
    template_name = 'workers/organization_structure/department_control.html'
    form_class = Form_Department_Control
    success_url = reverse_lazy('department')
    login_url = 'login'
    permission_required = 'workers.department_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить структуру/отдел'
        return context


class Chief_View(LoginRequiredMixin, ViewsPermissionsMixin, ListView):
    """Должность"""
    model = Chief
    template_name = 'workers/organization_structure/chief.html'
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


class Chief_Update(LoginRequiredMixin, ViewsPermissionsMixin, UpdateView):
    """Должность. Изменение"""
    model = Chief
    template_name = 'workers/organization_structure/chief_control.html'
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
        return context


class Chief_Add(LoginRequiredMixin, ViewsPermissionsMixin, CreateView):
    """Должность. Добавление"""
    model = Chief
    template_name = 'workers/organization_structure/chief_control.html'
    form_class = Form_Chief_Control
    success_url = reverse_lazy('chief')
    login_url = 'login'
    permission_required = 'workers.chief_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить должность'
        return context
