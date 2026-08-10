from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationSecurityTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')

        self.notif1 = Notification.objects.create(
            user=self.user1,
            title='Test Title 1',
            message='Message 1',
            notification_type=Notification.NotificationType.SYSTEM
        )
        self.notif2 = Notification.objects.create(
            user=self.user2,
            title='Test Title 2',
            message='Message 2',
            notification_type=Notification.NotificationType.SYSTEM
        )

    def test_anonymous_cannot_access_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_notifications(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.notif1.id)

    def test_user_cannot_access_other_user_notification(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/notifications/{self.notif2.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_as_read(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/notifications/{self.notif1.id}/mark-as-read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)

    def test_mark_all_read(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/notifications/mark-all-read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)

