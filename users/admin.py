from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .admin_forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Requests, Downloads, EmailOTP, FaceID, ResearchArea


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("email", "is_staff", "is_active", "first_name", "last_name", "birth_date")
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "last_name", "birth_date")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Downloads)
admin.site.register(Requests)
admin.site.register(EmailOTP)
admin.site.register(ResearchArea)


@admin.register(FaceID)
class FaceIDAdmin(admin.ModelAdmin):
    list_display = ["user", "aws_face_id", "created_at"]
    search_fields = ["user__email"]
    list_filter = ["created_at"]