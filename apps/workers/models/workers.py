import os

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from transliterate import translit
from django.template.defaultfilters import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.urls import reverse
from apps.workers.models.managers import UserManager
from PIL import Image


def user_path(instance, filename):
    return 'user/{0}/images/{1}'.format(instance.slug, filename)


class User(AbstractBaseUser,PermissionsMixin):
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
    email = models.EmailField(unique=False, verbose_name='Электронная почта')
    # Аватарки
    image = models.ImageField(upload_to=user_path, null=True, blank=True, verbose_name='Фото')
    image_smol = models.ImageField(upload_to=user_path, null=True, blank=True, verbose_name='Фото маленькое')
    # Текущий статус работника
    employee = models.CharField(verbose_name='Сотрудник', choices=WORKERS_STATUS, max_length=30, default='employee_current')
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
        slug_name = self.surname + "" + self.name + "" + self.patronymic
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
        return reverse('workers_views', kwargs={'workers_slug': self.slug})
