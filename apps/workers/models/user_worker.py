import os

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from transliterate.utils import _

from apps.workers.models import UserBasic, Subdivision, Department, Chief
from library.files import Files
from library.image import ImagesEdit


class WorkerManager(models.Manager):
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_('Не указан телефонный номер.'))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=UserBasic.Types.WORKER)


class Worker(UserBasic):
    class Meta:
        proxy = True

    objects = WorkerManager()

    def save(self, *args, **kwargs):
        self.type = UserBasic.Types.WORKER
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь. Сотрудник.'
        verbose_name_plural = 'Пользователи. Сотрудники.'
        ordering = ['pk']
        default_permissions = ('')

        permissions = (
            # Права общие
            ('Worker_add', 'Пользователи. Сотрудник. Добавить.'),
            ('Worker_view', 'Пользователи. Сотрудник. Просмотреть.'),
            # Самостоятельное редактирование
            ('Worker_his_change', 'Пользователи. Сотрудник. Самостоятельно. Редактировать. '),
            # Редактирование данных
            ('Worker_department_change', 'Пользователи. Сотрудник. Проверка отдела. Редактировать. '),
            ('Worker_subdivision_change', 'Пользователи. Сотрудник. Проверка управления. Редактировать. '),
            ('Worker_management_change', 'Пользователи. Сотрудник. Для руководства. Редактировать. '),
            # Редактирование пароля
            ('Worker_department_change_password', 'Пользователи. Сотрудник. Проверка отдела. Обновить пароль. '),
            ('Worker_subdivision_change_password', 'Пользователи. Сотрудник. Проверка управления. Обновить пароль.'),
            ('Worker_management_change_password', 'Пользователи. Сотрудник. Для руководства. Обновить пароль.'),
            # Редактирование прав доступа
            ('Worker_department_change_permission',
             'Пользователи. Сотрудник. Проверка отдела. Права доступа.'),
            ('Worker_subdivision_change_permission',
             'Пользователи. Сотрудник. Проверка управления. Права доступа.'),
            ('Worker_management_change_permission', 'Пользователи. Сотрудник. Для руководства. Права доступа.'),
        )


class WorkerBasic(models.Model):
    """Базовая информация о сотрудниках"""
    GENDER_CHOICES = (
        ('Male', 'Мужской'),
        ('Female', 'Женский'),
    )

    class WORKERS_STATUS(models.TextChoices):
        employee_current = "employee_current", "Сотрудник действующий"  #
        employee_fired = "employee_fired", "Сотрудник уволенный"  #

    user = models.OneToOneField(Worker, on_delete=models.PROTECT, verbose_name='ФИО')

    employee = models.CharField(verbose_name='Статус сотрудника', choices=WORKERS_STATUS.choices, max_length=30,
                                default=WORKERS_STATUS.employee_current)

    organization_subdivision = models.ForeignKey(Subdivision, on_delete=models.PROTECT, blank=True,
                                                 null=True, related_name='organization_subdivision',
                                                 verbose_name='Управление в организации')
    organization_department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True,
                                                null=True, related_name='organization_department',
                                                verbose_name='Отдел в организации')
    actual_subdivision = models.ForeignKey(Subdivision, on_delete=models.PROTECT, blank=True,
                                           null=True, related_name='actual_subdivision',
                                           verbose_name='Фактическое Управление')
    actual_department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True,
                                          null=True, related_name='actual_department',
                                          verbose_name='Фактический отдел')
    chief = models.ForeignKey(Chief, on_delete=models.PROTECT, blank=True,
                              null=True, verbose_name='Должность')
    date_employment = models.DateField(verbose_name='Дата трудоустройства', null=True, blank=True)
    date_chief = models.DateField(verbose_name='Дата в должности', null=True, blank=True)
    employee_date = models.DateField(verbose_name='Дата увольнения', null=True, blank=True)
    number_ga = models.IntegerField(default=0, verbose_name='Номер табеля', null=True, blank=True)
    date_birth = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    home_address = models.CharField(max_length=255, verbose_name='Домашний адрес', null=True, blank=True)
    home_metro = models.CharField(max_length=255, verbose_name='Ближайшее метро', null=True, blank=True)
    gender = models.CharField(verbose_name='Пол', choices=GENDER_CHOICES, max_length=10, blank=True)

    def __str__(self):
        return '{0} {1} {2}'.format(self.user.surname, self.user.name, self.user.patronymic)

    def save(self, *args, **kwargs):
        """Изменение прав пользователя по группам"""
        try:
            self.user.groups.clear()
            self.user.groups.add(self.chief.group)
        except:
            pass
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь. Сотрудник. Общая информация.'
        verbose_name_plural = 'Пользователь. Сотрудники. Общая информация.'  # Во множественнмо числе
        ordering = ['user']  # Сортировка по каким полям, - обратная сортировка
        default_permissions = ('')
        permissions = (
            # Самостоятельное редактирование
            ('WorkerBasic_his_change', 'Пользователи. Сотрудник. Общая информация. Самостоятельно. Редактировать. '),

            # Редактирование данных
            ('WorkerBasic_department_change',
             'Пользователи. Сотрудник. Общая информация. Проверка отдела. Редактировать. '),
            ('WorkerBasic_subdivision_change',
             'Пользователи. Сотрудник. Общая информация. Проверка управления. Редактировать.'),
            ('WorkerBasic_management_change',
             'Пользователи. Сотрудник. Общая информация. Для руководства. Редактировать.'),

            # Просмотреть данные
            ('WorkerBasic_department_view',
             'Пользователи. Сотрудник. Общая информация. Проверка отдела. Просмотреть. '),
            ('WorkerBasic_subdivision_view',
             'Пользователи. Сотрудник. Общая информация. Проверка управления. Просмотреть.'),
            ('WorkerBasic_management_view',
             'Пользователи. Сотрудник. Общая информация. Для руководства. Просмотреть.'),
        )

    # При создании пользователя данная таблица создается автоматом
    @receiver(post_save, sender=Worker)
    def create_user_basic(sender, instance, created, **kwargs):
        if created:
            WorkerBasic.objects.create(user=instance)


