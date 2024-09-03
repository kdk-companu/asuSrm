from django.db.models import Q
from django.template.defaultfilters import addslashes
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, TemplateView

from apps.workers.forms import WorkersMission_Form_Add, WorkersMission_Form_Filter
from apps.workers.models import WorkersMission, WorkerBasic
import datetime


class WorkersMission_Add(CreateView):
    model = WorkersMission
    template_name = 'user/worker/planning/workersmission_control.html'
    form_class = WorkersMission_Form_Add
    success_url = reverse_lazy('workersMission')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить командировку'
        context['title_page'] = 'Добавить'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMission_Add, self).get_form_kwargs()
        kwargs['initial']['user_current'] = self.request.user
        try:
            kwargs['initial']['workerBasic_current'] = WorkerBasic.objects.get(user=self.request.user)
        except:
            kwargs['initial']['workerBasic_current'] = None
        return kwargs


class WorkersMission_Update(UpdateView):
    model = WorkersMission
    template_name = 'user/worker/planning/workersmission_control.html'
    form_class = WorkersMission_Form_Add
    success_url = reverse_lazy('workersMission')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать кокомандировку'
        context['title_page'] = 'Редактировать'
        return context

    def get_form_kwargs(self):
        kwargs = super(WorkersMission_Add, self).get_form_kwargs()
        kwargs['initial']['user_current'] = self.request.user
        try:
            kwargs['initial']['workerBasic_current'] = WorkerBasic.objects.get(user=self.request.user)
        except:
            kwargs['initial']['workerBasic_current'] = None
        return kwargs


class WorkersMission_View(ListView):
    paginate_by = 40
    model = WorkersMission
    template_name = 'user/worker/planning/workersmission.html'
    context_object_name = 'workersmissions'
    workerBasic = None

    def get_queryset(self):
        date_start = datetime.date(datetime.datetime.now().year, 1, 1)
        date_end = datetime.date(datetime.datetime.now().year + 1, 1, 1)
        filters = Q()  # создаем первый объект Q, что бы складывать с ним другие
        """Обработка GET Запросов"""
        if self.request.GET:
            """Проверка формы для запроса"""
            form = WorkersMission_Form_Filter(self.request.GET, initial={'user': self.workerBasic})
            if form.is_valid():
                if not self.request.GET.get('date_in') == '' and self.request.GET.get('date_in'):
                    get_date_in = self.request.GET.get('date_in').split('.')
                    date_start = datetime.date(int(get_date_in[2]), int(get_date_in[1]), int(get_date_in[0]))
                if not self.request.GET.get('date_out') == '' and self.request.GET.get('date_out'):
                    get_date_out = self.request.GET.get('date_out').split('.')
                    date_end = datetime.date(int(get_date_out[2]), int(get_date_out[1]), int(get_date_out[0]))
                get_objects = 'own'
                if self.request.GET.get('objects'):
                    get_objects = addslashes(self.request.GET.get('objects'))
                if not get_objects == 'own':
                    filters &= Q(**{f'{"organizations_objects__slug"}': get_objects})
                get_workers = 'own'
                if self.request.GET.get('workers'):
                    get_workers = addslashes(self.request.GET.get('workers'))
                if not get_workers == 'own':
                    filters &= Q(**{f'{"user__user__slug"}': get_workers})

        """Фильтр в базу данных"""
        filters &= Q(**{f'{"date_departure__gte"}': date_start})
        filters &= Q(**{f'{"date_arrival__lte"}': date_end})

        if not self.request.user.has_perm('workers.WorkersMission_view_all') or not self.workerBasic:
            if self.request.user.has_perm('workers.WorkersMission_view_subdivision') and self.workerBasic:
                filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})
            if self.request.user.has_perm(
                    'workers.WorkersMission_view') and self.workerBasic and not self.request.user.has_perm(
                'workers.WorkersMission_view_subdivision'):
                filters &= Q(**{f'{"user__actual_subdivision"}': self.workerBasic.actual_subdivision})
                filters &= Q(**{f'{"user__actual_department"}': self.workerBasic.actual_department})

        return WorkersMission.objects.filter(filters).order_by('-date_departure')

    def get(self, request, *args, **kwargs):
        try:
            self.workerBasic = WorkerBasic.objects.get(user=self.request.user)
        except:
            pass
        if self.request.user.has_perm('workers.WorkersMission_delete') and self.request.GET.get('remove'):
            # Проверка разрешения удаления
            try:
                remove = WorkersMission.objects.get(pk=self.request.GET.get('remove'))
                if remove.user.actual_subdivision == self.workerBasic.actual_subdivision and remove.user.actual_department == self.workerBasic.actual_department:
                    remove.delete()
            except Exception:
                pass
        return super(WorkersMission_View, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Командировки.'
        context['form_filter'] = WorkersMission_Form_Filter(self.request.GET, initial={'user': self.workerBasic})
        context['url_filter'] = ""
        if self.request.GET:
            dateIn = ''
            dateOut = ''
            objects = 'own'
            workers = 'own'
            try:
                dateIn = self.request.GET['date_in']
            except Exception as e:
                pass
            try:
                dateOut = self.request.GET['date_out']
            except Exception as e:
                pass
            try:
                objects = self.request.GET['objects']
            except Exception as e:
                pass
            try:
                workers = self.request.GET['workers']
            except Exception as e:
                pass
            context['url_filter'] = "?&objects={2}&workers={3}&date_in={0}&date_out={1}".format((dateIn), dateOut,
                                                                                                objects, workers)
        return context
