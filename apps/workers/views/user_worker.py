import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages

from apps.workers.forms import Search_Filter,  Search_User_Filter, Workers_Add_Form, \
    Workers_Form_Upload_Images, Workers_Form_UpdatePassword, Workers_Form_PasswordChange, WorkerBasic_Form_Change, \
    WorkerClosed_Form_Change, WorkerClosed_Form_Upload_Passport, WorkerClosed_Form_Upload_Snils, \
    WorkerClosed_Form_Upload_Inn, WorkerClosed_Form_Upload_Archive, WorkerClosed_Form_Upload_Signature, \
    Workers_Form_Change
from apps.workers.models import Worker, WorkerBasic, WorkerClosed
from mixin.workers_right import WorkerPermissionsBased,WorkerPermissionsUpdateMixin, WorkerBasicPermissionsUpdateMixin, WorkerClosedPermissionsUpdateMixin


class Workers(LoginRequiredMixin, WorkerPermissionsBased, ListView):
    """Вывод всех пользователей"""
    model = WorkerBasic
    template_name = 'user/worker/workers.html'
    paginate_by = 40
    context_object_name = 'workers'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.Worker_view'

    def get_queryset(self):
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        if self.request.GET:
            if 'search' in self.request.GET:
                form = Search_Filter(self.request.GET)
                if form.is_valid():
                    if len(self.request.GET.get('search')) != 0:
                        search = str(self.request.GET.get('search')).replace("+", "")
                        filters |= Q(**{f'{"user__surname__iregex"}': search})
                        filters |= Q(**{f'{"user__name__iregex"}': search})
                        filters |= Q(**{f'{"user__patronymic__iregex"}': search})
                        filters |= Q(**{f'{"user__phone__iregex"}': search})
                        filters |= Q(**{f'{"user__email__iregex"}': search})
        filters &= Q(**{f'{"employee"}': "employee_current"})
        return super().get_queryset().filter(filters).select_related('actual_subdivision',
                                                                     'actual_department', 'chief', 'user').only(
            'actual_subdivision__name',
            'actual_department__name', 'chief__name', 'user__surname', 'user__name', 'user__patronymic', 'user__slug',
            'user__phone', 'user__email', 'user__image_smol',).order_by('user__surname')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Сотрудники'
        context['search_filter'] = Search_Filter(self.request.GET)
        # Сохранение ссылки в pagination
        if 'search' in self.request.GET:
            url_page = format((self.request.GET['search']).replace("+", ""))
            context['url_filter'] = "?search={0}".format(url_page)
        return context


class Workers_Filter(LoginRequiredMixin, WorkerPermissionsBased, ListView):
    """Вывод всех пользователей"""
    model = WorkerBasic
    template_name = 'user/worker/workers_filter.html'
    paginate_by = 40
    context_object_name = 'workers'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.Worker_view'

    def get_queryset(self):
        filters = Q()
        if self.request.GET:
            form = Search_User_Filter(self.request.GET)
            if form.is_valid():
                if 'subdivision' in self.request.GET:
                    subdivision = str(self.request.GET['subdivision']).replace("+", "")
                    if subdivision != '':
                        filters &= Q(**{f'{"actual_subdivision__slug"}': subdivision})
                if 'department' in self.request.GET:
                    department = str(self.request.GET['department']).replace("+", "")
                    if department != '':
                        filters &= Q(**{f'{"actual_department__slug"}': department})
                if 'chief' in self.request.GET:
                    chief = str(self.request.GET['chief']).replace("+", "")
                    if chief != '':
                        filters &= Q(**{f'{"chief"}': chief})

        filters &= Q(**{f'{"employee"}': "employee_current"})

        return super().get_queryset().filter(filters).select_related('actual_subdivision',
                                                                     'actual_department', 'chief', 'user').only(
            'actual_subdivision__name',
            'actual_department__name', 'chief__name', 'user__surname', 'user__name', 'user__patronymic', 'user__slug',
            'user__phone', 'user__email', 'user__image_smol').order_by('user__surname')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Сотрудники'
        context['search_user_filter'] = Search_User_Filter(self.request.GET)
        if self.request.GET:
            organization_subdivision = ''
            organization_department = ''
            chief = ''
            try:
                organization_subdivision = self.request.GET['subdivision']
                organization_department = self.request.GET['department']
                chief = self.request.GET['chief']
            except Exception as e:
                pass
            context['url_filter'] = '?organization_subdivision={0}&organization_department={1}&chief={0}'.format(
                organization_subdivision, organization_department, chief)

        return context


