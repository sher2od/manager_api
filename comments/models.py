from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from tasks.models import Task


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['task', '-created_at']),
        ]

    def clean(self):
        super().clean()
        if self.content and not self.content.strip():
            raise ValidationError({'content': "Izoh matni faqat bo'sh joylardan iborat bo'lishi mumkin emas."})

    def __str__(self):
        return f"Comment by {self.author.username} on task #{self.task_id}"








