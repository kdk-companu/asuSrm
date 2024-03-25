import os
import random
from uuid import uuid4

from PIL import Image


class ImagesEdit:
    def add_avatar(image, user):
        """Добавление аватарок"""
        # Полный путь к папкам
        folder_user = "media/user/" + user
        folder_save = "media/user/" + user + "/images/"
        url_save = "user/" + user + "/images/"
        # Создание папок
        if not os.path.isdir(folder_user):
            os.mkdir(folder_user)
        if not os.path.isdir(folder_save):
            os.mkdir(folder_save)
        # Очистка папки от всех файлов
        out = dict()
        img = Image.open(image)
        width = image.width
        height = image.height
        min_size = min(width, height)
        # # Обрезка картинки до квадрата
        img = img.crop((0, 0, min_size, min_size))
        # # Первое уменьшение
        oputput_size = (300, 300)
        img.thumbnail(oputput_size)
        out['image'] = '{0}{1}'.format(url_save, "photo.jpg")
        img.save('{0}{1}'.format(folder_save, "photo.jpg"))
        # Второе уменьшение
        oputput_size = (128, 128)
        img.thumbnail(oputput_size)
        out['images_smol'] = '{0}{1}'.format(url_save, "photo_smol.jpg")
        img.save('{0}{1}'.format(folder_save, "photo_smol.jpg"))
        return out

    def add_signature(image, user):
        folder_user = "media/user/" + str(user)
        folder_save = "media/user/" + str(user) + "/files/"
        url_save = "user/" + str(user) + "/files/"
        # Создание папок
        if not os.path.isdir(folder_user):
            os.mkdir(folder_user)
        if not os.path.isdir(folder_save):
            os.mkdir(folder_save)
        # Обработка изображнеий
        img = Image.open(image)
        width = img.size[0]
        height = img.size[1]
        max_size = max(width, height)
        # Обрезка картинки до квадрата
        img = img.crop((0, 0, 700, 350))
        # Первое уменьшение
        name_file = uuid4().hex + ".png"
        img.save('{0}{1}'.format(folder_save, name_file))

        return '{0}{1}'.format(url_save, name_file)
