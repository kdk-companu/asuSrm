import os
import datetime
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import ModelSignal, post_save
from transliterate import translit
from django.template.defaultfilters import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.urls import reverse
from django.dispatch import receiver
from apps.workers.models import Organization, Subdivision, Department, Chief
from apps.workers.models.managers import UserManager
from PIL import Image


# Аватарки
def user_path(instance, filename):
    return 'user/{0}/images/{1}'.format(instance.slug, filename)


class User(AbstractBaseUser, PermissionsMixin):
    """Сотрудники переписанная от User
        https://docs.djangoproject.com/en/4.1/ref/models/instances/"""

    WORKERS_STATUS = (
        ('employee_current', 'Сотрудник действующий'),
        ('employee_fired', 'Сотрудник уволенный'),
        ('contractor_current', 'Подрядчик действующий'),
        ('contractor_fired', 'Подрядчик уволенный'),
        ('exploitation_current', 'Эксплуатация действующий'),
        ('exploitation_fired', 'Эксплуатация уволенный'),
        ('technician_current', 'Наладчик действующий'),
        ('technician_fired', 'Наладчик уволенный')
    )

    # ФИО
    surname = models.CharField(max_length=60, unique=False, verbose_name='Фамилия')
    name = models.CharField(max_length=60, unique=False, verbose_name='Имя')
    patronymic = models.CharField(max_length=60, unique=False, verbose_name='Отчество')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name='slug')
    # Контакты
    phone = PhoneNumberField(null=False, blank=False, unique=True, verbose_name='Телефон')
    email = models.EmailField(unique=False, verbose_name='Почта')
    # Аватарки
    image = models.ImageField(upload_to=user_path, null=True, blank=True, verbose_name='Фото')
    image_smol = models.ImageField(upload_to=user_path, null=True, blank=True, verbose_name='Фото маленькое')
    # Текущий статус работника
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, blank=False, null=True,
                                     verbose_name='Организация')
    employee = models.CharField(verbose_name='Статус', choices=WORKERS_STATUS, max_length=30,
                                default='employee_current')
    # Система прав
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['surname', 'name', 'patronymic']
    objects = UserManager()

    def __str__(self):
        return '{0} {1} {2}'.format(self.surname, self.name, self.patronymic)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['pk']
        default_permissions = ('')

        permissions = (
            ('user_add', 'Добавить.'),
            ('user_change', 'Редактировать.'),
            ('user_delete', 'Удалить.'),
            ('user_view', 'Просмотреть.'),
        )

    def save(self, *args, **kwargs):
        # Создаем slug
        date_add = datetime.date.today().strftime("%d-%m-%Y")
        slug_name = "{0}{1}{2}{3}".format(self.surname,self.name,self.patronymic,date_add)
        self.slug = slugify(translit(slug_name, 'ru', reversed=True))
        # Сохранение фотографий
        if self.image:
            # Полный путь к папкам
            folder_user = "media/user/" + str(self.pk)
            folder_save = "media/user/" + str(self.pk) + "/images/"
            url_save = "user/" + str(self.pk) + "/images/"
            # Создание папок
            if not os.path.isdir(folder_user):
                os.mkdir(folder_user)
            if not os.path.isdir(folder_save):
                os.mkdir(folder_save)
            # Обработка изображнеий
            img = Image.open(self.image)
            width = self.image.width
            height = self.image.height
            min_size = min(width, height)
            # Обрезка картинки до квадрата
            img = img.crop((0, 0, min_size, min_size))
            # Первое уменьшение
            oputput_size = (300, 300)
            img.thumbnail(oputput_size)
            img.save(folder_save + "photo.jpg")
            self.image = url_save + "photo.jpg"
            # Второе уменьшение
            oputput_size = (128, 128)
            img.thumbnail(oputput_size)
            img.save(folder_save + "smol_photo.jpg")
            self.image_smol = url_save + "smol_photo.jpg"

        super().save()

    def get_absolute_url(self):
        return reverse('workers_detailView', kwargs={'workers_slug': self.slug})


class User_Basic(models.Model):
    """Базовая информация о сотрудниках"""
    GENDER_CHOICES = (
        ('Male', 'Мужской'),
        ('Female', 'Женский'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='ФИО')
    organization_subdivision = models.ForeignKey(Subdivision, on_delete=models.PROTECT, blank=True,
                                                 null=True, related_name='organization_subdivision',
                                                 verbose_name='Управление в организации')
    organization_department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True,
                                                null=True, related_name='organization_department',
                                                verbose_name='Отдел в организации')
    actual_subdivision = models.ForeignKey(Subdivision, on_delete=models.PROTECT, blank=True,
                                           null=True, related_name='actual_subdivision',
                                           verbose_name='Управление в организации')
    actual_department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True,
                                          null=True, related_name='actual_department',
                                          verbose_name='Отдел в организации')
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

    class Meta:
        verbose_name = 'Сотрудники общая информация'
        verbose_name_plural = 'Сотрудники общая информация'  # Во множественнмо числе
        ordering = ['pk']  # Сортировка по каким полям, - обратная сортировка
        default_permissions = ('')
        permissions = (
            ('user_basic_change', 'Редактировать.'),
            ('user_basic_view', 'Просмотреть.'),
        )

    # При создании пользователя данная таблица создается автоматом
    @receiver(post_save, sender=User)
    def create_user_basic(sender, instance, created, **kwargs):
        if created and instance.employee == "employee_current":
            User_Basic.objects.create(user=instance)


