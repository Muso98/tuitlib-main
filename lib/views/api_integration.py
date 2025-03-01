import json
import requests
from django.shortcuts import render
from django.http import JsonResponse

def searching_dissertations(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title", "").strip()
            author = data.get("author", "").strip()

            print("📥 Qabul qilindi:", data)

            if not title and not author:
                return JsonResponse({"error": "❌ Iltimos, kamida bitta maydonni to‘ldiring!"}, status=400)

            api_url = "https://diss.natlib.uz/api/query"
            query = f"{title} {author}".strip()

            payload = {"query": query}
            print("📡 API-ga so‘rov yuborilmoqda:", payload)

            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            print("🔄 API status kodi:", response.status_code)
            print("📩 API javobi:", response.text)

            # Agar API xato qaytarsa
            if response.status_code != 200:
                return JsonResponse({"error": f"❌ API xatosi: {response.status_code}"}, status=500)

            # API dan kelgan ma’lumotni JSON formatga o‘tkazish
            results = response.json()

            # Agar API natija qaytarmasa yoki xatolik bo‘lsa
            if not results or "error" in results:
                return JsonResponse({"error": "❌ API natija qaytarmadi yoki xato berdi!"}, status=500)

            # Kutilgan natijalar formati
            formatted_results = []
            for item in results:
                formatted_results.append({
                    "Author": item.get("Author", ""),
                    "Title": item.get("Title", ""),
                    "Code": item.get("Code", ""),
                    "Year": item.get("Year", ""),
                    "sahifalar": item.get("sahifalar", ""),
                    "level": item.get("level", ""),
                    "downloads": item.get("downloads", None),
                })

            return JsonResponse({"results": formatted_results}, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "❌ JSON format xato!"}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"❌ API xatosi: {str(e)}"}, status=500)

    return render(request, "searching_dissertations.html")
