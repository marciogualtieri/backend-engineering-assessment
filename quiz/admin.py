from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import forms, models


class UserAdmin(BaseUserAdmin):
    add_form = forms.UserCreationForm
    form = forms.UserChangeForm
    model = models.User
    list_display = ("username", "id")
    readonly_fields = ("id",)
    list_filter = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_superuser", "is_active", "is_quizzer")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "is_quizzer",
                ),
            },
        ),
    )
    search_fields = ("username",)
    ordering = ("username",)


admin.site.register(models.Quiz)
admin.site.register(models.Question)
admin.site.register(models.Choice)
admin.site.register(models.Assignment)
admin.site.register(models.Answer)
admin.site.register(models.User, UserAdmin)
