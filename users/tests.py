import json

from django.urls import reverse

from core.tests_utils import IAPITestCase


class UserAppIntegrationTest(IAPITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print('\n  -------------- Integracyjne testy panelu użytkownika -------------- \n ')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.basic_data = {'password': 'testPassword',
                          'firstName': 'FooBar',
                          'lastName': 'BarrFoo'}

    def test_register_endpoint_proper_data(self):
        data = {
            'email': 'testEmail@email.com',
            **self.basic_data
        }
        response = self.client.post(reverse('user-register'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content),
                         {'id': 7, 'email': 'testEmail@email.com', 'firstName': 'FooBar', 'lastName': 'BarrFoo',
                          'image': '/media/default-profile.gif', 'role': 0, 'active': False})

    def test_register_endpoint_invalid_data(self):
        data = {
            'email': 'wrong_email',
            **self.basic_data
        }
        response = self.client.post(reverse('user-register'), data=data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(json.loads(response.content), {'email': ['Podaj poprawny adres e-mail.']})

    def test_update_profile_valid_data(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.put(reverse('user-update'), data={**self.basic_data, 'id': self.test_user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content),
                         {'id': 1, 'email': 'foo@foo.foo', 'firstName': 'FooBar', 'lastName': 'BarrFoo',
                          'image': '/media/default-profile.gif', 'role': 0, 'active': True})

    def test_update_profile_invalid_data(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.put(reverse('user-update'), data={**self.basic_data, 'id': self.test_user.id, 'email': ''})
        self.assertEqual(response.status_code, 406)
        self.assertEqual(json.loads(response.content), {'email': ['To pole nie może być puste.']})

    def test_update_profile_unauthorized(self):
        response = self.client.put(reverse('user-update'), data={**self.basic_data,  'id': self.test_user.id, 'email': ''})
        self.assertEqual(response.status_code, 401)

    def test_accept_user(self):
        self.client.force_authenticate(self.test_admin)
        response = self.client.put(reverse('user-manage_user'), data={'user_id': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Pomyślnie aktywowano użytkownika'})
        response = self.client.put(reverse('user-manage_user'), data={'user_id': '99'})
        self.assertEqual(response.status_code, 404)
        self.client.force_authenticate(self.test_user)
        response = self.client.put(reverse('user-manage_user'), data={'user_id': '2'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {'detail': 'Musisz być administratorem'})
