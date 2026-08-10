from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from projects.models import Project
from tasks.models import Task
from comments.models import Comment

User = get_user_model()


class CommentSecurityTestCase(APITestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            username='mgr', password='Password123!', role='manager'
        )
        self.employee1 = User.objects.create_user(
            username='emp1', password='Password123!', role='employee'
        )
        self.employee2 = User.objects.create_user(
            username='emp2', password='Password123!', role='employee'
        )
        self.project = Project.objects.create(
            title='Test Project', manager=self.manager
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Desc',
            project=self.project,
            creator=self.manager,
            assignee=self.employee1,
            deadline='2026-12-31T23:59:59Z'
        )

    def test_authenticated_user_can_create_comment(self):
        self.client.force_authenticate(user=self.employee1)
        response = self.client.post('/api/comments/', {
            'task': self.task.id,
            'content': 'Test comment by employee1'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author_username'], 'emp1')

    def test_anonymous_cannot_create_comment(self):
        response = self.client.post('/api/comments/', {
            'task': self.task.id,
            'content': 'Anon comment'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unrelated_employee_cannot_see_comment(self):
        comment = Comment.objects.create(
            task=self.task, author=self.employee1, content='Private comment'
        )
        self.client.force_authenticate(user=self.employee2)
        response = self.client.get(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_content_rejected(self):
        self.client.force_authenticate(user=self.employee1)
        response = self.client.post('/api/comments/', {
            'task': self.task.id,
            'content': '   '
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

