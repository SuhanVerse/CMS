from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import CustomUser
from inventory.models import Inventory


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost'])
class AdminAccessControlTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username='student_user',
            password='testpass123',
            user_code='12345',
            role='student',
        )
        self.admin_user = CustomUser.objects.create_user(
            username='admin_user',
            password='testpass123',
            user_code='54321',
            role='admin',
            is_staff=True,
        )
        self.item = Inventory.objects.create(
            item_name='Tea',
            category='beverages',
            price='25.00',
            quantity=10,
        )

    def test_admin_page_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse('admin_page'))

        self.assertRedirects(response, '/login/?next=/admin_page/')

    def test_student_cannot_access_admin_page(self):
        self.client.login(username='student_user', password='testpass123')

        response = self.client.get(reverse('admin_page'))

        self.assertRedirects(response, '/menu/')

    def test_student_cannot_access_update_page(self):
        self.client.login(username='student_user', password='testpass123')

        response = self.client.get(reverse('admin_update_item', args=[self.item.id]))

        self.assertRedirects(response, '/menu/')

    def test_student_cannot_delete_item(self):
        self.client.login(username='student_user', password='testpass123')

        response = self.client.post(reverse('admin_delete_item', args=[self.item.id]))

        self.assertRedirects(response, '/menu/')
        self.assertTrue(Inventory.objects.filter(id=self.item.id).exists())

    def test_admin_can_access_admin_routes(self):
        self.client.login(username='admin_user', password='testpass123')

        dashboard_response = self.client.get(reverse('admin_page'))
        update_response = self.client.get(reverse('admin_update_item', args=[self.item.id]))

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)

    def test_admin_delete_requires_post(self):
        self.client.login(username='admin_user', password='testpass123')

        response = self.client.get(reverse('admin_delete_item', args=[self.item.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Inventory.objects.filter(id=self.item.id).exists())

    def test_admin_can_delete_item_with_post(self):
        self.client.login(username='admin_user', password='testpass123')

        response = self.client.post(reverse('admin_delete_item', args=[self.item.id]))

        self.assertRedirects(response, reverse('admin_page'))
        self.assertFalse(Inventory.objects.filter(id=self.item.id).exists())


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost'])
class RegistrationTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.existing_user = CustomUser.objects.create_user(
            username='existing_user',
            password='testpass123',
            user_code='11111',
            role='student',
        )

    def test_registration_rejects_duplicate_user_code(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'new_user',
                'password': 'testpass123',
                'user_code': '11111',
                'role': 'student',
            },
        )

        self.assertRedirects(response, self.register_url)
        self.assertEqual(CustomUser.objects.filter(username='new_user').count(), 0)

    def test_registration_rejects_invalid_role(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'fake_admin',
                'password': 'testpass123',
                'user_code': '22222',
                'role': 'admin',
            },
        )

        self.assertRedirects(response, self.register_url)
        self.assertFalse(CustomUser.objects.filter(username='fake_admin').exists())

    def test_registration_creates_non_admin_user(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'teacher_user',
                'password': 'testpass123',
                'user_code': '33333',
                'role': 'teacher',
            },
        )

        self.assertRedirects(response, reverse('login'))

        user = CustomUser.objects.get(username='teacher_user')
        self.assertEqual(user.role, 'teacher')
        self.assertFalse(user.is_staff)