class Workers_Add(LoginRequiredMixin, WorkerPermissionsBased, CreateView):
    """Добавление нового сотрудника"""
    model = Worker
    template_name = 'user/worker/editing/workers_add.html'
    form_class = Workers_Add_Form
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.Worker_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить сотрудника'
        context['title_page'] = 'Добавить'
        return context

    def get_success_url(self):
        super()
        # Получение последнего пользователя
        upadate_user = Worker.objects.latest('id')
        # Исключаем ошибки при создании пользователя
        try:
            # Создание папок для нового пользователя
            folder_user = "media/user/" + str(upadate_user.pk)
            folder_user_images = "media/user/" + str(upadate_user.pk) + "/images/"
            folder_save_files = "media/user/" + str(upadate_user.pk) + "/files/"
            os.mkdir(folder_user)
            os.mkdir(folder_user_images)
            os.mkdir(folder_save_files)
        except Exception:
            pass
        # Добавить управление и отдел при добавлении сотрудника
        try:
            authorized_user = WorkerBasic.objects.get(user__pk=self.request.user.pk)  # Текущий пользователь
            new_user = WorkerBasic.objects.get(user=upadate_user)
            new_user.organization_subdivision = authorized_user.organization_subdivision
            new_user.organization_department = authorized_user.organization_department
            new_user.actual_subdivision = authorized_user.actual_subdivision
            new_user.actual_department = authorized_user.actual_department
            new_user.chief = authorized_user.chief
            new_user.save()

        except:
            pass
        return reverse('workers_basic_change', kwargs={'workers_slug': upadate_user.slug})


