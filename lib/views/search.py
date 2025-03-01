import requests
import json
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from lib.models import Book, Category
from users.tasks import save_user_search_history
from django.core.serializers import serialize

API_URL = "https://diss.natlib.uz/api/query"

def book_filter_queryset(query):
    """Mahalliy bazadan qidirish"""
    return Book.objects.filter(
        Q(name__icontains=query) |
        Q(about__icontains=query) |
        Q(author__icontains=query) |
        Q(key_words__icontains=query)
    ).order_by('-id')


def fetch_api_results(query):
    """API orqali qidirish va JSON formatni tekshirish"""
    try:
        response = requests.post(API_URL, json={"query": query}, timeout=10)

        # ✅ JSON format ekanligini tekshiramiz
        try:
            response_json = response.json()
        except ValueError:
            print("❌ Xato: API JSON formatda emas!")
            return []

        # ✅ Agar API javobi `list` bo‘lsa, to‘g‘ridan-to‘g‘ri qaytariladi
        if isinstance(response_json, list):
            return response_json

        # ✅ Agar API javobi `dict` bo‘lsa, `results` kalitini olishga harakat qilamiz
        elif isinstance(response_json, dict):
            return response_json.get("results", [])

        else:
            print("❌ Xato: API noto‘g‘ri formatda javob berdi!")
            return []

    except requests.RequestException as e:
        print(f"❌ API so‘rovda xatolik: {e}")
        return []


class SearchView(View):
    def get(self, request):
        categories = Category.objects.all()
        query = self.request.GET.get('q', '').strip()

        if not query:
            return render(request, 'search.html', {"books": [], "query": "", "categories": categories})

        # ✅ Mahalliy bazadan qidirish
        local_results = list(book_filter_queryset(query))

        # ✅ API dan natijalar
        api_results = fetch_api_results(query)

        # ✅ API natijalarini `Book` modeliga o‘xshatib yaratamiz
        formatted_api_results = [
            {
                "id": result.get("uuid", "unknown"),
                "name": result.get("Title", "Noma’lum"),
                "author": result.get("Author", "Noma’lum"),
                "key_words": result.get("OtherTitleInformation", "Noma’lum"),
                "published_year": result.get("Year", "Noma’lum"),
            }
            for result in api_results
        ]

        # ✅ Mahalliy + API natijalarini birlashtirish
        combined_results = local_results + formatted_api_results

        # ✅ Sahifalash (Pagination)
        paginator = Paginator(combined_results, 12)  # Har sahifada 12 ta natija
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'books': page_obj,
            'query': query,
            'categories': categories
        }

        return render(request, 'search.html', context)
