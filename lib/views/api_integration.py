import json
import requests
import logging
from django.shortcuts import render
from django.http import JsonResponse
from lib.models import SearchQuery, Notification

# Logger sozlash
logger = logging.getLogger(__name__)

def searching_dissertations(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title", "").strip()
            author = data.get("author", "").strip()

            if not title and not author:
                return JsonResponse({"error": "❌ Iltimos, kamida bitta maydonni to‘ldiring!"}, status=400)

            api_url = "https://diss.natlib.uz/api/query"
            query = f"{title} {author}".strip()

            payload = {"query": query}
            headers = {"Content-Type": "application/json"}

            logger.info(f"📡 API so‘rov yuborilmoqda: {payload}")
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            logger.info(f"🔄 API status kodi: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"❌ API xatosi: {response.status_code} - {response.text}")
                return JsonResponse({"error": f"❌ API xatosi: {response.status_code}"}, status=500)

            results = response.json()

            if not results or "error" in results:
                logger.warning("❌ API natija qaytarmadi yoki xato berdi!")
                return JsonResponse({"error": "❌ API natija qaytarmadi yoki xato berdi!"}, status=500)

            # API natijalarini formatlash
            formatted_results = [
                {
                    "Author": item.get("Author", ""),
                    "Title": item.get("Title", ""),
                    "Code": item.get("Code", ""),
                    "Year": item.get("Year", ""),
                    "sahifalar": item.get("sahifalar", ""),
                    "level": item.get("level", ""),
                    "downloads": item.get("downloads", None),
                }
                for item in results
            ]

            # 🔴 Agar natija bo'lmasa, qidiruvni saqlaymiz va bildirishnoma tizimini ishga tushiramiz
            if not formatted_results:
                search_query, created = SearchQuery.objects.get_or_create(
                    user=request.user if request.user.is_authenticated else None,
                    title=title,
                    author=author
                )
                if created:
                    logger.info(f"🔎 Yangi qidiruv saqlandi: {title} - {author}")
                return JsonResponse(
                    {"message": "🔎 Ma'lumot topilmadi, sizga bildirishnoma jo‘natamiz!"},
                    status=404
                )

            return JsonResponse({"results": formatted_results}, safe=False)

        except json.JSONDecodeError:
            logger.error("❌ JSON format xato!")
            return JsonResponse({"error": "❌ JSON format xato!"}, status=400)
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API xatosi: {str(e)}")
            return JsonResponse({"error": f"❌ API xatosi: {str(e)}"}, status=500)

    return render(request, "searching_dissertations.html")
