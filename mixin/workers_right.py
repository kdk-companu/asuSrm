from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from apps.workers.models import WorkerBasic, WorkersMissing




class WorkerPermissionsUpdateMixin:
    """Редактирование к базе Worker"""
    permission = None  # права высшее руководство
    permission_his = None  # права редактирования самого себя
    permission_subdivision = None  # права Управление
    permission_subdivision_department = None  # права Управление и отдел

    def has_permission(self):
        user = None
        worker = None
        if self.request.user.has_perm(self.permission):
            return True
        else:
            user = WorkerBasic.objects.values('user', 'actual_subdivision', 'actual_department').get(
                user__pk=self.get_object())
            try:
                worker = WorkerBasic.objects.values('user', 'actual_subdivision', 'actual_department').get(
                    user=self.request.user)
            except Exception:
                pass
            if user and worker:
                # Проверка на саморедактирования
                if self.permission_his:
                    if self.request.user.has_perm(self.permission_his) and user['user'] == worker['user']:
                        return True
                # Проверка на управление
                if self.request.user.has_perm(self.permission_subdivision) \
                        and user['user'] != worker['user'] \
                        and user['actual_subdivision'] == worker['actual_subdivision']:
                    return True
                # Проверка на управление и отдел
                if self.request.user.has_perm(self.permission_subdivision_department) \
                        and user['user'] != worker['user'] \
                        and user['actual_subdivision'] == worker['actual_department'] \
                        and user['actual_department'] == worker['actual_subdivision']:
                    return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)




class WorkerPlaningPermissionsViewMixin:
    """Просмотр к странице Planing"""
    permission = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_subdivision_department = None  # права Управление и отдел
    worker = None

    def has_permission(self):
        if self.request.user.has_perm(self.permission):
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.worker = WorkerBasic.objects.only('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass
        if self.worker:
            if self.request.user.has_perm(self.permission_subdivision_department):
                if self.worker.actual_subdivision and self.worker.actual_department:
                    return redirect(reverse('workers_planning_subdivision_department',
                                            kwargs={'subdivision_slug': self.worker.actual_subdivision.slug,
                                                    'department_slug': self.worker.actual_department.slug}))

            if self.request.user.has_perm(self.permission_subdivision):
                if self.worker.actual_subdivision:
                    return redirect(reverse('workers_planning_subdivision',
                                            kwargs={'subdivision_slug': self.worker.actual_subdivision.slug}))

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)


class WorkerPlaningSubdivisionPermissionsViewMixin:
    """Просмотр к странице Planing"""
    permission = None  # права Управление и отдел
    worker = None

    def has_permission(self):
        if self.worker:
            if self.request.user.has_perm(self.permission):
                slug_subdivision = self.kwargs.get('subdivision_slug')
                if self.worker.actual_subdivision:
                    if self.worker.actual_subdivision.slug == slug_subdivision:
                        return True
        return False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.worker = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)


class WorkerPlaningDepartmentPermissionsViewMixin:
    """Просмотр к странице Planing"""
    permission = None  # права Управление и отдел
    worker = None

    def has_permission(self):
        if self.worker:
            if self.request.user.has_perm(self.permission):
                slug_subdivision = self.kwargs.get('subdivision_slug')
                slug_department = self.kwargs.get('department_slug')
                if self.worker.actual_subdivision and self.worker.actual_department:
                    if self.worker.actual_subdivision.slug == slug_subdivision and self.worker.actual_department.slug == slug_department:
                        return True
        return False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.worker = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)


class WorkerMissingPermissionsViewMixin:
    """Просмотр к странице Planing"""
    permission = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_subdivision_department = None  # права Управление и отдел
    worker = None

    def has_permission(self):
        if self.request.user.has_perm(self.permission) or self.request.user.has_perm(
                self.permission_subdivision) or self.request.user.has_perm(self.permission_subdivision_department):
            return True

        return False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.worker = WorkerBasic.objects.only('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass

        if self.worker:
            if not self.request.user.has_perm(self.permission):
                if self.request.user.has_perm(self.permission_subdivision):
                    return redirect(reverse('workers_missing_subdivision',
                                            kwargs={'subdivision_slug': self.worker.actual_subdivision.slug}))
                if self.request.user.has_perm(self.permission_subdivision_department):
                    return redirect(reverse('workers_missing_subdivision_department',
                                            kwargs={'subdivision_slug': self.worker.actual_subdivision.slug,
                                                    'department_slug': self.worker.actual_department.slug}))

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)


class WorkerMissingSubdivisionPermissionsViewMixin:
    """Просмотр к странице Planing"""
    permission = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_subdivision_department = None  # права Управление и отдел
    worker = None

    def has_permission(self):
        if self.worker:
            if self.request.user.has_perm(self.permission_subdivision):
                slug_subdivision = self.kwargs.get('subdivision_slug')
                if self.worker.actual_subdivision.slug == slug_subdivision:
                    return True
        return False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.worker = WorkerBasic.objects.only('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)


class WorkerMissingDepartmentPermissionsViewMixin:
    """Просмотр к странице Planing"""
    permission = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_subdivision_department = None  # права Управление и отдел
    worker = None

    def has_permission(self):
        if self.worker:
            if self.request.user.has_perm(self.permission_subdivision_department):
                slug_subdivision = self.kwargs.get('subdivision_slug')
                slug_department = self.kwargs.get('department_slug')
                if self.worker.actual_subdivision.slug == slug_subdivision and self.worker.actual_department.slug == slug_department:
                    return True
        return False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.worker = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)


class WorkerMissingUpdateDepartmentPermissionsViewMixin:
    """Просмотр к странице Planing"""
    permission = None  # права высшее руководство
    permission_subdivision = None  # права Управление
    permission_subdivision_department = None  # права Управление и отдел
    worker = None

    def has_permission(self):
        if self.worker:
            if self.request.user.has_perm(self.permission_subdivision_department):
                slug_subdivision = self.get_object().user.actual_subdivision.slug
                slug_department = self.get_object().user.actual_department.slug
                if self.worker.actual_subdivision.slug == slug_subdivision and self.worker.actual_department.slug == slug_department:
                    return True
        return False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.worker = WorkerBasic.objects.select_related('user', 'actual_subdivision', 'actual_department').get(
                user=self.request.user)
        except:
            pass

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)


class WorkerMissingHisPermissionsUpdateMixin:
    """Просмотр к странице Planing"""
    permission = None  # права высшее руководство

    workerBasic = None
    workersMissing = None

    def has_permission(self):
        if self.workerBasic:
            if self.request.user.has_perm(self.permission):
                # PK - нужен для редактирования если нет то создание
                if self.workersMissing:
                    if self.workersMissing.user.slug == self.workerBasic.user.slug:
                        return True
                else:
                    workers_slug = self.kwargs.get('workers_slug')
                    if self.workerBasic.user.slug == workers_slug:
                        return True
        return False

    def dispatch(self, request, *args, **kwargs):
        #PK - нужен для редактирования если нет то создание
        if self.kwargs.get('pk'):
            self.workersMissing = WorkersMissing.objects.select_related('user').get(pk=self.kwargs['pk']).user
        try:
            self.workerBasic = WorkerBasic.objects.select_related('user', ).get(user=self.request.user)
        except:
            pass

        if not self.has_permission():
            return HttpResponseForbidden("Вам отказано в доступе")
        return super().dispatch(request, *args, **kwargs)
