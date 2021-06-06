from django.db import models
from django.core import validators
from django.utils import timezone

import jwt

from datetime import datetime, timedelta, date
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.core.validators import RegexValidator

ROLES_CHOICES = [('Admin', 'Админ'), ('Doctor', 'Врач'), ('Patient', 'Пациент')]
MENU_CHOICES = [('Breakfast', 'Завтрак'), ('Lunch', 'Обед'), ('Dinner', 'Обед')]
GENDER_CHOICES = [('Male', 'Мужской'), ('Female', 'Женский')]
PATIENT_STATUS_CHOICES = [('Accept', 'Принят'), ('Discharged', 'Выписан')]
PATIENT_TYPE_CHOICES = [('Vacationer', 'Отдыхающий'), ('Treating', 'Лечащийся'), ('Discharged', 'Выписан')]
# PATIENT_GROUP_CHOICES = [('Diabetic', 'Диабетик')]  # стоит дополнить
NOTIFICATION_STATUS_CHOICES = [('Sended', 'Отправлена'), ('Not Sended', 'Не отправлена')]
TASK_STATUS_CHOICES = [('Done', 'Сделана'), ('Not done', 'Не сделана')]
NOTIFICATION_SEND_TIME = [('5', 5), ('10', 10), ('30', 30), ('60', 60)]
RECOMMENDATION_CHOICES = [('Mandatory', 'Обязательный'), ('Permissive', 'Необязательный')]
MEDPERSONA_POSITION_CHOICES = [('Specialist', 'Специалист по услугам'), ('Doctor', 'Врач')]
MEDPERSONA_QUALIFICATION_CHOICES = [('0', 'Без категории'), ('1', 'Первая'), ('2', 'Вторая'), ('3', 'Высшая')]
SERVICE_CHOICES = [('Speciality', 'Специальность'), ('Procedure', 'Процедура'), ('Survey', 'Обследование'),
                   ('Event', 'Мероприятие')]


class UserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, email, name, surname, phone_number, role, patronymic=None, password=None, photo=None):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """

        if email is None:
            raise TypeError('Users must have an email address.')

        if password is None:
            raise TypeError('Users must have a password.')

        user = self.model(email=self.normalize_email(email), name=name,
                          surname=surname, patronymic=patronymic, phone_number=phone_number, role=role,
                          password=password, photo=photo)
        if not password:
            user.set_password(self.cleaned_data["password"])
        user.set_password(password)
        user.save()

        return user

    def create_user_admin(self, email, password):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """

        if email is None:
            raise TypeError('Users must have an email address.')

        if password is None:
            raise TypeError('Users must have a password.')

        user = self.model(email=self.normalize_email(email),
                          password=password)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user_admin(email=email, password=password)
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

    phone_number = models.CharField(max_length=18, blank=True)
    address = models.CharField(verbose_name='Адрес', max_length=100)

    class Meta:
        verbose_name = 'Санаторий'
        verbose_name_plural = 'Санатории'

    def __str__(self):
        return self.name


class UserProfile(AbstractBaseUser, PermissionsMixin):
    # username = models.CharField(db_index=True, max_length=255, unique=True)
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
    role = models.CharField(verbose_name='Роль', max_length=50, choices=ROLES_CHOICES)
    name = models.CharField(verbose_name='Имя', max_length=30)
    surname = models.CharField(verbose_name='Фамилия', max_length=30)
    patronymic = models.CharField(verbose_name='Отчество', max_length=30, blank=True)
    photo = models.ImageField(verbose_name='Фотография', upload_to='users', null=True, blank=True)

    phone_number = models.CharField(max_length=18, blank=True)

    # Свойство USERNAME_FIELD сообщает нам, какое поле мы будем использовать
    # для входа в систему. В данном случае мы хотим использовать почту.
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

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

    def get_name(self):
        delim = ''
        name_parts = [self.name, self.surname, self.patronymic]
        full_name = ''
        for part in name_parts:
            if part != '':
                full_name += delim + part
                delim = ' '

        return full_name

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей, как обработка электронной
        почты. Обычно это имя фамилия пользователя, но поскольку мы не
        используем их, будем возвращать username.
        """
        return self.email

    def get_short_name(self):
        """ Аналогично методу get_full_name(). """
        return self.email

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """

        dt = datetime.now() + timedelta(days=30)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.encode().decode('utf-8')


# Восстановление доступа????