class User_Closed(models.Model):
    '''Закрытая информация о сотрудники'''
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='ФИО')
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
    passport_of_residence = models.CharField(max_length=255, verbose_name='Паспорт Место жительства', null=True,
                                             blank=True)

    # passport_scan = models.FileField(upload_to=user_directory_path_save, verbose_name='Паспорт скан', null=True,
    #                                  blank=True)
    # snils_number = models.CharField(max_length=255, verbose_name='СНИЛС номер', null=True,
    #                                 blank=True)
    # snils_scan = models.FileField(upload_to=user_directory_path_save, verbose_name='СНИЛС скан', null=True,
    #                               blank=True)
    # inn_number = models.CharField(max_length=255, verbose_name='Инн номер', null=True,
    #                               blank=True)
    # inn_scan = models.FileField(upload_to=user_directory_path_save, verbose_name='Инн скан', null=True,
    #                             blank=True)
    # archive_documents_employment = models.FileField(upload_to=user_directory_path_save,
    #                                                 verbose_name='Пакет документов при трудоустройстве',
    #                                                 null=True, blank=True)
    #
    # signature_example = models.ImageField(upload_to=user_directory_path_files, verbose_name='Пример подписи', null=True,
    #                                       blank=True)

    def __str__(self):
        return '{0} {1} {2}'.format(self.user.surname, self.user.name, self.user.patronymic)

    class Meta:
        verbose_name = 'Сотрудники закрытая информация'
        verbose_name_plural = 'Сотрудники закрытая информация'  # Во множественнмо числе
        ordering = ['pk']  # Сортировка по каким полям, - обратная сортировкаа
        default_permissions = ('')
        permissions = (
            ('user_closed_change', 'Редактировать.'),
            ('user_closed_view', 'Просмотреть.'),
        )

    # При создании пользователя данная таблица создается автоматом
    @receiver(post_save, sender=User)
    def create_user_closed(sender, instance, created, **kwargs):
        if created:
            User_Closed.objects.create(user=instance)

    def save(self, *args, **kwargs):
        # # Загрузка образца подписи
        # if self.signature_example and not '/' in str(self.signature_example):
        #     try:
        #         file_remove = User_Closed_Information.objects.get(user__slug=self.user.slug)
        #         file_remove.signature_example.delete(save=False)
        #     except:
        #         pass
        #     # Полный путь к папкам
        #     folder_user = "media/user/" + str(self.user.pk)
        #     folder_save = "media/user/" + str(self.user.pk) + "/files/"
        #     url_save = "user/" + str(self.user.pk) + "/files/"
        #     # Создание папок
        #     if not os.path.isdir(folder_user):
        #         os.mkdir(folder_user)
        #     if not os.path.isdir(folder_save):
        #         os.mkdir(folder_save)
        #     # Обработка изображнеий
        #     img = Image.open(self.signature_example)
        #     width = img.size[0]
        #     height = img.size[1]
        #     max_size = max(width, height)
        #     # Обрезка картинки до квадрата
        #     img = img.crop((0, 0, 700, 350))
        #     # Первое уменьшение
        #     name_file = uuid4().hex + ".png"
        #     img.save(folder_save + name_file)
        #     self.signature_example = url_save + name_file
        # # Загрузка паспорта
        # if self.passport_scan and not '/' in str(self.passport_scan):
        #     try:
        #         passport_remove = User_Closed_Information.objects.get(user__slug=self.user.slug)
        #         passport_remove.passport_scan.delete(save=False)
        #     except:
        #         pass
        # if self.inn_scan and not '/' in str(self.inn_scan):
        #     try:
        #         inn_remove = User_Closed_Information.objects.get(user__slug=self.user.slug)
        #         inn_remove.inn_scan.delete(save=False)
        #     except:
        #         pass
        # if self.snils_scan and not '/' in str(self.snils_scan):
        #     try:
        #         snils_remove = User_Closed_Information.objects.get(user__slug=self.user.slug)
        #         snils_remove.snils_scan.delete(save=False)
        #     except:
        #         pass
        # if self.archive_documents_employment and not '/' in str(self.archive_documents_employment):
        #     try:
        #         archive_documents_employment_remove = User_Closed_Information.objects.get(user__slug=self.user.slug)
        #         archive_documents_employment_remove.archive_documents_employment.delete(save=False)
        #     except:
        #         pass

        super().save()