class Workers_DetailView(LoginRequiredMixin, WorkerPermissionsBased, DetailView):
    """Подробная информация о сотруднике"""
    model = Worker
    template_name = 'user/worker/workers_detail.html'

    slug_url_kwarg = 'workers_slug'
    context_object_name = 'worker'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.Worker_view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Страница сотрудника'
        #########
        ## Базовые запросы
        #########
        user = None  # Если зайдет пользователь не из сотрудников
        try:
            user = WorkerBasic.objects.select_related('actual_subdivision', 'actual_department').get(
                user=self.request.user)  # проверить на оптимизацию
        except:
            pass
        # Страница пользователя
        workerBasic = WorkerBasic.objects.select_related('organization_subdivision', 'organization_department',
                                                         'actual_subdivision', 'actual_department', 'chief').get(
            user__slug=self.kwargs.get(self.slug_url_kwarg))  # проверить на оптимизацию
        # Сверка управлений и отделов
        user_subdivision = False
        user_subdivision_department = False
        user_сurrent = False
        if user:
            user_subdivision = user.actual_subdivision == workerBasic.actual_subdivision
            user_subdivision_department = user_subdivision and user.actual_department == workerBasic.actual_department
            user_сurrent = user == workerBasic
        context['permission_user_сurrent'] = user_сurrent
        context['permission_missing'] = user_сurrent and self.request.user.has_perm('workers.WorkersMissing_his_view')

        #########
        ## Пользователь. Сотрудник.
        #########
        context['permission_worker_change'] = False  # Изменять всю информацию
        context['permission_worker_change_password'] = False  # Обновлять пароль. Не для себя.
        context['permission_worker_change_permission'] = False  # Обновлять права доступа. Не для себя.
        # Вся информация
        if user_сurrent:
            if self.request.user.has_perm('workers.Worker_his_change'):
                context['permission_worker_change'] = True
        else:
            if self.request.user.has_perm('workers.Worker_change') and user_subdivision_department:
                context['permission_worker_change'] = True
            elif self.request.user.has_perm('workers.Worker_change_subdivision') and user_subdivision:
                context['permission_worker_change'] = True
            elif self.request.user.has_perm('workers.Worker_change_all'):
                context['permission_worker_change'] = True
        if not user_сurrent:
            # Пароль
            if self.request.user.has_perm('workers.Worker_change_password') and user_subdivision_department:
                context['permission_worker_change_password'] = True
            elif self.request.user.has_perm('workers.Worker_change_password_subdivision') and user_subdivision:
                context['permission_worker_change_password'] = True
            elif self.request.user.has_perm('workers.Worker_change_password_all'):
                context['permission_worker_change_password'] = True
            # Права доступа
            if self.request.user.has_perm('workers.Worker_change_permission') and user_subdivision_department:
                context['permission_worker_change_permission'] = True
            elif self.request.user.has_perm('workers.Worker_change_permission_subdivision') and user_subdivision:
                context['permission_worker_change_permission'] = True
            elif self.request.user.has_perm('workers.Worker_change_permission_all'):
                context['permission_worker_change_permission'] = True

        #########
        ## Базовая информация о сотрудниках
        #########
        context['permission_workerBasic_view'] = False  # Просматривать всю информацию
        context['permission_workerBasic_change'] = False  # Изменять всю информацию
        # Разрешение на просмотр
        if self.request.user.has_perm('workers.WorkerBasic_view_all') or \
                self.request.user.has_perm('workers.WorkerBasic_view_subdivision') and user_subdivision or \
                self.request.user.has_perm('workers.WorkerBasic_view') and user_subdivision_department:
            context['basic'] = workerBasic
            context['permission_workerBasic_view'] = True

        # Разрешение на просмотр
        if user_сurrent:
            if self.request.user.has_perm('workers.WorkerBasic_his_change'):
                context['permission_workerBasic_change'] = True
        else:
            if self.request.user.has_perm('workers.WorkerBasic_change') and user_subdivision_department:
                context['permission_workerBasic_change'] = True
            elif self.request.user.has_perm('workers.WorkerBasic_change_subdivision') and user_subdivision:
                context['permission_workerBasic_change'] = True
            elif self.request.user.has_perm('workers.WorkerBasic_change_all'):
                context['permission_workerBasic_change'] = True
        #########
        ## Закрытая информация о сотрудники
        #########
        context['permission_workerClosed_view'] = False  # Просматривать всю информацию
        context['permission_workerClosed_change'] = False  # Изменять всю информацию
        # Разрешение на просмотр
        if self.request.user.has_perm('workers.WorkerClosed_view_all') or \
                self.request.user.has_perm('workers.WorkerClosed_view_subdivision') and user_subdivision or \
                self.request.user.has_perm('workers.WorkerClosed_view') and user_subdivision_department:
            context['closed'] = WorkerClosed.objects.get(user__slug=self.kwargs.get(self.slug_url_kwarg))
            context['permission_workerClosed_view'] = True
        # Разрешение на редактирование
        if user_сurrent:
            if self.request.user.has_perm('workers.WorkerClosed_his_change'):
                context['permission_workerClosed_change'] = True
        else:
            if self.request.user.has_perm('workers.WorkerClosed_change') and user_subdivision_department:
                context['permission_workerClosed_change'] = True
            elif self.request.user.has_perm('workers.WorkerClosed_change_subdivision') and user_subdivision:
                context['permission_workerClosed_change'] = True
            elif self.request.user.has_perm('workers.WorkerClosed_change_all'):
                context['permission_workerClosed_change'] = True
        return context


class Workers_Change(LoginRequiredMixin, WorkerPermissionsUpdateMixin, UpdateView):
    model = Worker
    template_name = 'user/worker/editing/workers_change.html'

    form_class = Workers_Form_Change
    login_url = 'login'

    permission = 'workers.Worker_change_all'  # права высшее руководство
    permission_his = 'workers.Worker_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.Worker_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.Worker_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пользователя'
        context['user'] = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_change', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Change_Password(LoginRequiredMixin, PasswordChangeView):
    """Изменить только сам сотрудник"""
    template_name = 'user/worker/editing/workers_password_change.html'
    form_class = Workers_Form_PasswordChange
    redirect_field_name = ''

    login_url = 'login'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить пароль.'
        return context

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect('')


