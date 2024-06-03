from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView

from apps.workobjects.forms import OrganizationsObjects_Form_Control, OrganizationsObjects_Form_Filter
from apps.workobjects.models import OrganizationsObjects


class OrganizationsObjects_View(ListView):
    """Вывод всех объектов"""
    model = OrganizationsObjects
    template_name = 'objects/objects.html'
    paginate_by = 40
    context_object_name = 'objects'

    def get_queryset(self):
        filters = Q()
        if self.request.GET:
            form = OrganizationsObjects_Form_Filter(self.request.GET)
            if form.is_valid():
                if 'organization' in self.request.GET:
                    organization = str(self.request.GET['organization']).replace("+", "")
                    if organization != '':
                        filters &= Q(**{f'{"organization"}': organization})
        return super().get_queryset().filter(filters).select_related('organization', )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Объекты'
        context['form_filter'] = OrganizationsObjects_Form_Filter(self.request.GET)
        if self.request.GET:
            organization = ''
            try:
                organization = self.request.GET['organization']
            except Exception as e:
                pass
            context['url_filter'] = '?organization={0}'.format(organization)

        return context


class OrganizationsObjects_Update(UpdateView):
    """Управление/Подразделение"""
    model = OrganizationsObjects
    template_name = 'objects/objects_control.html'
    form_class = OrganizationsObjects_Form_Control
    success_url = reverse_lazy('objects')

    # Управление по slug
    def get_object(self, queryset=None):
        instance = OrganizationsObjects.objects.get(slug=self.kwargs.get('objects_slug', ''))
        return instance

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать объект'
        context['title_page'] = 'Редактировать'
        return context


class OrganizationsObjects_Add(CreateView):
    """Управление/Подразделение"""
    model = OrganizationsObjects
    template_name = 'objects/objects_control.html'
    form_class = OrganizationsObjects_Form_Control
    success_url = reverse_lazy('objects')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить объект'
        context['title_page'] = 'Редактировать'
        return context
