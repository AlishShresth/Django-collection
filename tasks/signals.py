from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Task, TaskHistory
from django.contrib.auth import get_user_model


User = get_user_model()


@receiver(pre_save, sender=Task)
def track_task_changes(sender, instance, **kwargs):
    """Log changes to task fields."""
    if instance.id:  # Only track updates, not creations
        old_instance = Task.objects.get(id=instance.id)
        fields_to_track = [
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "deadline",
            "estimated_hours",
            "actual_hours",
            "sprint",
            "story_points",
        ]
        for field in fields_to_track:
            old_value = str(getattr(old_instance, field, None))
            new_value = str(getattr(instance, field, None))
            if old_value != new_value:
                TaskHistory.objects.create(
                    task=instance,
                    user=(
                        instance._request_user
                        if hasattr(instance, "_request_user")
                        else None
                    ),
                    field=field,
                    old_value=old_value,
                    new_value=new_value,
                )
