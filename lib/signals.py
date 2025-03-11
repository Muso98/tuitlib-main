from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, SearchQuery, Notification
from users.tasks import get_users_list
from django.contrib.auth import get_user_model

User = get_user_model()  # Django foydalanuvchi modelini olish


@receiver(post_save, sender=Book)
def book_created_handler(sender, instance, created, **kwargs):
    if created:
        print("Book creation handled")
        get_users_list.delay(instance.id)



@receiver(post_save, sender=Book)
def create_notification(sender, instance, created, **kwargs):
    if created:  # Faqat yangi kitoblar uchun
        search_queries = SearchQuery.objects.filter(title__icontains=instance.author)

        for query in search_queries:
            Notification.objects.create(
                user=query.user,
                message=f"📚 Siz qidirgan '{query.title}' haqida yangi kitob qo‘shildi: {instance.name}"
            )
            query.delete()

@receiver(post_save, sender=Book)
def notify_users_on_new_book(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()  # Barcha foydalanuvchilarga yuborish
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"Yangi kitob qo‘shildi: {instance.name} - {instance.author}",
                book=instance
            )