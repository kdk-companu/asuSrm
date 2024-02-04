import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from apps.workers.forms import Search_Filter, Search_User_Filter, Workers_Add_Form
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
    template_name = 'workers/workers_add.html'
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
            upadate_user = User.objects.latest('id')
            # Создание папок для нового пользователя
            folder_user = "media/user/" + str(upadate_user.pk)
            folder_user_images = "media/user/" + str(upadate_user.pk) + "/images/"
            folder_save_files = "media/user/" + str(upadate_user.pk) + "/files/"
            os.mkdir(folder_user)
            os.mkdir(folder_user_images)
            os.mkdir(folder_save_files)
        except Exception:
            pass
        message = "Пользователь {0} добавлен в базу.".format(upadate_user)
        messages.success(self.request, message)

        return reverse('workers_add')


class Workers_DetailView(LoginRequiredMixin, ViewsPermissionsMixin, DetailView):
    """Добавление нового сотрудника"""
    model = User
    template_name = 'workers/workers_views.html'
    slug_url_kwarg = 'workers_slug'
    context_object_name = 'workers'
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

# class Workers_Change_Password(LoginRequiredMixin, PasswordChangeView):
#     '''Изменить только сам сотрудник'''
#     template_name = 'workers/workers_password_change.html'
#     form_class = Workers_Form_PasswordChange
#     login_url = 'login'
#     redirect_field_name = ''
#
#     def get(self, request, *args, **kwargs):
#         context = self.get_context_data(**kwargs)
#         return self.render_to_response(context)
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project_menus = self.get_user_context(title='Изменения пароля')
#         context = dict(list(context.items()) + list(project_menus.items()))
#         return context
#
#     def form_valid(self, form):
#         self.object = form.save()
#
#         return HttpResponseRedirect('')
#
#
# class Workers_Update_Password(LoginRequiredMixin, ViewsPermissionsMixin,  UpdateView):
#     '''Изменить только по правам'''
#     model = User
#     template_name = 'workers/workers_password_update.html'
#     form_class = Workers_Form_UpdatePassword
#     login_url = 'login'
#     redirect_field_name = ''
#     permission_required = 'workers.workers_update_password_superiors'
#
#     # Управление по slug
#     def get_object(self, queryset=None):
#         instance = User.objects.get(slug=self.kwargs.get('workers_slug', ''))
#         return instance
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project_menus = self.get_user_context(title='Сброс пароля')
#         context = dict(list(context.items()) + list(project_menus.items()))
#         context['workers'] = User.objects.get(slug=self.kwargs.get('workers_slug'))
#         return context
#
#     def get_success_url(self):
#         if 'workers_slug' in self.kwargs:
#             slug = self.kwargs['workers_slug']
#         return reverse('workers_update_password', kwargs={'workers_slug': slug})
#
#     def form_valid(self, form):
#         self.object = form.save()
#         messages.success(self.request, 'Данные сохранены успешно')
#         return HttpResponseRedirect(self.get_success_url())
