from django.db import models
from transliterate import translit
from django.template.defaultfilters import slugify

from apps.workers.models import Worker, WorkerBasic
from apps.workobjects.models import OrganizationsObjects


class InformationMissing(models.Model):
    """Причины отсутствия на работе."""
    name = models.CharField(max_length=150, unique=False, null=False, blank=False, verbose_name='Причина отсутствия')
    color = models.CharField(max_length=7, default="#ffffff", verbose_name='Цвет')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name='slug')

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        super(InformationMissing, self).save()

    class Meta:
        verbose_name = 'Причина отсутствия на работе'
        verbose_name_plural = 'Причины отсутствия на работе'
        ordering = ['name']
        default_permissions = ('')
        permissions = (
            ('InformationMissing_add', 'Пользователь. Сотрудник. Причины отсутствия на работе. Добавить.'),
            ('InformationMissing_view', 'Пользователь. Сотрудник. Причины отсутствия на работе. Просмотреть.'),
            ('InformationMissing_delete', 'Пользователь. Сотрудник. Причины отсутствия на работе. Удалить.'),
            (
                'InformationMissing_change', 'Пользователь. Сотрудник. Причины отсутствия на работе. Редактировать.'),
        )


class InformationWeekendsHolidays(models.Model):
    """Информация о выходных днях и праздниках"""
    date = models.DateField(unique=True, verbose_name='Дата')
    description = models.CharField(max_length=255, verbose_name='Описание')
    work = models.BooleanField(default=False, verbose_name='Выходим на работу')
    work_time = models.CharField(max_length=10, blank=True, verbose_name='Время работы')

    def __str__(self):
        return '{0}:{1}'.format(str(self.date), self.description)

    class Meta:
        verbose_name = 'Информация о выходных днях и праздниках'
        verbose_name_plural = 'Информация о выходных днях и праздниках'
        ordering = ['date']
        default_permissions = ('')
        permissions = (
            ('InformationWeekendsHolidays_add',
             'Пользователь. Сотрудник. Информация о выходных днях и праздниках. Добавить.'),
            ('InformationWeekendsHolidays_view',
             'Пользователь. Сотрудник. Информация о выходных днях и праздниках. Просмотреть.'),
            ('InformationWeekendsHolidays_delete',
             'Пользователь. Сотрудник. Информация о выходных днях и праздниках. Удалить.'),
            ('InformationWeekendsHolidays_change',
             'Пользователь. Сотрудник. Информация о выходных днях и праздниках. Редактировать.'),
        )


