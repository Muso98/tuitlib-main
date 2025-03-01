from django.urls import path
from .views import main, category, book, search
from lib.views_ import library_list, map_view
from . import views_
from .views.api_integration import searching_dissertations

urlpatterns = [
    path('', main.index, name='main'),
    path('category/<int:category_id>/', category.category_detail, name='category'),
    path('book/<int:book_id>/', book.book_detail, name='book'),
    path('book/<uuid:book_id>/', book.book_detail, name='book_uuid'),  # ✅ UUID versiyasi
    path('search/', search.SearchView.as_view(), name='search'),
    # path('sendvoice/', views_.send_voice, name='sendvoice'),
    path('voice-search/<str:query>/', views_.voice_search_view, name='search_voice'),
    # path('voice/', views_.voice_search, name='voice'),
    path('search-voice/', views_.voice_search, name='voice-search'),
    path('recog/', views_.get_recognized_text, name='recog'),
    path('api/libraries/', library_list, name='library-list'),
    path('map/', map_view, name='map'),
    path('categories/', category.category_list_api, name='category_list'),
    path("searching/", searching_dissertations, name="searching_dissertations"),

]
