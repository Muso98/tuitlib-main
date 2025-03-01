from django.shortcuts import render
from lib.models import Book, Category


def index(request):
    categories = Category.objects.all().order_by('id')
    data = dict()
    for category in categories:
        books = Book.objects.filter(category=category).order_by('-id')[:8]
        data[category.name_uz] = books
    return render(request, 'index.html',
                  {
                      'categories': categories,
                      **data
                  })