class Workers_Update_Password(LoginRequiredMixin, WorkerPermissionsUpdateMixin, UpdateView):
    """Изменить только по правам"""
    model = WorkerBasic
    template_name = 'user/worker/editing/workers_password_update.html'
    form_class = Workers_Form_UpdatePassword
    redirect_field_name = ''

    login_url = 'login'
    permission = 'workers.Worker_change_password_all'  # права высшее руководство
    permission_subdivision = 'workers.Worker_change_password_subdivision'  # права Управление
    permission_subdivision_department = 'workers.Worker_change_password'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановления пароля.'
        context['user'] = WorkerBasic.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        if 'workers_slug' in self.kwargs:
            slug = self.kwargs['workers_slug']
        return reverse('workers_update_password', kwargs={'workers_slug': slug})

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Данные сохранены успешно')
        return HttpResponseRedirect(self.get_success_url())


class Workers_Image(LoginRequiredMixin, WorkerPermissionsUpdateMixin, UpdateView):
    """Добавление аватарок на сайт"""
    model = Worker
    template_name = 'user/worker/editing/workers_images.html'
    form_class = Workers_Form_Upload_Images

    login_url = 'login'
    permission = 'workers.Worker_change_all'  # права высшее руководство
    permission_his = 'workers.Worker_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.Worker_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.Worker_change'  # права Управление и отдел

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form_check = Workers_Form_Upload_Images(request.POST, request.FILES)
        if form.is_valid() and len(form_check.files.dict()):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка аватарки.'
        context['workers'] = Worker.objects.get(slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_image', kwargs={'workers_slug': self.kwargs['workers_slug']})


class User_Permissions(LoginRequiredMixin, WorkerPermissionsUpdateMixin, DetailView):
    """Изменение прав доступа"""
    model = Worker
    template_name = 'user/worker/editing/workers_permissions.html'

    login_url = 'login'
    permission = 'workers.Worker_change_permission_all'  # права высшее руководство
    permission_subdivision = 'workers.Worker_change_permission_subdivision'  # права Управление
    permission_subdivision_department = 'workers.Worker_change_permission'  # права Управление и отдел

    def get_object(self, queryset=None):
        instance = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def post(self, request, *args, **kwargs):
        if request.POST.get("permission_add"):
            permission = Permission.objects.get(codename=request.POST.get("permission_add"))
            user = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
            user.user_permissions.add(permission)
        elif request.POST.get("permission_remove"):
            permission = Permission.objects.get(codename=request.POST.get("permission_remove"))
            user = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
            user.user_permissions.remove(permission)

        return redirect('workers_permissions', *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование прав пользователя.'

        # Сотрудник
        worker = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))  # Текущие права пользователя
        context['worker'] = worker  # Текущие права пользователя
        worker_permissions = dict()
        for perm in worker.user_permissions.all():
            worker_permissions[perm.codename] = perm.name
        context['worker_permissions'] = worker_permissions  # Текущие права пользователя

        worker_group_permissions = dict()
        try:
            for perm in worker.groups.first().permissions.all():
                worker_group_permissions[perm.codename] = perm.name
            context['worker_group_permissions'] = worker_group_permissions  # Текущие групповые права пользователя
        except:
            pass
        worker_all_permissions = {**worker_permissions, **worker_group_permissions}
        # Пользователь
        user_permissions = dict()
        for perm in self.request.user.user_permissions.all():
            user_permissions[perm.codename] = perm.name
        context['user_permissions'] = user_permissions  # Текущие права пользователя
        user_group_permissions = dict()
        try:
            for perm in self.request.user.groups.first().permissions.all():
                user_group_permissions[perm.codename] = perm.name
            context['user_group_permissions'] = user_group_permissions  # Текущие групповые права пользователя
        except:
            pass

        user_all_permissions = {**user_permissions, **user_group_permissions}

        user_add_permissions = user_all_permissions.copy()

        try:
            for worker_all_permission in worker_all_permissions:
                del user_add_permissions[worker_all_permission]
        except:
            print('Непонятная ошибка. Workers. User_Permissions')
            pass
        context['user_add_permissions'] = user_add_permissions

        # worker_permissions
        user_remove_permissions = dict()
        for perm in worker_permissions:
            if user_all_permissions[perm]:
                user_remove_permissions[perm] = worker_permissions[perm]

        context['user_remove_permissions'] = user_remove_permissions

        return context


