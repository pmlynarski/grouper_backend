import json

from django.urls import reverse

from core.utils import IAPITestCase


class GroupAppIntegrationTests(IAPITestCase):
    counter = 1
    base_data = {}
    return_data = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print('\n  -------------- Integracyjne testy panelu grup -------------- \n ')

    @classmethod
    def setUpClassData(cls):
        super().setUpTestData()
        cls.base_data = {
            'name': 'TestName'
        }

    def test_searching_for_groups(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.get(reverse('group-search'), data={'phrase': 'Test'})
        self.assertEqual(len(json.loads(response.content)['results']), 1)
        self.assertEqual(response.status_code, 200)

    def test_searching_for_groups_wrong_data(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.get(reverse('group-search'))
        self.assertEqual(response.status_code, 406)

    def test_create_group_admin(self):
        proper_data = {
            'id': 2, 'name': '',
            'owner': {'id': 4, 'email': 'admin@admin.admin', 'first_name': 'Admin', 'last_name': 'Tester',
                      'is_admin': True, 'is_lecturer': False}, 'members': []}
        self.client.force_authenticate(self.test_admin)
        response = self.client.post(reverse('group-create_group'), data=self.base_data)
        self.assertEqual(json.loads(response.content), proper_data)
        self.assertEqual(response.status_code, 200)

    def test_create_group_lecturer(self):
        proper_data = {'id': 2, 'name': '',
                       'owner': {'id': 3, 'email': 'foo@lecturer.bar', 'first_name': 'Lecturer', 'last_name': 'Tester',
                                 'is_admin': False, 'is_lecturer': True}, 'members': []}

        self.client.force_authenticate(self.test_lecturer)
        response = self.client.post(reverse('group-create_group'), data=self.base_data)
        self.assertEqual(json.loads(response.content), proper_data)
        self.assertEqual(response.status_code, 200)

    def test_create_group_casual(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.post(reverse('group-create_group'), data=self.base_data)
        self.assertEqual(response.status_code, 403)

    def test_details_authenticated(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.get(reverse('group-get_group', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_details_unauthorized(self):
        response = self.client.get(reverse('group-get_group', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 401)

    def test_update_group_admin(self):
        self.client.force_authenticate(self.test_admin)
        response = self.client.put(reverse('group-update_group', kwargs={'id': 1}), data={'name': 'Updated name'})
        self.assertEqual(json.loads(response.content),
                         {'detail': 'Musisz być właścicielem lub moderatorem grupy by wykonać tą akcję'})
        self.assertEqual(response.status_code, 403)

    def test_update_group_owner(self):
        self.client.force_authenticate(self.test_moderator)
        response = self.client.put(reverse('group-update_group', kwargs={'id': 1}), data={'name': 'Updated name'})
        self.assertEqual(json.loads(response.content)['message'], 'Pomyślnie zaktualizowano grupę')
        self.assertEqual(response.status_code, 200)

    def test_delete_group_owner(self):
        self.client.force_authenticate(self.test_lecturer)
        response = self.client.delete(reverse('group-delete_group', kwargs={'id': 1}))
        self.assertEqual(json.loads(response.content)['message'], 'Pomyślnie usunięto grupę')
        self.assertEqual(response.status_code, 200)

    def test_delete_group_moderator(self):
        self.client.force_authenticate(self.test_moderator)
        response = self.client.delete(reverse('group-delete_group', kwargs={'id': 1}))
        self.assertEqual(json.loads(response.content)['detail'],
                         'Musisz być administratorem lub właścicielem by wykonać tą akcję')
        self.assertEqual(response.status_code, 403)

    def test_delete_group_casual(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.delete(reverse('group-delete_group', kwargs={'id': 1}))
        self.assertEqual(json.loads(response.content)['detail'],
                         'Musisz być administratorem lub właścicielem by wykonać tą akcję')
        self.assertEqual(response.status_code, 403)

    def test_leave_group(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.post(reverse('group-leave_group', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Pomyślnie opuściłeś grupę'})

    def test_drop_user_from_group_owner(self):
        self.client.force_authenticate(self.test_lecturer)
        response = self.client.post(reverse('group-drop_member', kwargs={'id': self.test_group.id}),
                                    data={'id': self.test_user.id})
        self.assertEqual(json.loads(response.content), {'message': 'Pomyślnie usunięto użytkownika z grupy'})
        self.assertEqual(response.status_code, 200)

    def test_drop_user_from_group_casual(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.post(reverse('group-drop_member', kwargs={'id': self.test_group.id}),
                                    data={'id': self.test_user.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content),
                         {'detail': 'Musisz być właścicielem lub moderatorem grupy by wykonać tą akcję'})

    def test_join_group_member(self):
        self.client.force_authenticate(self.test_lecturer)
        response = self.client.post(reverse('group-join_group', kwargs={'id': self.test_group.id}))
        self.assertEqual(response.status_code, 406)
        self.assertEqual(json.loads(response.content), {'message': 'Jesteś już członkiem tej grupy'})

    def test_join_group_casual(self):
        self.test_inactive_user.active = True
        self.test_inactive_user.save()
        self.client.force_authenticate(self.test_inactive_user)
        response = self.client.post(reverse('group-join_group', kwargs={'id': self.test_group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['message'], 'Pomyślnie zapisano się na listę oczekujących')

    def test_manage_pending_user_moderator_accept(self):
        self.client.force_authenticate(self.test_moderator)
        response = self.client.post(reverse('group-manage_pending_member', kwargs={'id': self.test_group.id}),
                                    data={'id': self.test_pending_user.id})
        self.assertEqual(json.loads(response.content), {'message': 'Pomyślnie zaakceptowano użytkownika'})
        self.assertEqual(response.status_code, 200)

    def test_manage_pending_user_casual_accept(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.post(reverse('group-manage_pending_member', kwargs={'id': self.test_group.id}),
                                    data={'id': self.test_pending_user.id})
        self.assertEqual(response.status_code, 403)

    def test_manage_pending_user_moderator_decline(self):
        self.client.force_authenticate(self.test_lecturer)
        response = self.client.delete(reverse('group-manage_pending_member', kwargs={'id': self.test_group.id}),
                                      data={'id': self.test_pending_user.id})
        self.assertEqual(json.loads(response.content), {'message': 'Pomyślnie odrzucono użytkownika'})
        self.assertEqual(response.status_code, 200)

    def test_manage_pending_user_casual_decline(self):
        self.client.force_authenticate(self.test_user)
        response = self.client.delete(reverse('group-manage_pending_member', kwargs={'id': self.test_group.id}),
                                      data={'id': self.test_pending_user.id})
        self.assertEqual(response.status_code, 403)