def closed_path(instance, filename):
    upload_to = str('user/{0}/files/'.format(instance.user.pk))
    return os.path.join(upload_to, Files.random_name(filename))


class WorkerClosed(models.Model):
    """Закрытая информация о сотрудники"""
    user = models.OneToOneField(Worker, on_delete=models.PROTECT, verbose_name='ФИО')
    organization_order_of_employment = models.CharField(max_length=255, verbose_name='Приказ о трудоустройстве',
                                                        null=True, blank=True)
    organization_labor_contract = models.CharField(max_length=255, verbose_name='Трудовой договор', null=True,
                                                   blank=True)
    passport_serial = models.IntegerField(default=0, verbose_name='Паспорт Серия', null=True, blank=True)
    passport_number = models.IntegerField(default=0, verbose_name='Паспорт Номер', null=True, blank=True)
    passport_passport_issued = models.CharField(max_length=255, verbose_name='Паспорт Выдан', null=True, blank=True)
    passport_passport_issued_date = models.DateField(verbose_name='Паспорт Дата выдачи', null=True, blank=True)
    passport_place_of_issue = models.CharField(max_length=255, verbose_name='Паспорт Код подразделения', null=True,
                                               blank=True)
    passport_registration = models.CharField(max_length=255, verbose_name='Паспорт Место выдачи', null=True, blank=True)
    passport_of_residence = models.CharField(max_length=255, verbose_name='Паспорт Прописка', null=True,
                                             blank=True)
    passport_scan = models.FileField(upload_to=closed_path, verbose_name='Паспорт скан', null=True,
                                     blank=True)
    snils_number = models.CharField(max_length=255, verbose_name='СНИЛС номер', null=True,
                                    blank=True)
    snils_scan = models.FileField(upload_to=closed_path, verbose_name='СНИЛС скан', null=True,
                                  blank=True)
    inn_number = models.CharField(max_length=255, verbose_name='Инн номер', null=True,
                                  blank=True)
    inn_scan = models.FileField(upload_to=closed_path, verbose_name='Инн скан', null=True,
                                blank=True)
    archive_documents_employment = models.FileField(upload_to=closed_path,
                                                    verbose_name='Пакет документов при трудоустройстве',
                                                    null=True, blank=True)

    signature_example = models.ImageField(upload_to=closed_path, verbose_name='Пример подписи', null=True,
                                          blank=True)

    def __str__(self):
        return '{0} {1} {2}'.format(self.user.surname, self.user.name, self.user.patronymic)

    class Meta:
        verbose_name = 'Пользователи. Сотрудник. Закрытая информация.'
        verbose_name_plural = 'Пользователи. Сотрудники. Закрытая информация.'  # Во множественнмо числе
        ordering = ['pk']  # Сортировка по каким полям, - обратная сортировкаа
        default_permissions = ('')
        permissions = (
            # Самостоятельное редактирование
            ('WorkerClosed_his_change', 'Пользователи. Сотрудник. Закрытая информация. Самостоятельно. Редактировать. '),

            # Редактирование данных
            ('WorkerClosed_department_change',
             'Пользователи. Сотрудник. Закрытая информация. Проверка отдела. Редактировать. '),
            ('WorkerClosed_subdivision_change',
             'Пользователи. Сотрудник. Закрытая информация. Проверка управления. Редактировать.'),
            ('WorkerClosed_management_change',
             'Пользователи. Сотрудник. Закрытая информация. Для руководства. Редактировать.'),

            # Просмотреть данные
            ('WorkerClosed_department_view',
             'Пользователи. Сотрудник. Закрытая информация. Проверка отдела. Просмотреть. '),
            ('WorkerClosed_subdivision_view',
             'Пользователи. Сотрудник. Закрытая информация. Проверка управления. Просмотреть.'),
            ('WorkerClosed_management_view',
             'Пользователи. Сотрудник. Закрытая информация. Для руководства. Просмотреть.'),
        )


    # При создании пользователя данная таблица создается автоматом
    @receiver(post_save, sender=Worker)
    def create_user_closed(sender, instance, created, **kwargs):
        if created:
            WorkerClosed.objects.create(user=instance)

    def save(self, *args, **kwargs):
        # Загрузка образца подписи
        if self.signature_example:
            try:
                file_remove = WorkerClosed.objects.get(user__slug=self.user.slug)
                file_remove.signature_example.delete(save=True)
            except:
                pass

            self.signature_example = ImagesEdit.add_signature(self.signature_example, str(self.pk))

        super().save()