class Notification(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    # тип
    name = models.CharField(verbose_name='Тип', max_length=50)
    description = models.TextField(verbose_name='Содержание')
    source = models.CharField(verbose_name='Источник', max_length=50)
    date_of_sending = models.DateField(verbose_name='Дата отправки', blank=True, default=timezone.now)
    status = models.CharField(verbose_name='Статус', max_length=50, choices=NOTIFICATION_STATUS_CHOICES)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class NotificationSettings(models.Model):
    # Источник уведомления(тип)
    time = models.IntegerField(verbose_name='Время', choices=NOTIFICATION_SEND_TIME)
    user = models.ForeignKey(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Конфигурация уведомлений'
        verbose_name_plural = 'Конфигурация уведомлений'


class Notes(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Заголовок', max_length=50)
    date_of_creation = models.DateField(verbose_name='Дата создания', blank=True, default=timezone.now)

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'


class Task(models.Model):
    description = models.TextField(verbose_name='Содержание')
    status = models.CharField(verbose_name='Статус', max_length=50, choices=TASK_STATUS_CHOICES)
    note = models.ForeignKey(Notes, verbose_name='Заметки', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class Admin(models.Model):
    user = models.OneToOneField(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    position = models.CharField(verbose_name='Должность', max_length=30)

    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'

    def __str__(self):
        return self.user.get_name()


class Patient(models.Model):
    user = models.OneToOneField(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    birth_date = models.DateField(verbose_name='Дата рождения', default=date.today)
    gender = models.CharField(verbose_name='Пол', max_length=50, choices=GENDER_CHOICES)
    # РЕГИОН И ГОРОД ПО ЛОГИКЕ ДОЛЖНЫ БЫТЬ ОТДЕЛЬНЫМИ ТАБЛИЦАМИ!!!!!!!
    region = models.CharField(verbose_name='Регион', max_length=30)
    city = models.CharField(verbose_name='Город', max_length=30)
    receipt_date = models.DateTimeField(verbose_name='Дата поступления', blank=True, default=timezone.now)

    # bonus = models.CharField(verbose_name='Бонус', max_length=30)
    # status = models.CharField(verbose_name='Статус', max_length=50, choices=PATIENT_STATUS_CHOICES)
    # api_tracker = models.CharField(verbose_name='Апи-трекера', max_length=200)
    type = models.CharField(verbose_name='Категория', max_length=50, choices=PATIENT_TYPE_CHOICES)
    group = ArrayField(models.CharField(verbose_name='Группа', max_length=50), blank=True)
    complaints = models.TextField(verbose_name='Жалобы при поступлении', default='Нет жалоб')

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def __str__(self):
        return self.user.get_name()
    # TODO Регионы и города


class Service(models.Model):
    sanatory = models.ForeignKey(Sanatorium, verbose_name='Санаторий', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, verbose_name='Название', unique=True)
    cost = models.FloatField(verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.name


class TimeTable(models.Model):
    service = models.OneToOneField(Service, verbose_name='Услуга', on_delete=models.CASCADE)
    dates = ArrayField(models.DateTimeField(), null=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'


class MedPersona(models.Model):
    user = models.OneToOneField(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    birth_date = models.DateField(verbose_name='Дата рождения')
    position = models.CharField(verbose_name='Должность', max_length=30, choices=MEDPERSONA_POSITION_CHOICES)
    qualification = models.CharField(verbose_name='Квалификация', max_length=30,
                                     choices=MEDPERSONA_QUALIFICATION_CHOICES)
    # specialty = models.CharField(verbose_name='Специальность', max_length=30)
    experience = models.CharField(verbose_name='Стаж', max_length=30)
    location = models.CharField(verbose_name='Расположение (кабинет)', max_length=256, null=True, blank=True)
    specialization = models.TextField(blank=True, null=True, verbose_name='Специализация')
    education = ArrayField(models.TextField(), verbose_name='Образование', blank=True, null=True)

    class Meta:
        verbose_name = 'Мед персона'
        verbose_name_plural = 'Мед персоны'

    def __str__(self):
        return self.user.get_name()


class ServiceMedPersona(models.Model):
    service = models.ForeignKey(Service, verbose_name='Услуга', on_delete=models.CASCADE)
    medpersona = models.ForeignKey(MedPersona, verbose_name='Мед персона', on_delete=models.CASCADE)
    type = models.CharField(verbose_name='Тип', max_length=30, choices=SERVICE_CHOICES)

    class Meta:
        verbose_name = 'Услуга-Медперсона'
        verbose_name_plural = 'Услуги-Медперсоны'  # ??


class Medcard(models.Model):
    patient = models.OneToOneField(Patient, verbose_name='Пациент', on_delete=models.CASCADE)
    height = models.IntegerField(verbose_name='Рост', null=True, blank=True)
    # расписание занятий ??
    allergies = ArrayField(models.CharField(max_length=256, blank=True), default=list, blank=True)
    rsk = models.IntegerField(verbose_name='Рекомендуемая суточная норма калорий', null=True, blank=True)
    complaints = models.TextField(verbose_name='Жалобы', help_text='Общие субъективные жалобы')

    class Meta:
        verbose_name = 'Медкарта'
        verbose_name_plural = 'Медкарты'


class Epyicrisis(models.Model):
    medcard = models.ForeignKey(Medcard, verbose_name='Медкарта', on_delete=models.CASCADE)
    medpersona = models.OneToOneField(MedPersona, verbose_name='Мед персона', on_delete=models.CASCADE, null=True)
    date = models.DateField(verbose_name='Дата создания')
    # анамнез = ...
    complaints = models.TextField(verbose_name='Жалобы')

    # persona
    class Meta:
        verbose_name = 'Эпикриз'
        verbose_name_plural = 'Эпикризы'


class PassportData(models.Model):
    user = models.OneToOneField(UserProfile, verbose_name='Пользователь', on_delete=models.CASCADE)
    series_number = models.CharField(verbose_name='Серия и номер', max_length=20)
    code = models.CharField(verbose_name='Код подразделения', max_length=10)
    date = models.DateField(verbose_name='Дата выдачи')
    by_whom = models.CharField(max_length=255, verbose_name='Кем выдан')

    class Meta:
        verbose_name = 'Паспортные данные'
        verbose_name_plural = 'Паспортные данные'

    def __str__(self):
        return self.user.get_name()


# Опрос/Анкета должна перейти в две таблицы Вопрос и Анкета - где Анкета будет содеражть список Вопросов

class Question(models.Model):
    question = models.CharField(max_length=250, verbose_name='Вопрос')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.question


class Answer(models.Model):
    answer = models.TextField(verbose_name='Ответ')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class FAQ(models.Model):
    sanatory = models.ForeignKey(Sanatorium, verbose_name='Санаторий', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='Вопрос', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, verbose_name='Ответ', on_delete=models.CASCADE)


class Menu(models.Model):
    sanatory = models.ForeignKey(Sanatorium, verbose_name='Санаторий', on_delete=models.CASCADE)
    ration = models.CharField(verbose_name='Рацион', max_length=50, choices=MENU_CHOICES)

    # Расписание?

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'


class Dish(models.Model):
    menu = models.ForeignKey(Menu, verbose_name='Меню', on_delete=models.CASCADE)
    # тип блюда?

    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'


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
    name = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    date = models.DateField(verbose_name='Дата создания')

    # source = models.CharField(verbose_name='Источник', max_length=255)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.name


class Translation(models.Model):
    sanatorium = models.OneToOneField(Sanatorium, verbose_name='Санаторий', on_delete=models.CASCADE)
    heading = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    created = models.DateTimeField(editable=False, verbose_name='Дата создания')

    # ссылка на трансляцию ??

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(Translation, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Трансляция'
        verbose_name_plural = 'Трансляции'


class Procedure(models.Model):
    service = models.OneToOneField(Service, verbose_name='Услуга', on_delete=models.CASCADE, null=True)
    photo = models.ImageField(verbose_name='Фото', upload_to='procedures', null=True)
    description = models.TextField(verbose_name='Описание')
    contraindications = ArrayField(models.CharField(verbose_name='Противопоказания', max_length=256), null=True,
                                   blank=True)
    purposes = ArrayField(models.CharField(verbose_name='Назначения', max_length=256), null=True, blank=True)
    placement = models.CharField(verbose_name='Расположение', max_length=50)

    # назначения ??

    class Meta:
        verbose_name = 'Процедура'
        verbose_name_plural = 'Процедуры'


class Speciality(models.Model):
    service = models.OneToOneField(Service, verbose_name='Услуга', on_delete=models.CASCADE, null=True)

    # назначения ??

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'


class Event(models.Model):
    service = models.OneToOneField(Service, verbose_name='Услуга', on_delete=models.CASCADE, null=True)
    photo = models.ImageField(verbose_name='Фото', upload_to='events', null=True)
    description = models.TextField(verbose_name='Содержание')
    begin_data = models.DateField(verbose_name='Дата начала')
    end_data = models.DateField(verbose_name='Дата окончания', null=True, blank=True)
    placement = models.CharField(verbose_name='Расположение', max_length=50)

    # назначения ??

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


class Survey(models.Model):
    service = models.OneToOneField(Service, verbose_name='Услуга', on_delete=models.CASCADE, null=True)
    description = models.TextField(verbose_name='Описание')
    purposes = ArrayField(models.CharField(verbose_name='Назначения', max_length=256), null=True, blank=True)
    photo = models.ImageField(verbose_name='Фото', upload_to='surveys', null=True)
    placement = models.CharField(verbose_name='Расположение', max_length=50)

    class Meta:
        verbose_name = 'Обследовние'
        verbose_name_plural = 'Обследования'


# таблица специальность

class Recommendation(models.Model):
    epyicrisis = models.OneToOneField(Epyicrisis, verbose_name='Эпикриз', on_delete=models.CASCADE)
    type = models.CharField(max_length=255, verbose_name='Тип', choices=RECOMMENDATION_CHOICES)

    # период

    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'


class RecommendationProcedure(models.Model):
    recommendation = models.OneToOneField(Recommendation, verbose_name='Рекомендация', on_delete=models.CASCADE)
    procedure = models.OneToOneField(Procedure, verbose_name='Процедура', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рекомендация-Процедура'
        verbose_name_plural = 'Рекомендации-Процедуры'
