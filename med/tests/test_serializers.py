from rest_framework.test import APITestCase
from med.serializers import *

class RegistrationSerializerTests(APITestCase):
    def setUp(self):
        self.data = {
            'email': 'user1@mail.com',
            'phone_number': '+79998887766',
            'role': 'Patient',
            'name': 'name1',
            'surname': 'surname1',
            'patronymic': 'patronymic1',
            'password': 'user1password',
            'photo': None,
        }

    def test_creation(self):
        serializer = RegistrationSerializer(data=self.data)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())


class LoginSerializerTests(APITestCase):
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

        inactive_user = UserProfile.objects.create_user(
            email='user2@mail.com',
            name='name2',
            surname='surname2',
            patronymic='patronymic2',
            phone_number='+79998887765',
            role='Patient',
            password='user2password',
        )
        inactive_user.is_active = False
        inactive_user.save()

    def test_login_validation(self):
        login_data = {
            'email': 'user1@mail.com',
            'password': 'user1password',
        }
        serializer = LoginSerializer(data=login_data)
        self.assertTrue(serializer.is_valid())

        incorrect_data_list = [
            {
                'another_field': 'example',
                'email': 'user1@mail.com',
            },
            {
                'another_field': 'example',
                'password': 'user1password',
            },
            {
                'email': 'user2@mail.com',
                'password': 'user1password',
            },
            {
                'email': 'user1@mail.com',
                'password': 'user2password',
            },
        ]
        for incorrect_data in incorrect_data_list:
            serializer = LoginSerializer(data=incorrect_data)
            self.assertFalse(serializer.is_valid())

        inactive_user_login_data = {
            'email': 'user2@mail.com',
            'password': 'user2password',
        }
        serializer = LoginSerializer(data=inactive_user_login_data)
        self.assertFalse(serializer.is_valid())


class UserSerializerTests(APITestCase):
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

    def setUp(self):
        self.user = UserProfile.objects.get(email='user1@mail.com')

    # Оказывается поле с токеном не выводится, хоть и он указан в сериализаторе
    # def test_explicit_fields(self):
    #     serializer = UserSerializer(self.user)
    #     print(repr(serializer))
    #     self.assertTrue(serializer.fields['token'].read_only)
    #     self.assertTrue(serializer.fields['password'].write_only)

    def test_update(self):
        new_data = {
            'role': 'Admin',
            'email': 'user1@mail.ru',
            'password': 'user1anotherpassword',
            'name': 'another name1',
            'surname': 'another surname2',
            # Вообще наверное это поле должно быть read_only
        }
        serializer = UserSerializer(self.user, data=new_data, partial=True)
        self.assertTrue(serializer.is_valid())

        another_new_data = {
            'role': 'Patient',
            'email': 'user1@mail.com',
            'password': 'user1password',
            'name': 'name1',
            'surname': 'surname1',
            'patronymic': 'patronymic1',
            'phone_number': '+79998887765',
        }
        serializer = UserSerializer(self.user, data=another_new_data)
        self.assertTrue(serializer.is_valid())


class MedPeronaSerializerTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        UserProfile.objects.create_user(
            email='user1@mail.com',
            name='name1',
            surname='surname1',
            patronymic='patronymic1',
            phone_number='+79998887766',
            role='Doctor',
            password='user1password',
        )

        UserProfile.objects.create_user(
            email='user2@mail.com',
            name='name2',
            surname='surname2',
            patronymic='patronymic2',
            phone_number='+79998887744',
            role='Doctor',
            password='user2password',
        )

    def setUp(self):
        self.user = UserProfile.objects.get(email='user1@mail.com')

        user2 = UserProfile.objects.get(email='user2@mail.com')
        self.medpersona = MedPersona.objects.create(
            user=user2,
            birth_date='2001-08-03',
            position='Specialist',
            qualification='3',
            experience='5 years',
            location=200,
            specilization='Second Doctors Specialization',
            education='Second Doctors education',
        )

    def test_creation(self):
        data = {
            'user': self.user.id,
            'birth_date': '2001-07-04',
            'position': 'Specialist',
            'qualification': '3',
            'experience': '3 years',
            'location': 404,
            'specilization': 'Doctors Specialization',
            'education': 'Doctors education',
        }

        serializer = MedPeronaSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_update(self):
        new_data = {
            # при не частичном обновлении данных (partial=False), 
            # нужно указывать user, то есть можно вот эти данные 
            # медперсоны перемещать между разными пользователями
            'birth_date': '2000-07-03',
            'position': 'Doctor',
            'qualification': '1',
            'experience': '1 year',
            'location': 777,
            'specilization': 'Doctors another Specialization',
            'education': 'Doctors another education',
        }
        serializer = MedPeronaSerializer(self.medpersona, data=new_data, partial=True)
        self.assertTrue(serializer.is_valid())