class WorkersMissing(models.Model):
    """Отсутствие сотрудников"""
    user = models.ForeignKey(WorkerBasic, on_delete=models.PROTECT, verbose_name='Сотрудник')
    information_missing = models.ForeignKey(InformationMissing, on_delete=models.PROTECT,
                                            verbose_name='Причина отсутствия')
    date_start = models.DateField(verbose_name='Дата начала отсутствия')
    date_end = models.DateField(verbose_name='Дата окончание отсутствия')
    comments = models.CharField(max_length=255, blank=True, verbose_name='Комментарии')

    def __str__(self):
        return '{0}:{1}:{2} - {3}'.format(self.user, self.information_missing, str(self.date_start), str(self.date_end))

    class Meta:
        verbose_name = 'Отсутствие сотрудника'
        verbose_name_plural = 'Отсутствие сотрудников'
        ordering = ['pk']
        default_permissions = ('')
        permissions = (
            #
            ('WorkersMissing_his_add', 'Пользователь. Сотрудник. Отсутствие сотрудников. Добавить. Самостоятельно.'),
            ('WorkersMissing_his_view', 'Пользователь. Сотрудник. Отсутствие сотрудников. Просмотреть. Самостоятельно'),
            ('WorkersMissing_his_delete', 'Пользователь. Сотрудник. Отсутствие сотрудников. Удалить. Самостоятельно'),
            ('WorkersMissing_his_change', 'Пользователь. Сотрудник. Отсутствие сотрудников. Редактировать. Самостоятельно'),

            ('WorkersMissing_add', 'Пользователь. Сотрудник. Отсутствие сотрудников. Добавить. Проверка управления и отдела.'),
            ('WorkersMissing_add_subdivision','Пользователь. Сотрудник. Отсутствие сотрудников. Добавить. Проверка управления.'),
            ('WorkersMissing_add_all','Пользователь. Сотрудник. Отсутствие сотрудников. Добавить. Для руководства.'),

            ('WorkersMissing_view',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Просмотреть. Проверка управления и отдела.'),
            ('WorkersMissing_view_subdivision',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Просмотреть. Проверка управления.'),
            ('WorkersMissing_view_all', 'Пользователь. Сотрудник. Отсутствие сотрудников. Просмотреть. Для руководства.'),

            ('WorkersMissing_delete',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Удалить. Проверка управления и отдела.'),
            ('WorkersMissing_delete_subdivision',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Удалить. Проверка управления.'),
            ('WorkersMissing_delete_all',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Удалить. Для руководства.'),

            ('WorkersMissing_change',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Редактировать. Проверка управления и отдела.'),
            ('WorkersMissing_change_subdivision',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Редактировать. Проверка управления.'),
            ('WorkersMissing_change_all',
             'Пользователь. Сотрудник. Отсутствие сотрудников. Редактировать. Для руководства.'),

            ('WorkersPlanning_view_all',
             'Пользователь. Сотрудник. Планирование работ. Для руководства.'),
            ('WorkersPlanning_view_subdivision',
             'Пользователь. Сотрудник. Планирование работ. Для управления.'),
            ('WorkersPlanning_view_department',
             'Пользователь. Сотрудник. Планирование работ. Для отдела.'),

        )


class WorkersMission(models.Model):
    """Командировка сотрудников"""
    MISSING_STATUS = (
        ('FINAL', 'Итоговая'),
        ('PLANNING', 'Планируемая'),
    )
    user = models.ForeignKey(WorkerBasic, on_delete=models.PROTECT, verbose_name='Сотрудник')
    organizations_objects = models.ForeignKey(OrganizationsObjects, on_delete=models.PROTECT,
                                              verbose_name='Объект командировки')
    date_departure = models.DateField(verbose_name='Дата выезда')
    date_start = models.DateField(blank=True, null=True, verbose_name='Дата начала работы')
    date_end = models.DateField(blank=True, null=True, verbose_name='Дата окончание работы')
    date_arrival = models.DateField(verbose_name='Дата прибытия')
    status = models.CharField(verbose_name='Статус', choices=MISSING_STATUS, max_length=30, default='FINAL')

    def __str__(self):
        return '{0}:{1}:{2} - {3}'.format(self.user, self.organizations_objects, str(self.date_departure),
                                          str(self.date_arrival))

    class Meta:
        verbose_name = 'Командировка сотрудника'
        verbose_name_plural = 'Командировка сотрудников'
        ordering = ['pk']
        default_permissions = ('')
        permissions = (
            ('WorkersMissing_his_add','Пользователь. Сотрудник. Командировка сотрудников. Добавить. Самостоятельно редактировать.'),
            ('WorkersMissing_his_view','Пользователь. Сотрудник. Командировка сотрудников. Просмотреть. Самостоятельно редактировать'),
            ('WorkersMissing_his_delete','Пользователь. Сотрудник. Командировка сотрудников. Удалить. Самостоятельно редактировать'),
            ('WorkersMissing_his_change','Пользователь. Сотрудник. Командировка сотрудников. Редактировать. Самостоятельно редактировать'),

            ('WorkersMission_add','Пользователь. Сотрудник. Командировка сотрудников. Добавить. Проверка управления и отдела.'),
            ('WorkersMission_add_subdivision','Пользователь. Сотрудник. Командировка сотрудников. Добавить. Проверка управления.'),
            ('WorkersMission_add_all', 'Пользователь. Сотрудник. Командировка сотрудников. Добавить. Для руководства.'),

            ('WorkersMission_view','Пользователь. Сотрудник. Командировка сотрудников. Просмотреть. Проверка управления и отдела.'),
            ('WorkersMission_view_subdivision','Пользователь. Сотрудник. Командировка сотрудников. Просмотреть. Проверка управления.'),
            ('WorkersMission_view_all', 'Пользователь. Сотрудник. Командировка сотрудников. Просмотреть. Для руководства.'),

            ('WorkersMission_delete','Пользователь. Сотрудник. Командировка сотрудников. Удалить. Проверка управления и отдела.'),
            ('WorkersMission_delete_subdivision','Пользователь. Сотрудник. Командировка сотрудников. Удалить. Проверка управления.'),
            ('WorkersMission_delete_all','Пользователь. Сотрудник. Командировка сотрудников. Удалить. Для руководства.'),

            ('WorkersMission_change','Пользователь. Сотрудник. Командировка сотрудников. Редактировать. Проверка управления и отдела.'),
            ('WorkersMission_change_subdivision','Пользователь. Сотрудник. Командировка сотрудников. Редактировать. Проверка управления.'),
            ('WorkersMission_change_all','Пользователь. Сотрудник. Командировка сотрудников. Редактировать. Для руководства.'),


        )


class WorkersWeekendWork(models.Model):
    """Работа в выходные в офисе."""
    user = models.ForeignKey(WorkerBasic, on_delete=models.PROTECT, null=True, verbose_name='Сотрудник')
    date = models.DateField(verbose_name='Дата выхода')
    planning = models.TextField(verbose_name='Планирование работ', blank=True)
    hours_working = models.FloatField(blank=True, default=-1.0, verbose_name='Отработанное время')

    def __str__(self):
        return '{0}:{1}'.format(str(self.date), self.user)

    class Meta:
        verbose_name = 'Работа в выходные в офисе.'
        verbose_name_plural = 'Работа в выходные в офисе.'
        ordering = ['pk']
        default_permissions = ('')
        permissions = (
            ('WorkersWeekendWork_his_add',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Добавить. Самостоятельно редактировать.'),
            ('WorkersWeekendWork_his_view',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Просмотреть. Самостоятельно редактировать'),
            ('WorkersWeekendWork_his_delete',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Удалить. Самостоятельно редактировать'),
            ('WorkersWeekendWork_his_change',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Редактировать. Самостоятельно редактировать'),

            ('WorkersWeekendWork_add',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Добавить. Проверка управления и отдела.'),
            ('WorkersWeekendWork_add_subdivision',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Добавить. Проверка управления.'),
            ('WorkersWeekendWork_add_all', 'Пользователь. Сотрудник. Работа в выходные в офисе. Добавить. Для руководства.'),

            ('WorkersWeekendWork_view','Пользователь. Сотрудник. Работа в выходные в офисе. Просмотреть. Проверка управления и отдела.'),
            ('WorkersWeekendWork_view_subdivision','Пользователь. Сотрудник. Работа в выходные в офисе. Просмотреть. Проверка управления.'),
            ('WorkersWeekendWork_view_all','Пользователь. Сотрудник. Работа в выходные в офисе. Просмотреть. Для руководства.'),

            ('WorkersWeekendWork_delete',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Удалить. Проверка управления и отдела.'),
            ('WorkersWeekendWork_delete_subdivision',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Удалить. Проверка управления.'),
            ('WorkersWeekendWork_delete_all',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Удалить. Для руководства.'),

            ('WorkersWeekendWork_change',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Редактировать. Проверка управления и отдела.'),
            ('WorkersWeekendWork_change_subdivision',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Редактировать. Проверка управления.'),
            ('WorkersWeekendWork_change_all',
             'Пользователь. Сотрудник. Работа в выходные в офисе. Редактировать. Для руководства.'),


        )
