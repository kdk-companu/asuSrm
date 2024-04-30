from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404
from django.views.defaults import permission_denied

from apps.workers.models import UserBasic, WorkerBasic, Worker


class ViewsPermissionsMixin(PermissionRequiredMixin):
    """Опредение прав просмотра страницы"""
    permission_user = None
    permission_user_superiors = None

    def has_permission(self):
        perms = self.get_permission_required()
        """Запросы для предоставления прав доступа"""

        if self.permission_user == None and self.permission_user_superiors == None:
            # print('xerrrrrrr')
            return self.request.user.has_perms(perms)
        else:
            # print('lollll')
            own = self.get_object().subdivision == self.request.user.subdivision and self.get_object().department == self.request.user.department
            supervisor_right = own and self.request.user.has_perm(self.permission_user_superiors)
            # Пользователь
            base_righ = (self.get_object() == self.request.user) and self.request.user.has_perm(self.permission_user)
            return supervisor_right or base_righ

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            raise Http404()

        return super().dispatch(request, *args, **kwargs)


class WorkersPermissionsViewMixin(PermissionRequiredMixin):
    """Опредение прав просмотра страницы"""
    permission_required = None

    def has_permission(self):
        worker_employee = WorkerBasic.objects.only('employee').get(user=self.request.user).employee
        if self.request.user.type == UserBasic.Types.WORKER and \
                self.request.user.is_active and \
                worker_employee == WorkerBasic.WORKERS_STATUS.employee_current:
            perms = (self.permission_required,)
        else:
            raise Http404()

        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            raise Http404()

        return super().dispatch(request, *args, **kwargs)


class WorkersPermissionsUpdateMixin(PermissionRequiredMixin):
    """Опредение прав просмотра страницы"""
    permission_required = None  # права (permissions)
    belonging_subdivision = False  # Проверка на принадлежность к управлению
    organization_department = False  # Проверка на принадлежность к отделу

    def has_permission(self):
        # print(self.get_object().pk)
        # worker = Worker.objects.select_related('WorkerBasic').get(user__pk=self.get_object().pk)  # Метод get_object() должен возвращать объект статьи
        # user = Worker.objects.select_related('user').get(user=self.request.user)#Текущий пользователь

        # print(worker.actual_subdivision,'!=',user.actual_subdivision)
        # print(worker.actual_department, '!=', user.actual_department)
        #
        # if self.belonging_subdivision:
        #     if worker.actual_subdivision!=user.actual_subdivision:
        #         raise PermissionDenied()
        # if self.organization_department:
        #     if worker.actual_department!=user.actual_department:
        #         raise PermissionDenied()
        # print('llllllllllllllllllllllllllllllllll')
        # if self.request.user.type == UserBasic.Types.WORKER and \
        #         self.request.user.is_active and \
        #         worker.employee == WorkerBasic.WORKERS_STATUS.employee_current:
        #     perms = (self.permission_required,)
        # else:
        #     raise PermissionDenied("")
        # raise PermissionDenied("")
        # return self.request.user.has_perms(perms)
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


####FINAL
class WorkerPermissionsViewAddMixin(PermissionRequiredMixin):
    """Просмотр и создание к базе Worker"""
    permission_required = None  # права (permissions)

    def has_permission(self):
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)


####FINAL
class WorkerPermissionsUpdateMixin(PermissionRequiredMixin):
    """Редактирование к базе Worker"""
    permission_required = None  # права (permissions)
    belonging_subdivision = False  # Проверка на принадлежность к управлению
    belonging_department = False  # Проверка на принадлежность к отделу
    permission_his_required = None  # Права на редактирования самого себя
    belonging_his = False  # Самостоятельно можно редактировать

    def has_permissions(self):
        if self.belonging_his:
            if str(self.get_object()) == str(self.request.user):
                # Проверка на разрешения редактирование данных пользователем
                self.permission_required = self.permission_his_required
                perms = self.get_permission_required()
                return self.request.user.has_perms(perms)

        # Запрет пользователю редактировать информацию о себе
        if str(self.get_object()) == str(self.request.user):
            return False

        # Проверка на принадлежность к управлению и отделу
        if self.belonging_subdivision or self.organization_department:
            worker = WorkerBasic.objects.get(user__pk=self.get_object())  # Старница пользователя
            user = WorkerBasic.objects.get(user=self.request.user)  # Текущий пользователь
            if self.belonging_subdivision:
                if worker.actual_subdivision != user.actual_subdivision:
                    return False
            if self.belonging_department:
                if worker.actual_department != user.actual_department:
                    return False

        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise PermissionDenied()
        return super(WorkerPermissionsUpdateMixin, self).dispatch(
            request, *args, **kwargs)


####FINAL
class WorkerBasicPermissionsUpdateMixin(PermissionRequiredMixin):
    """Редактирование к базе Worker"""
    permission_required = None  # права (permissions)
    belonging_subdivision = False  # Проверка на принадлежность к управлению
    belonging_department = False  # Проверка на принадлежность к отделу
    permission_his_required = None  # Права на редактирования самого себя
    belonging_his = False  # Самостоятельно можно редактировать

    def has_permissions(self):

        if self.belonging_his:
            if str(self.get_object()) == str(self.request.user):
                # Проверка на разрешения редактирование данных пользователем
                self.permission_required = self.permission_his_required
                perms = self.get_permission_required()
                return self.request.user.has_perms(perms)

        # Запрет пользователю редактировать информацию о себе
        if str(self.get_object()) == str(self.request.user):
            return False

        # Проверка на принадлежность к управлению и отделу
        if self.belonging_subdivision or self.organization_department:
            worker = self.get_object()  # Старница пользователя
            user = WorkerBasic.objects.get(user=self.request.user)  # Текущий пользователь
            if self.belonging_subdivision:
                if worker.actual_subdivision != user.actual_subdivision:
                    return False
            if self.belonging_department:
                if worker.actual_department != user.actual_department:
                    return False

        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise PermissionDenied()
        return super(WorkerBasicPermissionsUpdateMixin, self).dispatch(
            request, *args, **kwargs)


####FINAL
class WorkerClosedPermissionsUpdateMixin(PermissionRequiredMixin):
    """Редактирование к базе Worker"""
    permission_required = None  # права (permissions)
    belonging_subdivision = False  # Проверка на принадлежность к управлению
    belonging_department = False  # Проверка на принадлежность к отделу
    permission_his_required = None  # Права на редактирования самого себя
    belonging_his = False  # Самостоятельно можно редактировать

    def has_permissions(self):
        if self.belonging_his:
            if str(self.get_object()) == str(self.request.user):
                # Проверка на разрешения редактирование данных пользователем
                self.permission_required = self.permission_his_required
                perms = self.get_permission_required()
                return self.request.user.has_perms(perms)

        # Запрет пользователю редактировать информацию о себе
        if str(self.get_object()) == str(self.request.user):
            return False

        # Проверка на принадлежность к управлению и отделу
        if self.belonging_subdivision or self.organization_department:
            worker = WorkerBasic.objects.get(user=self.get_object().user)  # Старница пользователя
            user = WorkerBasic.objects.get(user=self.request.user)  # Текущий пользователь
            print('xerrr1')
            if self.belonging_subdivision:
                if worker.actual_subdivision != user.actual_subdivision:
                    return False
            print('xerrr2')
            if self.belonging_department:
                print('stepppp')
                if worker.actual_department != user.actual_department:
                    return False
            print('xerrr3')
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise PermissionDenied()
        return super(WorkerClosedPermissionsUpdateMixin, self).dispatch(
            request, *args, **kwargs)