class PatientSerializerTests(APITestCase):
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

        UserProfile.objects.create_user(
            email='user2@mail.com',
            name='name2',
            surname='surname2',
            patronymic='patronymic2',
            phone_number='+79998887744',
            role='Patient',
            password='user2password',
        )

    def setUp(self):
        self.user = UserProfile.objects.get(email='user1@mail.com')

        user2 = UserProfile.objects.get(email='user2@mail.com')
        self.patient = Patient.objects.create(
            user=user2,
            birth_date='1999-04-03',
            gender='Male',
            region='Second Patients Region',
            city='Second Patients City',
            receipt_date='2021-09-01T10:00:00Z',
            type='Vacationer',
            group='Second Patients Group',
            complaints='Seconds Patients complaints',
        )

    def test_creation(self):
        data = {
            'user': self.user.id,
            'birth_date': '1998-01-01',
            'gender': 'Male',
            'region': 'Patients Region',
            'city': 'Patients City',
            'receipt_date': '2021-09-01T10:00:00Z',
            'type': 'Vacationer',
            'group': 'Patients Group',
            'complaints': 'Patients complaints',
        }

        serializer = PatientSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_update(self):
        new_data = {
            'birth_date': '1998-01-05',
            'gender': 'Female',
            'region': 'Patients another Region',
            'city': 'Patients another City',
            'receipt_date': '2021-09-10T10:00:00Z',
            'type': 'Treating',
            'group': 'Patients another Group',
            'complaints': 'Patients more complaints',
        }
        serializer = PatientSerializer(self.patient, data=new_data, partial=True)
        self.assertTrue(serializer.is_valid())


class AdminSerializerTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        UserProfile.objects.create_user(
            email='user1@mail.com',
            name='name1',
            surname='surname1',
            patronymic='patronymic1',
            phone_number='+79998887766',
            role='Admin',
            password='user1password',
        )

        UserProfile.objects.create_user(
            email='user2@mail.com',
            name='name2',
            surname='surname2',
            patronymic='patronymic2',
            phone_number='+79998887744',
            role='Admin',
            password='user2password',
        )

    def setUp(self):
        self.user = UserProfile.objects.get(email='user1@mail.com')

        user2 = UserProfile.objects.get(email='user2@mail.com')
        self.admin = Admin.objects.create(
            user=user2,
            position='Second Admins Position',
        )

    def test_creation(self):
        data = {
            'user': self.user.id,
            'position': 'Admins Position',
        }

        serializer = AdminSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_update(self):
        new_data = {
            'position': 'Admins another Position',
        }
        serializer = AdminSerializer(self.admin, data=new_data, partial=True)
        self.assertTrue(serializer.is_valid())


class PassportDataSerializerTests(APITestCase):
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

    def setUp(self):
        self.user = UserProfile.objects.get(email='user1@mail.com')

    def test_creation(self):
        data = {
            'user': self.user.id,
            'series_number': '2020202020',
            'code': '123-321',
            'date': '1999-04-03',
            'by_whom': 'Suspicious organization',
        }

        serializer = PassportDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())


# SanatoriumSerializer