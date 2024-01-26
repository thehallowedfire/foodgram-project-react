from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email',
                    'first_name', 'last_name',
                    'is_staff',)
    list_filter = ('email', 'username',)
    ordering = ('id',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)
