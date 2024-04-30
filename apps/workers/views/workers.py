import os
from datetime import time

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages

from apps.workers.forms import Search_Filter, Group_Form_Permissions, Search_User_Filter, Workers_Add_Form, \
    Workers_Form_Upload_Images, Workers_Form_UpdatePassword, Workers_Form_PasswordChange, WorkerBasic_Form_Change, \
    WorkerClosed_Form_Change, WorkerClosed_Form_Upload_Passport, WorkerClosed_Form_Upload_Snils, \
    WorkerClosed_Form_Upload_Inn, WorkerClosed_Form_Upload_Archive, WorkerClosed_Form_Upload_Signature, \
    Workers_Form_Change
from apps.workers.models import Worker, WorkerBasic, WorkerClosed, UserBasic
from mixin.user_right import WorkersPermissionsUpdateMixin, WorkersPermissionsViewMixin, WorkerPermissionsUpdateMixin, \
    WorkerPermissionsViewAddMixin, WorkerBasicPermissionsUpdateMixin, WorkerClosedPermissionsUpdateMixin


class Workers(LoginRequiredMixin, WorkerPermissionsViewAddMixin, ListView):
    """Вывод всех пользователей"""
    model = WorkerBasic
    template_name = 'workers/workers.html'
    paginate_by = 40
    context_object_name = 'workers'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.UserWorker_view'
    belonging_subdivision = False  # Проверка на принадлежность к управлению
    organization_department = False  # Проверка на принадлежность к отделу

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

        return super().get_queryset().filter(filters).select_related(
            'organization_subdivision',
            'organization_department',
            'actual_subdivision', 'actual_department', 'chief', 'user')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пользователи'
        context['search_filter'] = Search_Filter(self.request.GET)
        # Сохранение ссылки в pagination
        if 'search' in self.request.GET:
            url_page = format((self.request.GET['search']).replace("+", ""))
            context['url_filter'] = "?search={0}".format(url_page)
        return context


class Workers_Filter(LoginRequiredMixin, WorkersPermissionsViewMixin, ListView):
    """Вывод всех пользователей"""
    model = WorkerBasic
    template_name = 'workers/workers_filter.html'
    paginate_by = 40
    context_object_name = 'workers'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.user_view'

    # def get_queryset(self):
    #     filters = Q()
    #     if self.request.GET:
    #         form = Search_User_Filter(self.request.GET)
    #         if form.is_valid():
    #             if 'organization_subdivision' in self.request.GET:
    #                 organization_subdivision = str(self.request.GET['organization_subdivision']).replace("+", "")
    #                 if organization_subdivision != '':
    #                     filters |= Q(**{f'{"organization_subdivision"}': organization_subdivision})
    #             if 'organization_department' in self.request.GET:
    #                 organization_department = str(self.request.GET['organization_department']).replace("+", "")
    #                 if organization_department != '':
    #                     filters |= Q(**{f'{"organization_department"}': organization_department})
    #             if 'chief' in self.request.GET:
    #                 chief = str(self.request.GET['chief']).replace("+", "")
    #                 if chief != '':
    #                     filters |= Q(**{f'{"chief"}': chief})
    #
    #     filters &= Q(**{f'{"user__employee"}': "employee_current"})
    #
    #     return super().get_queryset().filter(filters).select_related(
    #         'user',
    #         'organization_subdivision',
    #         'organization_department',
    #         'actual_subdivision',
    #         'actual_department',
    #         'chief',
    #     )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пользователи'
        # context['search_user_filter'] = Search_User_Filter(self.request.GET)
        # if self.request.GET:
        #     organization_subdivision = ''
        #     organization_department = ''
        #     chief = ''
        #     try:
        #         organization_subdivision = self.request.GET['organization_subdivision']
        #         organization_department = self.request.GET['organization_department']
        #         chief = self.request.GET['chief']
        #     except Exception as e:
        #         pass
        #     context['url_filter'] = '?organization_subdivision={0}&organization_department={1}&chief={0}'.format(
        #         organization_subdivision, organization_department, chief)

        return context


class Workers_Add(LoginRequiredMixin, WorkerPermissionsViewAddMixin, CreateView):
    """Добавление нового сотрудника"""
    model = Worker
    template_name = 'workers/workers_settings/workers_add.html'
    form_class = Workers_Add_Form
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.UserWorker_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление пользователя'
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


