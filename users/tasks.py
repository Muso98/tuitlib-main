import random
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from lib.models import Book
from users.models import EmailOTP, User, ResearchArea, SearchHistory
from django.conf import settings
from celery import shared_task, group
import json


def otp_code() -> str:
    return ''.join(random.choices('0123456789', k=6))


@shared_task()
def verification_mail_sender(email):
    code = otp_code()
    EmailOTP.objects.create(
        email=email,
        code=code
    )
    subject = _('Verification code for Smart TUIT')
    message_code_text = _("Your verification code is")

    message = f"{message_code_text} {code}."

    from_ = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_, [email], fail_silently=False)


@shared_task()
def get_users_list(book_id):
    users_email_list = []

    book = Book.objects.get(id=book_id)
    subject = _('New book added to library')
    link_html = format_html('<a href="http://localhost:8000{}">{}</a>',
                            book.get_absolute_url(), _("View Book"))
    message = _(f"New Book: {book.name}. Link: {link_html}")

    research_area = ResearchArea.objects.get(name=book.resource_area.name)
    print(research_area)
    users = User.objects.all()
    print(users)

    for user in users:
        user_research_areas = user.research_area.all()
        if research_area in user_research_areas:
            users_email_list.append(user.email)

    print(users_email_list)
    # Chain recommendation email tasks for each user's email
    email_tasks = group(
        send_recommendation_mail.s(email, message, subject) for email in users_email_list
    )
    email_tasks.apply_async()


@shared_task()
def send_recommendation_mail(email, message, subject):
    send_mail(
        subject=subject,
        message='',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=message,
        fail_silently=False
    )


@shared_task()
def save_user_search_history(user, query):
    user_json = json.loads(user)
    user = User.objects.get(id=user_json[0]["pk"])
    SearchHistory.objects.create(
        user=user,
        query=query
    )
