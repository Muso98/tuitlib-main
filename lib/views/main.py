from django.shortcuts import render
from lib.models import Book, Category, Notification


def index(request):
    categories = Category.objects.all().order_by('id')
    data = dict()

    for category in categories:
        books = Book.objects.filter(category=category).order_by('-id')[:8]
        data[category.name_uz] = books

    # Foydalanuvchi tizimga kirgan bo‘lsa, uning o‘qilmagan bildirishnomalari sonini hisoblaymiz
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'index.html', {
        'categories': categories,
        'unread_notifications_count': unread_notifications_count,
        **data
    })
