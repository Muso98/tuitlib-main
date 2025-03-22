from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404

from lib.models import Book
from .models import Requests, Downloads, User, ResearchArea


@login_required(login_url="login")
def download_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.permission == 'public':
        download_obj = Downloads.objects.create(
            book=book,
            user=request.user
        )
        book.download_count += 1
        book.save(update_fields=["download_count"])
        book_file = book.file
        if book_file:
            try:
                with open(book_file.path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename={book_file.name}'
                    return response
            except FileNotFoundError:
                raise Http404("File Not Found")
        raise Http404("File Not Found")
    raise Http404("File Not Found")


def request_book(request, book_id):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # If the user is authenticated, proceed
        book = get_object_or_404(Book, id=book_id)
        # Create or retrieve a Requests object associated with the book and the authenticated user
        request_obj, created = Requests.objects.get_or_create(
            book=book,
            user=request.user
        )
        print(request_obj.status_request)
        # Check the status of the request and return a JSON response accordingly
        if created:
            # If the request was newly created, return "pending" status
            return JsonResponse(
                {
                    "status": "pending",
                    "status_code": 200
                }
            )
        if request_obj.status_request == "pending":
            # If the request status is "pending", return "accepted" status
            return JsonResponse(
                {
                    "status": "pending",
                }
            )
        if request_obj.status_request == "rejected":
            # If the request status is "rejected", return "rejected" status
            return JsonResponse(
                {
                    "status": "rejected",
                }
            )

        if request_obj.status_request == "accepted":
            book.download_count += 1
            book.save(update_fields=["download_count"])
            return JsonResponse(
                {
                    "url": book.file.url,
                    "status": "accepted",
                    "status_code": 200
                }
            )
    else:
        # If the user is not authenticated, return unauthorized status and URL to login page
        return JsonResponse({
            'status': 'unauthorized',
            'url': '/users/login/'
        })

    # If none of the above conditions are met, return "None" status
    return JsonResponse({
        "status": "None"
    })


def get_users_ids(request):
    book = Book.objects.all().order_by('id').last()
    data = {
        "book": book.id,
        "book_name": book.name,
        "book_author": book.author,
        "book_publisher": book.publisher,
        "book_year": book.published_year,
        "book_resource_area": book.resource_area.name
    }
    research_area = ResearchArea.objects.get(id=20)
    # users = User.objects.prefetch_related('research_area')
    users_id_list = []
    data['users'] = users_id_list

    users = User.objects.all()

    for user in users:
        user_research_areas = user.research_area.all()
        if research_area in user_research_areas:
            users_id_list.append(user.email)
    return JsonResponse({"test": data})

