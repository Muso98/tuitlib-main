import string
import random
import base64
import os
import requests
from django.conf import settings
from users.aws_rekognition import register_face
from django.utils.translation import gettext_lazy as _
from users.forms import CustomUserCreationForm, EmailVerificationForm, \
    AccountAuthenticationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, reverse
from users.models import Downloads, Requests, FaceID, ResearchArea, SearchHistory, User
from lib.pagination import DefaultPaginator
from lib.models import Category, SearchQuery
from django.contrib import messages
from django.contrib.auth import (
    logout,
    login, authenticate,get_user_model
)
from django.core.exceptions import ObjectDoesNotExist
from users.models import EmailOTP
from users.tasks import verification_mail_sender
from dotenv import load_dotenv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
import json
from users.aws_rekognition import recognize_face, rekognition
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

User = get_user_model()
load_dotenv('.env')

URL = os.getenv('FACE_ID_URL')


def get_categories():
    return Category.objects.all().order_by('id')

def registration_view(request):
    research_areas = ResearchArea.objects.all()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Foydalanuvchini tasdiqlash uchun faol emas qilib qo‘yamiz
            user.save()

            # Foydalanuvchining tanlagan research area'larini bog‘lash
            research_area_ids = request.POST.getlist('research_area_ids')
            for area_id in research_area_ids:
                try:
                    research_area = ResearchArea.objects.get(id=area_id)
                    user.research_area.add(research_area)
                except ObjectDoesNotExist:
                    continue  # Agar noto‘g‘ri ID kiritilgan bo‘lsa, davom etamiz

            # Email orqali tasdiqlash xabari yuborish
            verification_mail_sender.apply_async(args=(user.email,))

            messages.success(request, "✅ Ro‘yxatdan o‘tish muvaffaqiyatli! Iltimos, email orqali tasdiqlang.")
            return redirect('/users/verify/')

        else:
            messages.error(request, "❌ Ro‘yxatdan o‘tishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.")

    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'research_areas': research_areas
    }

    return render(request, 'accounts/register.html', context)


def login_view(request):
    """
    Email va parol yoki Face ID orqali tizimga kirish
    """
    context = {}
    user = request.user

    if user.is_authenticated:
        return redirect("profile")  # ✅ Agar foydalanuvchi allaqachon tizimga kirgan bo‘lsa, profilga yo‘naltirish

    if request.method == "POST":
        form = AccountAuthenticationForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        use_face_id = request.POST.get("use_face_id", "").lower() in ["true", "1", "yes"]  # ✅ To‘g‘ri tekshirish
        next_url = request.POST.get("next") or request.GET.get("next") or reverse("profile")

        if use_face_id:
            # ✅ Foydalanuvchini Face ID sahifasiga yo‘naltiramiz (lekin tizimga kiritmaymiz)
            return redirect(f"{reverse('face_login')}?next={next_url}")

        else:
            # ✅ Oddiy email va parol orqali tizimga kirish
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Tizimga muvaffaqiyatli kirdingiz!")
                return redirect(next_url)

            else:
                messages.error(request, "Email yoki parol noto‘g‘ri!")

    else:
        form = AccountAuthenticationForm()

    context["login_form"] = form
    return render(request, "accounts/login.html", context)


def account_edit_view(request):
    pass


# def email_verify_view(request):
#     form = EmailVerificationForm()
#     if request.method == 'POST':
#         email = request.session.get('email')
#         form = EmailVerificationForm(request.POST)
#         if form.is_valid():
#             code = form.cleaned_data.get('otp_code')
#             try:
#                 email_otp = EmailOTP.objects.get(email=email, code=code)
#             except EmailOTP.DoesNotExist:
#                 form.add_error('otp_code', _("Code is wrong"))
#                 return render(request, 'accounts/email_verify.html', {'form': form})
#             if email_otp.code == code:
#                 user = get_object_or_404(User, email=email)
#                 if user:
#                     user.is_active = True
#                     user.save()
#                     email_otp.delete()
#                     login(request, user)
#                     return redirect('face_recog')
#                 else:
#                     form.add_error(None, _("User not found"))
#             else:
#                 form.add_error('otp_code', _("Code is wrong"))
#
#     return render(request, 'accounts/email_verify.html', {'form': form})

