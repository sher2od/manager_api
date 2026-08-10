from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from projects.models import Project


class Task(models.Model):
    # Vazifa holatlari
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'

    # Muhimlik darajalari
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True
    )

    deadline = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def clean(self):
        super().clean()
        # Mantiqiy tekshiruv: deadline o'tib ketgan vaqt bo'lishi mumkin emas (yangi yaratilayotganda)
        if self.pk is None and self.deadline and self.deadline < timezone.now():
            raise ValidationError({'deadline': "Vazifa muddati (deadline) o'tib ketgan vaqt bo'lishi mumkin emas."})

    def __str__(self):
        return f"{self.title} ({self.status})"