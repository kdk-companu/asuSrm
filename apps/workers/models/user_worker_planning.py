from django.db import models
from transliterate import translit
from django.template.defaultfilters import slugify

from apps.workers.models import WorkerBasic
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
            ('InformationMissing_change', 'Пользователь. Сотрудник. Причины отсутствия на работе. Редактировать.'),
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
            # Добавить
            ('WorkersMissing_department_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Добавить.'),
            ('WorkersMissing_subdivision_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Добавить.'),
            ('WorkersMissing_management_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Добавить.'),
            ('WorkersMissing_his_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Добавить.'),
            # Редактирование
            ('WorkersMissing_department_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Редактировать.'),
            ('WorkersMissing_subdivision_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Редактировать.'),
            ('WorkersMissing_management_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Редактировать.'),
            ('WorkersMissing_his_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Редактировать.'),
            # Удалить
            ('WorkersMissing_department_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Удалить.'),
            ('WorkersMissing_subdivision_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Удалить.'),
            ('WorkersMissing_management_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Удалить.'),
            ('WorkersMissing_his_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Удалить.'),
            # Просмотреть
            ('WorkersMissing_department_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Просмотреть.'),
            ('WorkersMissing_subdivision_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Просмотреть.'),
            ('WorkersMissing_management_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Просмотреть.'),
            ('WorkersMissing_his_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Просмотреть.'),
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
            # Добавить
            ('WorkersMission_department_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Добавить.'),
            ('WorkersMission_subdivision_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Добавить.'),
            ('WorkersMission_management_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Добавить.'),
            ('WorkersMission_his_add',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Добавить.'),
            # Редактирование
            ('WorkersMission_department_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Редактировать.'),
            ('WorkersMission_subdivision_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Редактировать.'),
            ('WorkersMission_management_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Редактировать.'),
            ('WorkersMission_his_change',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Редактировать.'),
            # Удалить
            ('WorkersMission_department_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Удалить.'),
            ('WorkersMission_subdivision_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Удалить.'),
            ('WorkersMission_management_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Удалить.'),
            ('WorkersMission_his_delete',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Удалить.'),
            # Просмотреть
            ('WorkersMission_department_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка отдела. Просмотреть.'),
            ('WorkersMission_subdivision_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Проверка управления. Просмотреть.'),
            ('WorkersMission_management_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Для руководства. Просмотреть.'),
            ('WorkersMission_his_view',
             'Пользователи. Сотрудник. Отсутствие сотрудников. Самостоятельно. Просмотреть.'),
            # Просмотреть Планирование работ
            ('WorkersPlannig_department_view',
             'Пользователи. Сотрудник. Планирование работ. Проверка отдела. Просмотреть.'),
            ('WorkersPlannig_subdivision_view',
             'Пользователи. Сотрудник. Планирование работ. Проверка управления. Просмотреть.'),
            ('WorkersPlannig_management_view',
             'Пользователи. Сотрудник. Планирование работ. Для руководства. Просмотреть.'),
            ('WorkersPlannig_his_view',
             'Пользователи. Сотрудник. Планирование работ. Самостоятельно. Просмотреть.'),

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
            # Добавить
            ('WorkersWeekendWork_department_add',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка отдела. Добавить.'),
            ('WorkersWeekendWork_subdivision_add',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка управления. Добавить.'),
            ('WorkersWeekendWork_management_add',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Для руководства. Добавить.'),
            ('WorkersWeekendWork_his_add',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Самостоятельно. Добавить.'),
            # Редактирование
            ('WorkersWeekendWork_department_change',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка отдела. Редактировать.'),
            ('WorkersWeekendWork_subdivision_change',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка управления. Редактировать.'),
            ('WorkersWeekendWork_management_change',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Для руководства. Редактировать.'),
            ('WorkersWeekendWork_his_change',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Самостоятельно. Редактировать.'),
            # Удалить
            ('WorkersWeekendWork_department_delete',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка отдела. Удалить.'),
            ('WorkersWeekendWork_subdivision_delete',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка управления. Удалить.'),
            ('WorkersWeekendWork_management_delete',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Для руководства. Удалить.'),
            ('WorkersWeekendWork_his_delete',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Самостоятельно. Удалить.'),
            # Просмотреть
            ('WorkersWeekendWork_department_view',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка отдела. Просмотреть.'),
            ('WorkersWeekendWork_subdivision_view',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Проверка управления. Просмотреть.'),
            ('WorkersWeekendWork_management_view',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Для руководства. Просмотреть.'),
            ('WorkersWeekendWork_his_view',
             'Пользователи. Сотрудник. Работа в выходные в офисе. Самостоятельно. Просмотреть.'),
        )