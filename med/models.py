from django.db import models
from django.core import validators

import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

ROLES_CHOICES = [('Admin', 'Админ'), ('Doctor', 'Врач'), ('Patient', 'Пациент')]
GENDER_CHOICES = [('Male', 'Мужской'), ('Female', 'Женский')]
PATIENT_STATUS_CHOICES = [('Accept', 'Принят'), ('Discharged', 'Выписан')]
PATIENT_TYPE_CHOICES = [('Vacationer', 'Отдыхающий'), ('Treating', 'Лечащийся')]


class UserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, username, email, password=None):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username=username, email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class Sanatorium(models.Model):
    name = models.CharField(verbose_name='Название санатория', max_length=30)
    email = models.EmailField(verbose_name='Адрес почты',
                              validators=[validators.validate_email],
                              unique=True,
                              blank=False
                              )
    tel = models.CharField(verbose_name='Телефон', max_length=20)
    adress = models.CharField(verbose_name='Адерс', max_length=20)

    class Meta:
        verbose_name = 'Санаторий'
        verbose_name_plural = 'Санатории'

    def __str__(self):
        return self.name


class UserProfile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)

    # Когда пользователь более не желает пользоваться нашей системой, он может
    # захотеть удалить свой аккаунт. Для нас это проблема, так как собираемые
    # нами данные очень ценны, и мы не хотим их удалять :) Мы просто предложим
    # пользователям способ деактивировать учетку вместо ее полного удаления.
    # Таким образом, они не будут отображаться на сайте, но мы все еще сможем
    # далее анализировать информацию.
    is_active = models.BooleanField(default=True)

    # Этот флаг определяет, кто может войти в административную часть нашего
    # сайта. Для большинства пользователей это флаг будет ложным.
    is_staff = models.BooleanField(default=False)

    # Временная метка создания объекта.
    created_at = models.DateTimeField(auto_now_add=True)

    # Временная метка показывающая время последнего обновления объекта.
    updated_at = models.DateTimeField(auto_now=True)

    # Дополнительный поля, необходимые Django
    # при указании кастомной модели пользователя.
    role = models.CharField(verbose_name='Роль', max_length=30, choices=ROLES_CHOICES)
    firstName = models.CharField(verbose_name='Имя', max_length=30,null=True)
    secondName = models.CharField(verbose_name='Фамилия', max_length=30,null=True)
    thirdName = models.CharField(verbose_name='Отчество', max_length=30,null=True)
    photo = models.ImageField(verbose_name='Ключ', upload_to='users', null=True)
    tel = models.CharField(verbose_name='Телефон', max_length=20,null=True)
    # Свойство USERNAME_FIELD сообщает нам, какое поле мы будем использовать
    # для входа в систему. В данном случае мы хотим использовать почту.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Сообщает Django, что определенный выше класс UserManager
    # должен управлять объектами этого типа.
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """ Строковое представление модели (отображается в консоли) """
        return self.email

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей, как обработка электронной
        почты. Обычно это имя фамилия пользователя, но поскольку мы не
        используем их, будем возвращать username.
        """
        return self.username

    def get_short_name(self):
        """ Аналогично методу get_full_name(). """
        return self.username

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.encode().decode('utf-8')


class Admin(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    position = models.CharField(verbose_name='Должность', max_length=30)

    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'

    def __str__(self):
        name = self.user.firstName + ' ' + self.user.secondName + ' ' + self.user.thirdName
        return name




class Patient(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    birth_date = models.DateField(verbose_name='Дата рождения')
    gender = models.CharField(verbose_name='Пол', max_length=30, choices=GENDER_CHOICES)
    # РЕГИОН И ГОРОД ПО ЛОГИКЕ ДОЛЖНЫ БЫТЬ ОТДЕЛЬНЫМИ ТАБЛИЦАМИ!!!!!!!
    region = models.CharField(verbose_name='Город', max_length=30)
    city = models.CharField(verbose_name='Регион', max_length=30)

    bonus = models.CharField(verbose_name='Бонус', max_length=30)
    status = models.CharField(verbose_name='Статус', max_length=30, choices=PATIENT_STATUS_CHOICES)
    api_tracker = models.CharField(verbose_name='Апи-трекера', max_length=200)
    type = models.CharField(verbose_name='Тип', max_length=30, choices=PATIENT_TYPE_CHOICES)

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def __str__(self):
        name = self.user.firstName + ' ' + self.user.secondName + ' ' + self.user.thirdName
        return name
    # TODO Регионы и города


class PasportData(models.Model):
    patient = models.ForeignKey(Patient, verbose_name='Пациент', on_delete=models.CASCADE)
    series = models.IntegerField(verbose_name='Серия')
    number = models.IntegerField(verbose_name='Номер')
    date = models.DateField(verbose_name='Дата выдачи')
    by_whom = models.CharField(max_length=255, verbose_name='Кем выдан')

    class Meta:
        verbose_name = 'Поспортные данные'
        verbose_name_plural = 'Поспортные данные'

    def __str__(self):
        name = self.patient.user.firstName + ' ' + self.patient.user.secondName + ' ' + self.patient.user.thirdName
        return name


# Опрос/Анкета должна перейти в две таблицы Вопрос и Анкета - где Анкета будет содеражть список Вопросов

class Question(models.Model):
    question = models.CharField(max_length=250, verbose_name='Вопрос')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.question


class Form(models.Model):
    question = models.ManyToManyField(Question, verbose_name='Вопросы')
    patient = models.ForeignKey(Patient, verbose_name='Пациент', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Дата создания опроса')

    class Meta:
        verbose_name = 'Анкета пациента'
        verbose_name_plural = 'Анкеты пациентов'

    def __str__(self):
        return 'Анкета от ' + str(self.patient.id)


# Ответы на вопросы нужны???

class Article(models.Model):
    sanatory = models.ForeignKey(Sanatorium, verbose_name='Санаторий', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Название')
    content = models.TextField(verbose_name='Содержание')
    date = models.DateField(verbose_name='Дата создания')
    source = models.CharField(verbose_name='Источник', max_length=255)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.name
