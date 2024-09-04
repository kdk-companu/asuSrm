from django.shortcuts import redirect
from django.urls import reverse
from apps.workers.models import WorkerBasic


class UserAccessMixin:
    """Базовый класс"""
    # Права при установке
    permission_management = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_department = None  # права отдел
    permission_his = None  # права на самостоятельное редактирование
    # Поля пользователя
    user = None
    user_subdivision = None
    user_department = None

    def get_user(self):
        try:
            self.user = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
            self.user_subdivision = self.user.actual_subdivision
            self.user_department = self.user.actual_department
        except Exception as e:
            None

    def has_permission(self):
        # Права высшего руководства
        if self.permission_management:
            if self.request.user.has_perm(self.permission_management):
                return True
        # Права на самостоятельное редактирование
        if self.permission_his:
            if self.request.user.has_perm(self.permission_his) and self.user:
                return True
        # Права Управление
        if self.permission_subdivision:
            if self.user_subdivision:
                if self.request.user.has_perm(self.permission_subdivision):
                    return True
        # Права отдела

        if self.permission_department:
            if self.user_department:
                if self.request.user.has_perm(self.permission_department):
                    return True
        return False

    def dispatch(self, request, *args, **kwargs):
        self.get_user()  # Обязательная функция
        if not self.has_permission():
            return redirect('access')
        return super().dispatch(request, *args, **kwargs)


class UserAccessMixin_PlaningManagement(UserAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        self.get_user()  # Обязательная функция
        if not self.request.user.has_perm(self.permission_management):
            # Права Управление
            if self.permission_subdivision:
                if self.user_subdivision:
                    if self.request.user.has_perm(self.permission_subdivision):
                        return redirect(reverse('workers_planning_subdivision',
                                                kwargs={'subdivision_slug': self.user.actual_subdivision.slug}))
            # Права отдела
            if self.permission_department:

                if self.user_department:

                    if self.request.user.has_perm(self.permission_department):
                        return redirect(reverse('workers_planning_subdivision_department',
                                                kwargs={'subdivision_slug': self.user.actual_subdivision.slug,
                                                        'department_slug': self.user.actual_department.slug}))
            # Права на самостоятельное редактирование
            if self.permission_his:
                if self.request.user.has_perm(self.permission_his):
                    return redirect(reverse('workers_planning_his'))

        return super().dispatch(request, *args, **kwargs)


class UserAccessMixin_WorkersMissingManagement(UserAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        self.get_user()  # Обязательная функция
        if not self.request.user.has_perm(self.permission_management):
            # Права Управление
            if self.permission_subdivision:
                if self.user_subdivision:
                    if self.request.user.has_perm(self.permission_subdivision):
                        return redirect(reverse('workers_planning_subdivision',
                                                kwargs={'subdivision_slug': self.user.actual_subdivision.slug}))
            # Права отдела
            if self.permission_department:

                if self.user_department:

                    if self.request.user.has_perm(self.permission_department):
                        return redirect(reverse('workers_planning_subdivision_department',
                                                kwargs={'subdivision_slug': self.user.actual_subdivision.slug,
                                                        'department_slug': self.user.actual_department.slug}))
            # Права на самостоятельное редактирование
            if self.permission_his:
                if self.request.user.has_perm(self.permission_his):
                    return redirect(reverse('workers_planning_his'))

        return super().dispatch(request, *args, **kwargs)
