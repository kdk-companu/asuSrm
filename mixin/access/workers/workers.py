from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from apps.workers.models import WorkerBasic


class WorkersBasicAccessMixin(PermissionRequiredMixin):
    permission_required = None

    def has_permission(self):
        perms = self.request.user.has_perms(self.get_permission_required())
        """Запросы для предоставления прав доступа"""
        try:
            workers = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except Exception as e:
            return False
        if workers and perms:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return redirect('access')
        return super().dispatch(request, *args, **kwargs)


class WorkersAccessMixin:
    """Базовый класс"""
    # Права при установке
    permission_management = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_department = None  # права отдел
    permission_his = None  # права на самостоятельное редактирование
    # Поля страницы пользователя
    workers = None
    workers_subdivision = None
    workers_department = None
    # Поля пользователя
    user = None
    user_subdivision = None
    user_department = None

    def get_workers(self):
        None

    def get_user(self):
        try:
            self.user = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
            self.user_subdivision = self.user.actual_subdivision
            self.user_department = self.user.actual_department
        except Exception as e:
            None

    def has_permission(self):
        self.get_workers()  # Обязательная функция
        self.get_user()  # Обязательная функция
        # Права высшего руководства
        if self.permission_management:
            if self.request.user.has_perm(self.permission_management):
                return True
        # Права на самостоятельное редактирование
        if self.permission_his:
            if self.request.user.has_perm(self.permission_his) and self.user and self.workers:
                if self.user == self.workers:
                    return True
        # Права Управление
        if self.permission_subdivision:
            if self.user_subdivision:
                if self.request.user.has_perm(self.permission_subdivision):
                    if self.workers_subdivision == self.user_subdivision:
                        return True
        # Права отдела
        if self.permission_department:
            if self.user_department:
                if self.request.user.has_perm(self.permission_department):
                    if self.workers_subdivision == self.user_subdivision and self.workers_department == self.user_department:
                        return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return redirect('access')
        return super().dispatch(request, *args, **kwargs)


class WorkersAccessMixin_Worker(WorkersAccessMixin):
    """Класс для работы с моделью Worker"""

    def get_workers(self):
        self.workers = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
            user=self.get_object())
        self.workers_subdivision = self.workers.actual_subdivision
        self.workers_department = self.workers.actual_department


class WorkersAccessMixin_WorkerBasic(WorkersAccessMixin):
    """Класс для работы с моделью WorkerBasic"""

    def get_workers(self):
        self.workers = self.get_object()
        self.workers_subdivision = self.workers.actual_subdivision
        self.workers_department = self.workers.actual_department


class WorkersAccessMixin_WorkerClosed(WorkersAccessMixin):
    """Класс для работы с моделью WorkerClosed"""

    def get_workers(self):
        self.workers = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
            user=self.get_object().user)
        self.workers_subdivision = self.workers.actual_subdivision
        self.workers_department = self.workers.actual_department
