import base64
import boto3
import io
from django.conf import settings
from PIL import Image
from django.core.files.base import ContentFile

rekognition = boto3.client(
    'rekognition',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def compare_faces(image_base64):
    """ Yangi tasvirni AWS Rekognition-da saqlangan yuzlar bilan taqqoslash """
    try:
        image_bytes = base64.b64decode(image_base64)  # ✅ Base64 dan dekodlash

        response = rekognition.search_faces_by_image(
            CollectionId=settings.AWS_REKOGNITION_COLLECTION,
            Image={'Bytes': image_bytes},
            MaxFaces=1,
            FaceMatchThreshold=85
        )

        if response.get("FaceMatches"):
            return response["FaceMatches"][0]["Face"]["ExternalImageId"]  # ✅ User ID qaytariladi

    except rekognition.exceptions.InvalidParameterException:
        print("❌ AWS Rekognition: Noto‘g‘ri rasm formati yoki noto‘g‘ri parametr!")
    except rekognition.exceptions.ResourceNotFoundException:
        print("❌ AWS Rekognition: Kolleksiya topilmadi!")
    except Exception as e:
        print(f"❌ Compare faces error: {str(e)}")

    return None

def recognize_face(image_base64):
    """ Face ID orqali foydalanuvchini aniqlash """
    try:
        image_bytes = base64.b64decode(image_base64)

        response = rekognition.search_faces_by_image(
            CollectionId=settings.AWS_REKOGNITION_COLLECTION,
            Image={"Bytes": image_bytes},
            MaxFaces=1,
            FaceMatchThreshold=75  # ✅ BU YERDA 90 dan 75 ga tushirildi
        )

        print("🧐 AWS Rekognition javobi:", response)  # ✅ Log chiqarish

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





def register_face(user, image_data):
    """ Foydalanuvchi yuz ma'lumotlarini AWS Rekognition'ga yuklash """
    try:
        print(f"🔍 Foydalanuvchi: {user.id}, Rasmni AWS Rekognition'ga qo‘shyapmiz...")

        if isinstance(image_data, str):  # ✅ Agar Base64 bo‘lsa, dekodlash
            image_bytes = base64.b64decode(image_data.split(",")[1])
        elif isinstance(image_data, bytes):  # ✅ Agar bytes bo‘lsa, to‘g‘ridan-to‘g‘ri ishlatamiz
            image_bytes = image_data
        else:
            print("❌ Noto‘g‘ri rasm formati! Faqat JPEG yoki PNG yuboring.")
            return None

        # 🔥 AWS Rekognition'ga yuklash
        response = rekognition.index_faces(
            CollectionId=settings.AWS_REKOGNITION_COLLECTION,
            Image={'Bytes': image_bytes},
            ExternalImageId=str(user.id),  # ✅ Foydalanuvchi ID sifatida saqlash
            DetectionAttributes=['DEFAULT']
        )

        print("🧐 AWS Rekognition javobi:", response)  # ✅ Log chiqarish

        if "FaceRecords" in response and response["FaceRecords"]:
            return response["FaceRecords"][0]["Face"]["FaceId"]  # ✅ AWS Face ID qaytariladi
        else:
            print("❌ AWS Rekognition yuzni saqlay olmadi!")

    except rekognition.exceptions.InvalidParameterException:
        print("❌ AWS Rekognition: Noto‘g‘ri rasm formati yoki noto‘g‘ri parametr!")
    except rekognition.exceptions.ResourceNotFoundException:
        print("❌ AWS Rekognition: Face ID kolleksiyasi topilmadi! Uni yaratish kerak.")
    except Exception as e:
        print(f"❌ AWS Rekognition xatosi: {str(e)}")

    return None  # ✅ Agar xatolik bo‘lsa, `None` qaytaradi

def create_collection():
    """ AWS Rekognition kolleksiyasini yaratish (agar mavjud bo‘lmasa) """
    try:
        existing_collections = rekognition.list_collections()["CollectionIds"]
        if settings.AWS_REKOGNITION_COLLECTION in existing_collections:
            print(f"✅ Kolleksiya allaqachon mavjud: {settings.AWS_REKOGNITION_COLLECTION}")
            return

        rekognition.create_collection(CollectionId=settings.AWS_REKOGNITION_COLLECTION)
        print(f"✅ Kolleksiya yaratildi: {settings.AWS_REKOGNITION_COLLECTION}")

    except rekognition.exceptions.ResourceInUseException:
        print("⚠️ Kolleksiya allaqachon mavjud!")
    except Exception as e:
        print(f"❌ AWS Rekognition xatosi: {str(e)}")
