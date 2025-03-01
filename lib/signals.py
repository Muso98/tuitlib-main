from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book
from users.tasks import get_users_list


@receiver(post_save, sender=Book)
def book_created_handler(sender, instance, created, **kwargs):
    if created:
        print("Book creation handled")
        get_users_list.delay(instance.id)