def email_verify_view(request):
    email = request.session.get('email')

    if not email:
        messages.error(request, "Email topilmadi, qayta ro‘yxatdan o‘ting!")
        return redirect("register")

    # Foydalanuvchini email orqali topamiz
    user = get_object_or_404(User, email=email)

    # ✅ Email avtomatik tasdiqlanadi
    user.is_active = True
    user.save()

    # ✅ Avtomatik tizimga kirish
    login(request, user)

    messages.success(request, "Email muvaffaqiyatli tasdiqlandi!")
    return redirect("profile")  # ✅ Profil sahifasiga yo‘naltirish

def generate_random_password(length=12):
    """ Tasodifiy kuchli parol yaratish """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def face_register_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email", "").strip()
            first_name = data.get("first_name", "").strip() or "NoName"
            last_name = data.get("last_name", "").strip() or "NoLastName"
            image_data = data.get("image", "")

            if not email or not image_data:
                return JsonResponse({"success": False, "message": "❌ Email yoki rasm topilmadi!"}, status=400)

            # ✅ Rasm formatini tekshirish va dekodlash
            if image_data.startswith("data:image/"):
                try:
                    format_part, imgstr = image_data.split(";base64,", 1)
                    ext = format_part.split("/")[-1]  # Masalan, "image/png" => "png"
                    image_bytes = base64.b64decode(imgstr)
                except Exception as e:
                    return JsonResponse({"success": False, "message": f"❌ Rasm dekodlashda xatolik: {str(e)}"}, status=400)
            else:
                # Agar `data:image/` bo‘lmasa, to‘g‘ridan-to‘g‘ri dekod qilishga harakat qilamiz
                try:
                    image_bytes = base64.b64decode(image_data)
                    ext = "jpeg"  # Default format
                except Exception as e:
                    return JsonResponse({"success": False, "message": f"❌ Rasm noto‘g‘ri formatda!"}, status=400)

            # ✅ Foydalanuvchini yaratish yoki olish
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"first_name": first_name, "last_name": last_name}
            )

            update_fields = {}
            if first_name and user.first_name != first_name:
                update_fields["first_name"] = first_name
            if last_name and user.last_name != last_name:
                update_fields["last_name"] = last_name
            if update_fields:
                for key, value in update_fields.items():
                    setattr(user, key, value)
                user.save()

            # ✅ AWS Rekognition orqali yuzni ro‘yxatdan o‘tkazish
            file_name = f"face_{user.id}.{ext}"
            face_id = register_face(user, image_bytes)

            if face_id:
                FaceID.objects.update_or_create(
                    user=user,
                    defaults={"aws_face_id": face_id, "image": ContentFile(image_bytes, name=file_name)}
                )
                login(request, user)
                messages.success(request, "✅ Face ID muvaffaqiyatli saqlandi va tizimga kirdingiz!")
                return JsonResponse({"success": True, "message": "✅ Face ID muvaffaqiyatli saqlandi!",
                                     "redirect_url": reverse('profile')})
            else:
                return JsonResponse(
                    {"success": False, "message": "❌ AWS Rekognition'ga yuz ma’lumotlarini saqlab bo‘lmadi!"},
                    status=500
                )

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "❌ JSON formatida xatolik bor!"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"❌ Server xatosi: {str(e)}"}, status=500)

    return render(request, "accounts/register_faceid.html", {"form": CustomUserCreationForm()})