class WorkerBasic_Change(LoginRequiredMixin, WorkerBasicPermissionsUpdateMixin, UpdateView):
    model = WorkerBasic
    template_name = 'user/worker/editing/workerbasic_change.html'

    form_class = WorkerBasic_Form_Change
    login_url = 'login'

    permission = 'workers.WorkerBasic_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerBasic_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerBasic_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerBasic_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerBasic.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование. Базовая информация.'
        context['user'] = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_basic_change', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkerClosed_Change(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, UpdateView):
    model = WorkerClosed
    template_name = 'user/worker/editing/workerclosed_change.html'

    form_class = WorkerClosed_Form_Change
    login_url = 'login'

    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование. Закрытая информация.'
        context['user'] = Worker.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_closed_change', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkerClosed_Passport(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, UpdateView):
    """Добавление паспорта на сайт"""
    model = WorkerClosed
    template_name = 'user/worker/editing/workerclosed_passport.html'
    form_class = WorkerClosed_Form_Upload_Passport

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.passport_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка паспорта.'
        context['workers'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_passport', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkerClosed_Passport_Delete(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, DetailView):
    """Удаление паспорта """
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    def post(self, request, *args, **kwargs):
        # Удаляем паспорт
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.passport_scan.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    def form_valid(self, form):
        # Удаление старых файлов
        file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.passport_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление паспорта.'
        context['info'] = 'паспорт.'
        context['file'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class WorkerClosed_Snils(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, UpdateView):
    """Добавление снилс на сайт"""
    model = WorkerClosed
    template_name = 'user/worker/editing/workerclosed_snils.html'
    form_class = WorkerClosed_Form_Upload_Snils

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.snils_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка снилс.'
        context['workers'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_snils', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkerClosed_Snils_Delete(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, DetailView):
    """Удаление снилс"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    def post(self, request, *args, **kwargs):
        # Удаляем паспорт
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.snils_scan.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление снилс.'
        context['info'] = 'снилс.'
        context['file'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class WorkerClosed_Inn(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, UpdateView):
    """Добавление инн на сайт"""
    model = WorkerClosed
    template_name = 'user/worker/editing/workerclosed_inn.html'
    form_class = WorkerClosed_Form_Upload_Inn

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.inn_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка инн.'
        context['workers'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_inn', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkerClosed_Inn_Delete(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, DetailView):
    """Удаление инн"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    def post(self, request, *args, **kwargs):
        # Удаляем инн
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.inn_scan.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление инн.'
        context['info'] = 'инн.'
        context['file'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class WorkerClosed_Archive(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, UpdateView):
    """Добавление архива на сайт"""
    model = WorkerClosed
    template_name = 'user/worker/editing/workerclosed_archive.html'
    form_class = WorkerClosed_Form_Upload_Archive

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.archive_documents_employment.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка архива.'
        context['workers'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_archive', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkerClosed_Archive_Delete(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, DetailView):
    """Удаление архива"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    def post(self, request, *args, **kwargs):
        # Удаляем архив
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.archive_documents_employment.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление архива.'
        context['info'] = 'архив.'
        context['file'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class WorkerClosed_Signature(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, UpdateView):
    """Добавление подписи на сайт"""
    model = WorkerClosed
    template_name = 'user/worker/editing/workerclosed_signature.html'
    form_class = WorkerClosed_Form_Upload_Signature

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка подписи.'
        context['workers'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_signature', kwargs={'workers_slug': self.kwargs['workers_slug']})


class WorkerClosed_Signature_Delete(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, DetailView):
    """Удаление подписи"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

    login_url = 'login'
    permission = 'workers.WorkerClosed_change_all'  # права высшее руководство
    permission_his = 'workers.WorkerClosed_his_change'  # права редактирования самого себя
    permission_subdivision = 'workers.WorkerClosed_change_subdivision'  # права Управление
    permission_subdivision_department = 'workers.WorkerClosed_change'  # права Управление и отдел

    def post(self, request, *args, **kwargs):
        # Удаляем архив
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.signature_example.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление подписи.'
        context['info'] = 'подпись.'
        context['file'] = WorkerClosed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context