class Workers_DetailView(LoginRequiredMixin, WorkersPermissionsViewMixin, DetailView):
    """Добавление нового сотрудника"""
    model = Worker
    template_name = 'workers/workers_views.html'

    slug_url_kwarg = 'workers_slug'
    context_object_name = 'worker'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.UserWorker_view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Страница пользователя'

        user = WorkerBasic.objects.select_related('actual_subdivision', 'actual_department').get(user=self.request.user)
        workerBasic = WorkerBasic.objects.select_related('organization_subdivision', 'organization_department',
                                                         'actual_subdivision', 'actual_department', 'chief').get(
            user__slug=self.kwargs.get(self.slug_url_kwarg))
        # Проверка базовых прав
        user_subdivision_department = user.actual_subdivision == workerBasic.actual_subdivision and user.actual_department == workerBasic.actual_department
        if user_subdivision_department:
            if self.request.user.has_perm('workers.UserWorker_change'):
                context['worker_permission'] = True
            if (self.request.user.has_perm('workers.UserWorker_his_change') and workerBasic == user):
                context['worker_permission'] = True
            if (not self.request.user.has_perm('workers.UserWorker_his_change') and workerBasic == user):
                context['worker_permission'] = False
                # Права доступа
            if self.request.user.has_perm('workers.UserBasic_permission'):
                context['permission'] = True

        # # Провеврка на права просмотра страницы базовой информации
        if self.request.user.has_perm('workers.WorkerBasic_view'):
            if user_subdivision_department:
                context['basic'] = workerBasic
                if self.request.user.has_perm('workers.WorkerBasic_change'):
                    context['basic_permission'] = True
                if (self.request.user.has_perm('workers.WorkerBasic_his_change') and workerBasic == user):
                    context['basic_permission'] = True
                if (not self.request.user.has_perm('workers.WorkerBasic_his_change') and workerBasic == user):
                    context['basic_permission'] = False
        # Провеврка на права просмотра страницы закрытой информации
        if self.request.user.has_perm('workers.WorkerClosed_view'):
            workerClosed = WorkerClosed.objects.get(user__slug=self.kwargs.get(self.slug_url_kwarg))
            if user.actual_subdivision == workerBasic.actual_subdivision and user.actual_department == workerBasic.actual_department:
                context['closed'] = workerClosed
                if self.request.user.has_perm('workers.WorkerClosed_change'):
                    context['closed_permission'] = True
                if (self.request.user.has_perm('workers.WorkerClosed_his_change') and workerBasic == user):
                    context['closed_permission'] = True
                if (not self.request.user.has_perm('workers.WorkerClosed_his_change') and workerBasic == user):
                    context['closed_permission'] = False

        return context


class Workers_Change_Password(LoginRequiredMixin, PasswordChangeView):
    """Изменить только сам сотрудник"""
    template_name = 'workers/workers_settings/workers_password_change.html'
    form_class = Workers_Form_PasswordChange
    login_url = 'login'
    redirect_field_name = ''

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


class Workers_Update_Password(UpdateView):
    """Изменить только по правам"""
    model = WorkerBasic
    template_name = 'workers/workers_password_update.html'
    form_class = Workers_Form_UpdatePassword
    login_url = 'login'
    redirect_field_name = ''
    permission_required = 'workers.workers_update_password_superiors'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = WorkerBasic.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пользователя'
        context['user'] = WorkerBasic.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        if 'workers_slug' in self.kwargs:
            slug = self.kwargs['workers_slug']
        return reverse('workers_update_password', kwargs={'workers_slug': slug})

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Данные сохранены успешно')
        return HttpResponseRedirect(self.get_success_url())


class Workers_Change(LoginRequiredMixin, WorkerPermissionsUpdateMixin, UpdateView):
    model = Worker
    template_name = 'workers/workers_settings/workers_change.html'

    form_class = Workers_Form_Change
    login_url = 'login'
    permission_required = 'workers.UserWorker_change'  #
    belonging_subdivision = True  # Проверка на принадлежность к управлению
    belonging_department = True  # Проверка на принадлежность к отделу
    permission_his_required = 'workers.UserWorker_his_change'  # Права на редактирования самого себя
    belonging_his = True  # Самостоятельно можно редактировать

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


