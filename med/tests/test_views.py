from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.http import HttpRequest
from med.views import *


class RegistrationAPIViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('registration')

    def test_post(self):
        data = {
            'user': {
                'email': 'user1@mail.com',
                'phone_number': '+79998887766',
                'role': 'Patient',
                'name': 'name1',
                'surname': 'surname1',
                'patronymic': 'patronymic1',
                'password': 'user1password',
                'photo': None,
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # Убеждаемся, что запись в БД появилась
        try:
            user = UserProfile.objects.get(email='user1@mail.com')
        except:
            self.assertFalse(True)

        incorrect_data_list = [
            {
                'user': {
                    'email': 'user2@mail.com',
                    'phone_number': '+79998887766',
                    'role': 'Not a role',
                    'name': 'name2',
                    'surname': 'surname2',
                    'password': 'user2password',
                    'photo': None,
                }
            },
            {
                'user': {
                    'email': 'user1@mail.com',
                    'phone_number': '+79998887766',
                    'role': 'Patient',
                    'name': 'name2',
                    'surname': 'surname2',
                    'password': 'user1anotherpassword',
                    'photo': None,
                }
            }
        ]
        for incorrect_data in incorrect_data_list:
            response = self.client.post(self.url, incorrect_data, format='json')
            self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPIViewTests(APITestCase):
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
            phone_number='+79998887755',
            role='Doctor',
            password='user2password',
        )
        UserProfile.objects.create_user(
            email='user3@mail.com',
            name='name3',
            surname='surname3',
            patronymic='patronymic3',
            phone_number='+79998887744',
            role='Admin',
            password='user3password',
        )

    def setUp(self):
        self.url = reverse('login')

    def test_response_fields(self):
        data = {
            'user': {
                'email': 'user1@mail.com',
                'password': 'user1password',
            }
        }
        response = self.client.post(self.url, data, format='json')

        expected_response_fields = ['token', 'role', ] # 'email'
        for field in expected_response_fields:
            self.assertTrue(field in response.data)

    def test_post(self):
        correct_data_list = [
            {
                'user': {
                    'email': 'user1@mail.com',
                    'password': 'user1password',
                },
            },
            {
                'user': {
                    'email': 'user2@mail.com',
                    'password': 'user2password',
                },
            },
            {
                'user': {
                    'email': 'user3@mail.com',
                    'password': 'user3password',
                },
            },
        ]

        for correct_data in correct_data_list:
            response = self.client.post(self.url, correct_data, format='json')
            self.assertEquals(response.status_code, status.HTTP_200_OK)

        incorrect_data_list = [
            {
                'user': {
                    'email': 'user1@mail.com',
                },
            },
            {
                'user': {
                    'email': 'user2@mail.com',
                    'password': 'user1password',
                },
            },
            {
                'user': {
                },
            },
        ]

        for incorrect_data in incorrect_data_list:
            response = self.client.post(self.url, incorrect_data, format='json')
            self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateAPIViewTests(APITestCase):
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
        self.url = reverse('user')

        user = UserProfile.objects.get(email='user1@mail.com')
        self.client.force_authenticate(user=user)

    def test_retrieve(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        new_data = {
            'user': {
                'name': 'new name1',
                'surname': 'new surname1',
                'phone_number': '+79998887765',
                'role': 'Doctor',
            }
        }
        response = self.client.patch(self.url, new_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Данные должны поменяться
        user = UserProfile.objects.get(email='user1@mail.com')
        self.assertEquals(user.role, 'Doctor')
        self.assertEquals(user.name, 'new name1')
        self.assertEquals(user.surname, 'new surname1')
        self.assertEquals(user.phone_number, '+79998887765')

        incorrect_data = {
            'user': {
                'role': 'Not a role',
            }
        }
        response = self.client.patch(self.url, incorrect_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Данные НЕ должны поменяться
        user = UserProfile.objects.get(email='user1@mail.com')
        self.assertEquals(user.role, 'Doctor')

    def test_permission(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        new_data = {
            'user': {
                'name': 'new name1',
                'surname': 'new surname1',
                'phone_number': '+79998887765',
                'role': 'Doctor',
            }
        }
        response = self.client.patch(self.url, new_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)


class MedPersonaAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Медперсона
        user_medpersona = UserProfile.objects.create_user(
            email='user1@mail.com',
            name='name1',
            surname='surname1',
            patronymic='patronymic1',
            phone_number='+79998887766',
            role='Doctor',
            password='user1password',
        )
        # Пациент
        UserProfile.objects.create_user(
            email='user2@mail.com',
            name='name2',
            surname='surname2',
            patronymic='patronymic2',
            phone_number='+79998887755',
            role='Patient',
            password='user2password',
        )
        # Администратор
        UserProfile.objects.create_user(
            email='user3@mail.com',
            name='name3',
            surname='surname3',
            patronymic='patronymic3',
            phone_number='+79998887744',
            role='Admin',
            password='user3password',
        )
        # Медперсона без своей записи в MedPersona
        UserProfile.objects.create_user(
            email='user4@mail.com',
            name='name4',
            surname='surname4',
            patronymic='patronymic4',
            phone_number='+79998887733',
            role='Doctor',
            password='user4password',
        )
        MedPersona.objects.create(
            user=user_medpersona,
            birth_date='2001-08-03',
            position='Specialist',
            qualification='3',
            experience='5 years',
            location=200,
            specilization='Second Doctors Specialization',
            education='Second Doctors education',
        )

    def setUp(self):
        self.url = reverse('medpersona')
        self.user_medpersona = UserProfile.objects.get(email='user1@mail.com')
        self.user_patient = UserProfile.objects.get(email='user2@mail.com')
        self.user_admin = UserProfile.objects.get(email='user3@mail.com')
        self.user_medpersona2 = UserProfile.objects.get(email='user4@mail.com')
        self.client.force_authenticate(user=self.user_medpersona)

    def test_post(self):
        data = {
            'medpersona': {
                'birth_date': '2012-12-12',
                'position': 'Doctor',
                'qualification': '0',
                'experience': '0 years',
                'location': 101,
            }
        }

        self.client.force_authenticate(user=self.user_medpersona)
        response = self.client.post(self.url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.force_authenticate(user=self.user_medpersona2)
        response = self.client.post(self.url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        try:
            MedPersona.objects.get(user__email=self.user_medpersona2)
        except:
            self.assertFalse(True)

    def test_patch(self):
        min_data = {
            'medpersona': {
                'birth_date': '2011-11-11',
            }
        }
        response = self.client.patch(self.url, min_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.user_medpersona2)
        response = self.client.patch(self.url, min_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_permissions(self):
        # GET
        def check_get_status(user_list, expected_status):
            for user in user_list:
                self.client.force_authenticate(user=user)
                response = self.client.get(self.url)
                self.assertEquals(response.status_code, expected_status)

        ok_list = [self.user_medpersona]
        check_get_status(ok_list, status.HTTP_200_OK)

        not_found_list = [self.user_patient, self.user_admin, self.user_medpersona2]
        check_get_status(not_found_list, status.HTTP_404_NOT_FOUND)

        forbidden_list = [None]
        check_get_status(forbidden_list, status.HTTP_403_FORBIDDEN)

        # PATCH
        def check_patch_status(user_list, data, expected_status):
            for user in user_list:
                self.client.force_authenticate(user=user)
                response = self.client.patch(self.url, data, format='json')
                self.assertEquals(response.status_code, expected_status)

        min_data = {
            'medpersona': {
                'birth_date': '2011-11-11',
            }
        }

        check_patch_status(ok_list, min_data, status.HTTP_200_OK)
        check_patch_status(not_found_list, min_data, status.HTTP_404_NOT_FOUND)
        check_patch_status(forbidden_list, min_data, status.HTTP_403_FORBIDDEN)

        # POST
        def check_post_status(user_list, data, expected_status):
            for user in user_list:
                self.client.force_authenticate(user=user)
                response = self.client.post(self.url, data, format='json')
                self.assertEquals(response.status_code, expected_status)

        min_data = {
            'medpersona': {
                'birth_date': '2012-12-12',
                'position': 'Doctor',
                'qualification': '0',
                'experience': '0 years',
                'location': 101,
            }
        }

        check_post_status(forbidden_list, min_data, status.HTTP_403_FORBIDDEN)
        check_post_status(ok_list, min_data, status.HTTP_400_BAD_REQUEST)
        check_post_status(not_found_list, min_data, status.HTTP_201_CREATED)

# PatientAPIView
# AdminAPIView

# PassportDataAPIView
# SanatoriumView
# SingleSanatoriumView
