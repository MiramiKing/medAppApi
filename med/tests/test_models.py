from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from med.models import *


class UserProfileTests(APITestCase):
    # вызывается один раз для подготовки неизменяемых
    # данных для всех методов класса
    @classmethod
    def setUpTestData(cls):
        UserProfile.objects.create_user(
            email='user1@mail.com',
            name='name1',
            surname='surname1',
            patronymic='patronymic1',
            phone_number='+79998887766',
            role='Patient',
            password='user1password',
        )
        UserProfile.objects.create_user_admin(
            email='admin1@mail.com',
            password='admin1password',
        )
        UserProfile.objects.create_superuser(
            email='su1@mail.com',
            password='su1password',
        )

    # Вызывается для перед каждым методом
    def setUp(self):
        self.user = UserProfile.objects.get(email='user1@mail.com')
        self.admin = UserProfile.objects.get(email='admin1@mail.com')
        self.superuser = UserProfile.objects.get(email='su1@mail.com')

    # Тест на уникальность входных данных
    def test_unique(self):
        try:
            UserProfile.objects.create_user(
                email='user1@mail.com',
                name='name1',
                surname='surname1',
                patronymic='patronymic1',
                phone_number='+79998887766',
                role='Patient',
                password='user1password',
            )
        except:
            pass
        else:
            self.assertFalse(True)

        try:
            UserProfile.objects.create_user_admin(
                email='admin1@mail.com',
                password='admin1password',
            )
        except:
            pass
        else:
            self.assertFalse(True)

        try:
            UserProfile.objects.create_superuser(
                email='su1@mail.com',
                password='su1password',
            )
        except:
            pass
        else:
            self.assertFalse(True)

    # Тест флагов is_active, is_staff, is_superuser
    def test_flags(self):
        # Обычный пользователь
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

        # Администратор
        self.assertTrue(self.admin.is_active)
        # self.assertTrue(self.admin.is_staff)
        self.assertFalse(self.admin.is_superuser)

        # Суперпользователь
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    # Тест типа пользователя
    def test_role(self):
        self.assertEquals(self.user.role, 'Patient')
        self.assertEquals(self.admin.role, '')
        self.assertEquals(self.superuser.role, '')

    # Тест склеивания ФИО
    def test_fullname(self):
        UserProfile.objects.create_user(
            email='user2@mail.com',
            name='name2',
            surname='surname2',
            patronymic='',
            phone_number='+79998887766',
            role='Patient',
            password='user2password',
        )
        UserProfile.objects.create_user(
            email='user3@mail.com',
            name='name3',
            surname='',
            patronymic='patronymic3',
            phone_number='+79998887766',
            role='Patient',
            password='user3password',
        )

        user2 = UserProfile.objects.get(email='user2@mail.com')
        user3 = UserProfile.objects.get(email='user3@mail.com')

        self.assertEquals(user2.get_name(), 'name2 surname2')
        self.assertEquals(user3.get_name(), 'name3 patronymic3')


class AdminTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserProfile.objects.create_user(
            email='user1@mail.com',
            name='name1',
            surname='surname1',
            patronymic='patronymic1',
            phone_number='+79998887766',
            role='Admin',
            password='user1password',
        )
        admin = UserProfile.objects.create_user_admin(
            email='admin1@mail.com',
            password='admin1password',
        )
        superuser = UserProfile.objects.create_superuser(
            email='su1@mail.com',
            password='su1password',
        )
        Admin.objects.create(user=user, position='Админ (пользователь)')
        Admin.objects.create(user=admin, position='Админ (админ)')
        Admin.objects.create(user=superuser, position='Админ (суперпользователь)')

    def setUp(self):
        self.admin_user = Admin.objects.get(user__email='user1@mail.com')
        self.admin_admin = Admin.objects.get(user__email='admin1@mail.com')
        self.admin_superuser = Admin.objects.get(user__email='su1@mail.com')

    def test_position_field(self):
        max_length = self.admin_user._meta.get_field('position').max_length;
        self.assertEquals(max_length, 30);

        self.assertEquals(self.admin_user.position, 'Админ (пользователь)')
        self.assertEquals(self.admin_admin.position, 'Админ (админ)')
        self.assertEquals(self.admin_superuser.position, 'Админ (суперпользователь)')

        user_admin = UserProfile.objects.create_user_admin(
            email='admin2@mail.com',
            password='admin2password'
        )

        # это проверять не обязательно, но почему и нет
        # хочется удостовериться в правильном понимании того, что происходит внутри
        try:
            admin = Admin.objects.create(user=user_admin, position='эта строка больше чем 30 знаков')
        except:
            pass
        else:
            self.assertFalse(True)

    def test_creation(self):
        user_admin = UserProfile.objects.create_user_admin(
            email='admin2@mail.com',
            password='admin2password'
        )
        admin = Admin.objects.create(user=user_admin)
        self.assertEquals(admin.position, '')

        # так же как и проверка длины строки в test_position_field эта проверка
        # необязательна
        try:
            another_admin = Admin.objects.create(user=user_admin)
        except:
            pass
        else:
            self.assertFalse(True)

    def test_name(self):
        self.assertEquals(str(self.admin_user), 'name1 surname1 patronymic1')


class PatientTests(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email='user1@mail.com',
            name='name1',
            surname='surname1',
            patronymic='patronymic1',
            phone_number='+79998887766',
            role='Patient',
            password='user1password',
        )

    def test_full_creation(self):
        try:
            Patient.objects.create(
                user=self.user,
                birth_date='2001-07-04',
                gender='Male',
                region='Patients Region',
                city='Patients City',
                receipt_date='2021-09-01T10:20:00Z',
                type='Vacationer',
                group=["Patient's Group"],
                complaints='No complaints',
            )
        except:
            self.assertFalse(True)

    def test_min_creation(self):
        try:
            Patient.objects.create(
                user=self.user,
                gender='Male',
                type='Vacationer',
                group=[],
            )
        except:
            self.assertFalse(True)


class MedPersonaTests(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email='user1@mail.com',
            name='name1',
            surname='surname1',
            patronymic='patronymic1',
            phone_number='+79998887766',
            role='Doctor',
            password='user1password',
        )

    def test_full_creation(self):
        try:
            MedPersona.objects.create(
                user=self.user,
                birth_date='2001-07-04',
                position='Specialist',
                qualification='3',
                experience='3 years',
                location=404,
                specialization='Doctors Specialization',
                education=["Doctor's education"],
            )
        except:
            self.assertFalse(True)

    def test_min_creation(self):
        try:
            MedPersona.objects.create(
                user=self.user,
                birth_date='2001-07-04',
                position='Specialist',
                qualification='3',
                experience='3 years',
            )
        except:
            self.assertFalse(True)


'''Для остальных тесты можно написать потом '''

# Услуга
# Услуга-Медперсона
# Процедура
# Обследование
# Специальность
# Мероприятие

# Санаторий
# Новости
# Трансляция
# Расписание

# Рекомендация
# Рекомендация-Процедура

# Анкета
# Вопрос
# Ответ
# FAQ

# Меню
# Блюдо

# Медкарта
# Эпикриз
# Паспортные данные

# Заметка
# Задача

# Уведомление
# Конфигурация