class WorkerBasic_Change(LoginRequiredMixin, WorkerClosedPermissionsUpdateMixin, UpdateView):
    model = WorkerBasic
    template_name = 'workers/workers_settings/workers_change_basic_detail.html'

    form_class = WorkerBasic_Form_Change
    login_url = 'login'
    permission_required = 'workers.WorkerBasic_change'
    belonging_subdivision = True  # Проверка на принадлежность к управлению
    belonging_department = True  # Проверка на принадлежность к отделу
    permission_his_required = 'workers.WorkerBasic_his_change'  # Права на редактирования самого себя
    belonging_his = True  # Самостоятельно можно редактировать

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
    template_name = 'workers/workers_settings/workers_change_closed_detail.html'

    form_class = WorkerClosed_Form_Change
    login_url = 'login'
    permission_required = 'workers.WorkerClosed_change'
    belonging_subdivision = True  # Проверка на принадлежность к управлению
    belonging_department = True  # Проверка на принадлежность к отделу
    permission_his_required = 'workers.WorkerClosed_his_change'  # Права на редактирования самого себя
    belonging_his = True  # Самостоятельно можно редактировать

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


class Workers_Image(LoginRequiredMixin, WorkerPermissionsUpdateMixin, UpdateView):
    """Добавление аватарок на сайт"""
    model = Worker
    template_name = 'workers/workers_settings/workers_images.html'
    form_class = Workers_Form_Upload_Images

    login_url = 'login'
    permission_required = 'workers.UserWorker_change'  #
    belonging_subdivision = True  # Проверка на принадлежность к управлению
    belonging_department = True  # Проверка на принадлежность к отделу
    permission_his_required = 'workers.UserWorker_his_change'  # Права на редактирования самого себя
    belonging_his = True  # Самостоятельно можно редактировать

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


class WorkerClosed_Passport(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление паспорта на сайт"""
    model = WorkerClosed
    template_name = 'workers/workers_settings/workers_passport.html'
    form_class = WorkerClosed_Form_Upload_Passport

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


class WorkerClosed_Passport_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление паспорта """
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

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


class WorkerClosed_Snils(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление снилс на сайт"""
    model = WorkerClosed
    template_name = 'workers/workers_settings/workers_snils.html'
    form_class = WorkerClosed_Form_Upload_Snils

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


class WorkerClosed_Snils_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление снилс"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

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


class WorkerClosed_Inn(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление инн на сайт"""
    model = WorkerClosed
    template_name = 'workers/workers_settings/workers_inn.html'
    form_class = WorkerClosed_Form_Upload_Inn

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


class WorkerClosed_Inn_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление инн"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

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


class WorkerClosed_Archive(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление архива на сайт"""
    model = WorkerClosed
    template_name = 'workers/workers_settings/workers_archive.html'
    form_class = WorkerClosed_Form_Upload_Archive

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


class WorkerClosed_Archive_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление архива"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

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


class WorkerClosed_Signature(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление подписи на сайт"""
    model = WorkerClosed
    template_name = 'workers/workers_settings/workers_signature.html'
    form_class = WorkerClosed_Form_Upload_Signature

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


class WorkerClosed_Signature_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление подписи"""
    model = WorkerClosed
    template_name = 'typical/file_delete.html'

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


class User_Permissions(LoginRequiredMixin, WorkerPermissionsUpdateMixin, DetailView):
    """Добавление нового сотрудника"""
    model = Worker
    template_name = 'workers/workers_settings/workers_permissions.html'

    login_url = 'login'
    permission_required = 'workers.UserBasic_permission'  #
    belonging_subdivision = True  # Проверка на принадлежность к управлению
    belonging_department = True  # Проверка на принадлежность к отделу
    permission_his_required = 'workers.UserBasic_permission'  # Права на редактирования самого себя
    belonging_his = False  # Самостоятельно можно редактировать

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
        # ------------------------------------
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
        for worker_all_permission in worker_all_permissions:
            del user_add_permissions[worker_all_permission]
        context['user_add_permissions'] = user_add_permissions

        # worker_permissions
        user_remove_permissions = dict()
        for perm in worker_permissions:
            if user_all_permissions[perm]:
                user_remove_permissions[perm] = worker_permissions[perm]

        context['user_remove_permissions'] = user_remove_permissions

        return context
