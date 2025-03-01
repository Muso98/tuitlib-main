from django.db.models import F
from django.shortcuts import render, get_object_or_404
from lib.models import Category, Book
from ..pagination import DefaultPaginator
from django.http.response import JsonResponse


def category_detail(request, category_id):
    categories = Category.objects.all().order_by('id')
    category = get_object_or_404(Category, id=category_id)
    books = Book.objects.filter(category_id=category_id).order_by('-id')
    most_downloaded_books = books.annotate(total_downloads=F('download_count')).order_by('-total_downloads')[:6]
    default_paginator = DefaultPaginator(request, books)
    return render(request, 'category_detail.html',
                  {
                      'categories': categories,
                      'category': category,
                      'books': default_paginator.get_paginated_response(),
                      'downloads': most_downloaded_books,
                  })


def category_list_api(request):
    category_list = []
    categories = Category.objects.all()
    for category in categories:
        category_list.append({
            "id": category.id,
            "name": category.name,
        })

    return JsonResponse(category_list, safe=False)
