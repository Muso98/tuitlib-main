from django.shortcuts import render, get_object_or_404
from lib.models import Book, Category
import requests
import uuid

API_URL = "https://diss.natlib.uz/api/query"


def fetch_book_from_api(book_uuid):
    """API orqali kitobni UUID bo‘yicha qidirish"""
    try:
        response = requests.post(API_URL, json={"query": book_uuid}, timeout=10)
        if response.status_code == 200:
            books = response.json()
            if isinstance(books, dict) and "results" in books:
                books = books["results"]
            if isinstance(books, list) and books:
                book = books[0]
                return {
                    "id": book.get("uuid", ""),
                    "name": book.get("Title", "Noma'lum"),
                    "author": book.get("Author", "Noma'lum"),
                    "published_year": book.get("Year", "Noma'lum"),
                    "resource_type": book.get("turi", "Noma'lum"),
                    "code": book.get("Code", ""),
                    "collective_name": book.get("CollectiveName", ""),
                    "razdel": book.get("razdel", ""),
                    "language_code": book.get("LanguageCode", ""),
                    "other_title_info": book.get("OtherTitleInformation", ""),
                    "sahifalar": book.get("sahifalar", "Noma'lum"),
                    "level": book.get("level", ""),
                    "reads": book.get("reads", 0),
                    "downloads": book.get("downloads") if book.get(
                        "downloads") is not None else "Yuklab olish mavjud emas",
                    "filename": book.get("filename", ""),
                }
    except requests.RequestException:
        return None
    return None


def book_detail(request, book_id):
    """Mahalliy yoki API dagi kitob ma'lumotlarini chiqarish"""
    categories = Category.objects.all().order_by('id')
    book = None
    similar_books = []

    # **1️⃣ Mahalliy bazada qidirish (agar ID integer bo‘lsa)**
    try:
        if isinstance(book_id, int) or (isinstance(book_id, str) and book_id.isdigit()):
            book = get_object_or_404(Book, id=int(book_id))
            similar_books = book.similar_books()
    except (ValueError, Book.DoesNotExist):
        book = None

    # **2️⃣ API orqali qidirish (agar UUID bo‘lsa)**
    if book is None:
        try:
            if isinstance(book_id, uuid.UUID):
                book_uuid = str(book_id)
            else:
                book_uuid = str(uuid.UUID(book_id, version=4))

            print(f"📡 API orqali qidirilmoqda: {book_uuid}")
            book = fetch_book_from_api(book_uuid)

            # ✅ Agar kategoriya mavjud bo‘lsa, o‘xshash kitoblarni chiqarish
            if book and book.get("razdel"):
                similar_books = list(Book.objects.filter(category__id=book["razdel"])[:5])
        except (ValueError, AttributeError):
            print("❌ Noto‘g‘ri UUID format!")
            return render(request, '404.html', {"query": book_id})

    # **3️⃣ Agar hech narsa topilmasa, 404 sahifasi**
    if not book:
        return render(request, '404.html', {"query": book_id})

    return render(request, 'blok.html', {
        'book': book,
        'categories': categories,
        'similar_books': similar_books,
    })


def search_books(request):
    query = request.GET.get('q', '')
    source = request.GET.get('source', 'local') # Манбани аниқлаш

    combined_books = []

    if source == 'local':
        # Маҳаллий базадан маълумот олиш
        local_books = Book.objects.filter(title__icontains=query) # Мисол учун
        combined_books.extend(local_books)
    elif source == 'api':
        # API дан маълумот олиш
        api_books = fetch_book_from_api(query) # Мисол учун
        if api_books:
            combined_books.extend(api_books)

    paginator = Paginator(combined_books, 10) # 10 тадан саҳифага бўлиш
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    return render(request, 'search_results.html', {'books': books, 'query': query, 'source': source})