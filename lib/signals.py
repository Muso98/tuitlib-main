from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q  # ❗ Q obyektini import qilish
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
        print(f"📚 Yangi kitob qo‘shildi: {instance.name}")

        # 🔎 SearchQuery modelida 'title' maydoni bor, shuni ishlatamiz
        search_queries = SearchQuery.objects.filter(
            Q(title__icontains=instance.author) |
            Q(title__icontains=instance.name) |
            Q(title__icontains=instance.key_words)
        )

        if search_queries.exists():
            notifications = [
                Notification(
                    user=query.user,
                    message=f"📚 Siz qidirgan '{query.title}' haqida yangi kitob qo‘shildi: {instance.name}",
                    book=instance
                )
                for query in search_queries
            ]

            # ✅ Bildirishnomalarni optimallashtirib qo‘shish
            Notification.objects.bulk_create(notifications)

            # 🔄 So‘rov bajarilgani uchun uni o‘chirish
            search_queries.delete()