@csrf_exempt  # ✅ CSRFni o‘chirish (faqat AJAX uchun)
def face_login_view(request):
    if request.method == "GET":
        return render(request, "accounts/login_faceid.html")  # ✅ Face ID sahifasini ochish

    elif request.method == "POST":
        try:
            if request.content_type != "application/json":
                return JsonResponse({"success": False, "message": "❌ So‘rov JSON formatida bo‘lishi kerak!"}, status=400)

            data = json.loads(request.body)  # ✅ JSON so‘rovni dekodlash
            image_base64 = data.get("image")
            next_url = data.get("next", reverse("profile"))  # ✅ `next` URL avtomatik olish

            if not image_base64:
                return JsonResponse({"success": False, "message": "❌ Rasm topilmadi!"}, status=400)

            user_id = recognize_face(image_base64)  # ✅ Face ID orqali foydalanuvchini aniqlash
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    login(request, user)

                    return JsonResponse({
                        "success": True,
                        "message": "✅ Face ID orqali tizimga kirdingiz!",
                        "redirect_url": next_url
                    })
                except User.DoesNotExist:
                    return JsonResponse({"success": False, "message": "❌ Foydalanuvchi topilmadi!"}, status=404)

            return JsonResponse({"success": False, "message": "❌ Face ID mos kelmadi."}, status=400)

        except json.JSONDecodeError as e:
            return JsonResponse({"success": False, "message": f"❌ JSON formatida xatolik: {str(e)}"}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"❌ Server xatosi: {str(e)}"}, status=500)



def recognize_face(image_base64):
    """ Face ID orqali foydalanuvchini aniqlash """
    try:
        image_bytes = base64.b64decode(image_base64)

        response = rekognition.search_faces_by_image(
            CollectionId=settings.AWS_REKOGNITION_COLLECTION,
            Image={"Bytes": image_bytes},
            MaxFaces=1,
            FaceMatchThreshold=90
        )

        if "FaceMatches" in response and response["FaceMatches"]:
            face_id = response["FaceMatches"][0]["Face"]["ExternalImageId"]
            return face_id  # ✅ Foydalanuvchi ID sini qaytarish

    except rekognition.exceptions.InvalidImageFormatException:
        print("❌ Rasm formati noto‘g‘ri! Iltimos, JPEG yoki PNG yuklang.")
    except rekognition.exceptions.ResourceNotFoundException:
        print("❌ Face ID kolleksiyasi mavjud emas! Yaratish kerak.")
    except Exception as e:
        print(f"❌ AWS Rekognition xatosi: {str(e)}")

    return None  # ✅ Agar hech qanday moslik topilmasa, `None` qaytadi



def logout_view(request):
    logout(request)
    messages.success(request, "Logged Out")
    return redirect("main")


@login_required(login_url='/login/')
def profile_view(request):
    return render(request, "myaccount.html",
                  context={
                      'categories': get_categories(),
                  })




@login_required(login_url="/users/login/")
def requests_view(request):
    user_requests = Requests.objects.filter(user=request.user).order_by('-id')
    search_queries = SearchQuery.objects.filter(user=request.user).order_by('-created_at')  # ❗ Foydalanuvchi qidirgan lekin topa olmagan kitoblar
    not_found_books = [query.title for query in search_queries]  # Faqat nomlarini olish

    paginator = Paginator(user_requests, 8)  # Har bir sahifada 8 ta element
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "accounts/download_requests.html", {
        "requests": page_obj,
        "search_queries": search_queries,  # ❗ HTML sahifaga yuboramiz
        "not_found_books": not_found_books,  # ❗ HTML sahifaga jo‘natamiz

        "categories": get_categories(),
    })



@login_required(login_url="/users/login/")
def downloads_view(request):
    user_downloads = Downloads.objects.filter(user=request.user).order_by('-id')
    paginator = Paginator(user_downloads, 8)  # Har bir sahifada 8 ta element
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "accounts/downloads.html", {
        "categories": get_categories(),
        "downloads": page_obj,
    })


def get_categories():
    """Helper function to get all categories."""
    return Category.objects.all()

from django.core.paginator import Paginator as DefaultPaginator

@login_required(login_url="/users/login/")
def history(request):
    histories = SearchHistory.objects.filter(user=request.user).order_by('-created_at') # created_at bo'yicha saralash tavsiya etiladi
    paginator = DefaultPaginator(histories, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "accounts/history.html", {
        "histories": page_obj,
        "categories": get_categories()
    })


def user_update(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('profile')  # Redirect to user profile page
        else:
            form = UserUpdateForm(instance=request.user)
        return render(request, 'accounts/myaccedit.html', {'form': form})
    return redirect('/users/login/')


