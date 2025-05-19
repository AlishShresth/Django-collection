from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task
from .models import Task


@shared_task
def send_task_assignment_email(task_id, user_email):
    """Send email when a task is assigned."""
    task = Task.objects.get(id=task_id)
    subject = f"New Task Assigned: {task.title}"
    message = f"You have been assigned to '{task.title}' in project ' {task.project.name}'.\n\nDescription: {task.description}\nDeadline: {task.deadline or 'Not set'}"
    send_mail(subject, message, "no-reply@taskmanager.com", [user_email])


@shared_task
def send_deadline_reminder_email(task_id, user_email):
    """Send deadline reminder 24 hours before due."""
    task = Task.objects.get(id=task_id)
    subject = f"Deadline Reminder: {task.title}"
    message = f"The task '{task.title}' is due in 24 hours.\n\nDescription: {task.description}\nProject: {task.project.name}"
    send_mail(subject, message, "no-reply@taskmanager.com", [user_email])


@shared_task
def check_deadline_reminders():
    """Check tasks due in 24 hours and send reminders."""
    now = timezone.now()
    due_soon = now + timedelta(hours=24)
    tasks = Task.objects.filter(
        deadline__range=(now, due_soon), assigned_to__isnull=False
    )
    for task in tasks:
        send_deadline_reminder_email.delay(task.id, task.assigned_to.email)
