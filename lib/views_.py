from urllib.parse import urlencode
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
import requests
import os
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import STTModel, Category, Library, Notification
from dotenv import load_dotenv
from .views.search import book_filter_queryset
from .pagination import DefaultPaginator
from pydub import AudioSegment
from django.conf import settings

load_dotenv(".env")

URL = os.getenv('URL')
USERNAME = os.getenv('STT_USERNAME')
PASSWORD = os.getenv('PASSWORD')


def get_token(url: str, username: str, password: str) -> dict:
    print(f"Requesting token from: {url}")  # Debugging uchun
    request = requests.post(
        url,
        data={
            'username': username,
            'password': password
        }
    )
    print(f"Response status code: {request.status_code}")  # Javob kodini ko‘rish uchun
    print(f"Response content: {request.text}")  # Serverdan nima qaytayotganini ko‘rish

    if request.status_code == 200:
        save_token(request.json())
        return request.json()


def save_token(token: dict) -> STTModel:
    access = token['access']
    refresh = token['refresh']

    obj = STTModel.objects.create(
        access=access,
        refresh=refresh
    )

    return obj


def refresh_token(url: str) -> dict:
    token = STTModel.objects.filter('-id').first()
    refresh = token.refresh
    request = requests.post(
        url,
        data={
            "refresh": refresh
        }
    )
    if request.status_code == 200:
        token.access = request.json()['access']
        token.save()
        return request.json()


def recognize_audio(audio):
    token = STTModel.objects.all().last()

    if token is None:
        url = f"{URL}token/"
        token = get_token(url, USERNAME, PASSWORD)
        headers = {'Authorization': f'JWT {token["access"]}'}
    else:
        headers = {'Authorization': f'JWT {token.access}'}
    r_url = f"{URL}recog/"

    r = requests.post(
        url=r_url,
        headers=headers,
        files={'audio': audio}
    )

    if r.status_code == 200:
        data = {"word": r.json()}
        return data

    elif r.status_code == 401:
        refresh_token(url=f"{URL}refresh/")

    elif r.status_code == 403:
        raise Http404("Access denied. Forbidden")
    return r


@csrf_exempt
def get_recognized_text(request):
    if request.method == "POST":
        audio = request.FILES["recorded_audio"]
        audio_segment = AudioSegment.from_file(audio)
        output_file = "record.wav"
        wav_file = audio_segment.export(output_file, format="wav")
        resp = recognize_audio(wav_file)
        query = urlencode({'q': resp['word']})
        url = reverse('search') + '?' + query
        return JsonResponse(
            {
                "url": url,
                "success": True,
            }
        )


def voice_search_view(request, query):

    categories = Category.objects.all()

    queryset = book_filter_queryset(query)

    paginator = DefaultPaginator(request, queryset, per_page=12)
    result = paginator.get_paginated_response()
    context = {
        'books': result,
        'query': query,
        'categories': categories
    }

    return render(request, 'search.html', context)


def voice_search(request):
    return render(request, 'voice_search.html')


def library_list(request):
    libraries = Library.objects.all()
    lib_list = []
    for library in libraries:
        # Check if the library has an associated image and generate the full URL
        if library.image:
            image_url = request.build_absolute_uri(library.image.url)
        else:
            image_url = None
        
        lib_list.append({
            "name": library.name,
            "latitude": str(library.latitude),
            "longitude": str(library.longitude),
            "image": image_url,
            "phone": library.phone_number
        })
    
    return JsonResponse(lib_list, safe=False)


def map_view(request):
    return render(request, 'map.html')

def user_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        data = [{"message": n.message, "created_at": n.created_at} for n in notifications]
        return JsonResponse({"notifications": data}, safe=False)
    return JsonResponse({"error": "❌ Foydalanuvchi autentifikatsiyadan o‘tmagan!"}, status=403)

@login_required
def notifications_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    """Bitta bildirishnomani o‘qilgan deb belgilash"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user, is_read=False)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True, 'notification_id': notification_id})


@login_required
def mark_all_notifications_as_read(request):
    """Barcha bildirishnomalarni o‘qilgan deb belgilash"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})
