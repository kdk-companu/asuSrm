import os
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from apps.workers.forms import Search_Filter, Search_User_Filter, Workers_Add_Form, Workers_Form_Upload_Images, \
    Workers_Form_PasswordChange, Workers_Form_Change, Workers_Form_Basic_Change, Workers_Form_Closed_Change, \
    Workers_Form_Upload_Passport, Workers_Form_Upload_Snils, Workers_Form_Upload_Inn, Workers_Form_Upload_Archive, \
    Workers_Form_Upload_Signature, Workers_Form_UpdatePassword, Group_Form_Permissions
from apps.workers.models import User, User_Basic, User_Closed
from django.contrib import messages

from mixin.user_right import ViewsPermissionsMixin


class Workers(LoginRequiredMixin, ViewsPermissionsMixin, ListView):
    """Вывод всех пользователей"""
    model = User_Basic
    template_name = 'workers/workers.html'
    paginate_by = 40
    context_object_name = 'workers'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.user_view'

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
        filters &= Q(**{f'{"user__employee"}': "employee_current"})

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


class Workers_Filter(LoginRequiredMixin, ViewsPermissionsMixin, ListView):
    """Вывод всех пользователей"""
    model = User_Basic
    template_name = 'workers/workers_filter.html'
    paginate_by = 40
    context_object_name = 'workers'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.user_view'

    def get_queryset(self):
        filters = Q()
        if self.request.GET:
            form = Search_User_Filter(self.request.GET)
            if form.is_valid():
                if 'organization_subdivision' in self.request.GET:
                    organization_subdivision = str(self.request.GET['organization_subdivision']).replace("+", "")
                    if organization_subdivision != '':
                        filters |= Q(**{f'{"organization_subdivision"}': organization_subdivision})
                if 'organization_department' in self.request.GET:
                    organization_department = str(self.request.GET['organization_department']).replace("+", "")
                    if organization_department != '':
                        filters |= Q(**{f'{"organization_department"}': organization_department})
                if 'chief' in self.request.GET:
                    chief = str(self.request.GET['chief']).replace("+", "")
                    if chief != '':
                        filters |= Q(**{f'{"chief"}': chief})

        filters &= Q(**{f'{"user__employee"}': "employee_current"})

        return super().get_queryset().filter(filters).select_related(
            'user',
            'organization_subdivision',
            'organization_department',
            'actual_subdivision',
            'actual_department',
            'chief',
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пользователи'
        context['search_user_filter'] = Search_User_Filter(self.request.GET)
        if self.request.GET:
            organization_subdivision = ''
            organization_department = ''
            chief = ''
            try:
                organization_subdivision = self.request.GET['organization_subdivision']
                organization_department = self.request.GET['organization_department']
                chief = self.request.GET['chief']
            except Exception as e:
                pass
            context['url_filter'] = '?organization_subdivision={0}&organization_department={1}&chief={0}'.format(
                organization_subdivision, organization_department, chief)

        return context


class Workers_Add(LoginRequiredMixin, ViewsPermissionsMixin, CreateView):
    """Добавление нового сотрудника"""
    model = User
    template_name = 'workers/workers_settings/workers_add.html'
    form_class = Workers_Add_Form
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.user_add'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление пользователя'
        return context

    def form_valid(self, form):
        form.save().organization = self.request.user.organization
        base = form.save(commit=False)
        base.save()
        return super().form_valid(form)

    def get_success_url(self):
        super()
        # Получение последнего пользователя
        upadate_user = User.objects.latest('id')
        # Исключаем ошибки при создании пользователя
        try:
            # upadate_user = User.objects.latest('id')
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
        # print(self.user)
        user_subdivision_department = User_Basic.objects.get(user=self.request.user)
        new_user_subdivision_department = User_Basic.objects.get(user=upadate_user)
        new_user_subdivision_department.organization_subdivision = user_subdivision_department.organization_subdivision
        new_user_subdivision_department.organization_department = user_subdivision_department.organization_department
        new_user_subdivision_department.save()

        return reverse('workers_detail', kwargs={'workers_slug': upadate_user.slug})


class Workers_DetailView(LoginRequiredMixin, ViewsPermissionsMixin, DetailView):
    """Добавление нового сотрудника"""
    model = User
    template_name = 'workers/workers_views.html'
    slug_url_kwarg = 'workers_slug'
    context_object_name = 'worker'
    # Права пользователя
    login_url = 'login'
    permission_required = 'workers.user_view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Страница пользователя'

        if self.request.user.has_perm('workers.user_basic_view'):
            context['basic'] = User_Basic.objects.get(user__slug=self.kwargs.get(self.slug_url_kwarg))

        if self.request.user.has_perm('workers.user_closed_view'):
            context['closed'] = User_Closed.objects.get(user__slug=self.kwargs.get(self.slug_url_kwarg))

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
    model = User
    template_name = 'workers/workers_password_update.html'
    form_class = Workers_Form_UpdatePassword
    login_url = 'login'
    redirect_field_name = ''
    permission_required = 'workers.workers_update_password_superiors'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пользователя'
        context['user'] = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        if 'workers_slug' in self.kwargs:
            slug = self.kwargs['workers_slug']
        return reverse('workers_update_password', kwargs={'workers_slug': slug})

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Данные сохранены успешно')
        return HttpResponseRedirect(self.get_success_url())


class User_Change(LoginRequiredMixin, ViewsPermissionsMixin, UpdateView):
    model = User
    template_name = 'workers/workers_settings/workers_change.html'

    form_class = Workers_Form_Change
    login_url = 'login'
    permission_required = 'workers.user_change'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пользователя'
        context['user'] = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_change', kwargs={'workers_slug': self.kwargs['workers_slug']})


class User_Basic_Change(LoginRequiredMixin, ViewsPermissionsMixin, UpdateView):
    model = User_Basic
    template_name = 'workers/workers_settings/workers_change_basic_detail.html'

    form_class = Workers_Form_Basic_Change
    login_url = 'login'
    permission_required = 'workers.user_basic_change'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Basic.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование. Базовая информация.'
        context['user'] = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_basic_change', kwargs={'workers_slug': self.kwargs['workers_slug']})


class User_Closed_Change(LoginRequiredMixin, ViewsPermissionsMixin, UpdateView):
    model = User_Closed
    template_name = 'workers/workers_settings/workers_change_closed_detail.html'

    form_class = Workers_Form_Closed_Change
    login_url = 'login'
    permission_required = 'workers.user_closed_change'

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование. Закрытая информация.'
        context['user'] = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_closed_change', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Image(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление аватарок на сайт"""
    model = User
    template_name = 'workers/workers_settings/workers_images.html'
    form_class = Workers_Form_Upload_Images

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
        instance = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка аватарки.'
        context['workers'] = User.objects.get(slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_image', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Passport(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление паспорта на сайт"""
    model = User_Closed
    template_name = 'workers/workers_settings/workers_passport.html'
    form_class = Workers_Form_Upload_Passport

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.passport_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка паспорта.'
        context['workers'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_passport', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Passport_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление паспорта """
    model = User_Closed
    template_name = 'typical/file_delete.html'

    def post(self, request, *args, **kwargs):
        # Удаляем паспорт
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.passport_scan.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    def form_valid(self, form):
        # Удаление старых файлов
        file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.passport_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление паспорта.'
        context['info'] = 'паспорт.'
        context['file'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class Workers_Snils(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление снилс на сайт"""
    model = User_Closed
    template_name = 'workers/workers_settings/workers_snils.html'
    form_class = Workers_Form_Upload_Snils

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.snils_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка снилс.'
        context['workers'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_snils', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Snils_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление снилс"""
    model = User_Closed
    template_name = 'typical/file_delete.html'

    def post(self, request, *args, **kwargs):
        # Удаляем паспорт
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.snils_scan.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление снилс.'
        context['info'] = 'снилс.'
        context['file'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class Workers_Inn(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление инн на сайт"""
    model = User_Closed
    template_name = 'workers/workers_settings/workers_inn.html'
    form_class = Workers_Form_Upload_Inn

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.inn_scan.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка инн.'
        context['workers'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_inn', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Inn_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление инн"""
    model = User_Closed
    template_name = 'typical/file_delete.html'

    def post(self, request, *args, **kwargs):
        # Удаляем инн
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.inn_scan.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление инн.'
        context['info'] = 'инн.'
        context['file'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class Workers_Archive(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление архива на сайт"""
    model = User_Closed
    template_name = 'workers/workers_settings/workers_archive.html'
    form_class = Workers_Form_Upload_Archive

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def form_valid(self, form):
        # Удаление старых файлов
        file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        file.archive_documents_employment.delete(save=True)
        # Сохранение формы
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка архива.'
        context['workers'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_archive', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Archive_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление архива"""
    model = User_Closed
    template_name = 'typical/file_delete.html'

    def post(self, request, *args, **kwargs):
        # Удаляем архив
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.archive_documents_employment.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление архива.'
        context['info'] = 'архив.'
        context['file'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class Workers_Signature(UpdateView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Добавление подписи на сайт"""
    model = User_Closed
    template_name = 'workers/workers_settings/workers_signature.html'
    form_class = Workers_Form_Upload_Signature

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Загрузка подписи.'
        context['workers'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse('workers_signature', kwargs={'workers_slug': self.kwargs['workers_slug']})


class Workers_Signature_Delete(DetailView):  # LoginRequiredMixin, ViewsPermissionsMixin,
    """Удаление подписи"""
    model = User_Closed
    template_name = 'typical/file_delete.html'

    def post(self, request, *args, **kwargs):
        # Удаляем архив
        if request.POST:
            if request.POST.get("delete"):
                if request.POST.get("delete") == "yes":
                    file = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
                    file.signature_example.delete(save=True)
        return redirect('workers_detail', *args, **kwargs)

    # Управление по slug
    def get_object(self, queryset=None):
        instance = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug', ''))
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление подписи.'
        context['info'] = 'подпись.'
        context['file'] = User_Closed.objects.get(user__slug=self.kwargs.get('workers_slug'))
        return context


class Group_Permissions(UpdateView):
    """Управление группами"""
    model = Group
    form_class = Group_Form_Permissions
    template_name = 'workers/workers_settings/group_permissions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Настройка прав группы'
        context['group'] = Group.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        messages.success(self.request, "Данные сохранены успешно")
        return reverse("chief_permissions", kwargs={"pk": self.kwargs['pk']})


class User_Permissions(DetailView):
    """Добавление нового сотрудника"""
    model = User
    template_name = 'workers/workers_settings/workers_permissions.html'

    def get_object(self, queryset=None):
        instance = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
        return instance

    def post(self, request, *args, **kwargs):
        print('-------------1111')

        lll = request.POST.get("permission_add")
        if request.POST.get("permission_add"):
            permission = Permission.objects.get(codename=request.POST.get("permission_add"))
            user = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
            user.user_permissions.add(permission)
        elif request.POST.get("permission_remove"):
            permission = Permission.objects.get(codename=request.POST.get("permission_remove"))
            user = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
            user.user_permissions.remove(permission)

        return redirect('workers_permissions', *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование прав пользователя.'
        worker = User.objects.get(slug=self.kwargs.get('workers_slug', ''))  # Текущие права пользователя
        context['worker'] = worker  # Текущие права пользователя
        worker_permissions = dict()
        for perm in worker.user_permissions.all():
            worker_permissions[perm.codename] = perm.name
        context['worker_permissions'] = worker_permissions  # Текущие права пользователя

        worker_group_permissions = dict()
        for perm in worker.groups.first().permissions.all():
            worker_group_permissions[perm.codename] = perm.name
        context['worker_group_permissions'] = worker_group_permissions  # Текущие групповые права пользователя

        worker_all_permissions = {**worker_permissions, **worker_group_permissions}
        # ------------------------------------
        user_permissions = dict()
        for perm in self.request.user.user_permissions.all():
            user_permissions[perm.codename] = perm.name
        context['user_permissions'] = user_permissions  # Текущие права пользователя

        user_group_permissions = dict()
        for perm in self.request.user.groups.first().permissions.all():
            user_group_permissions[perm.codename] = perm.name
        context['user_group_permissions'] = user_group_permissions  # Текущие групповые права пользователя

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
