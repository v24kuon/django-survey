"""
管理画面のカスタマイズ

CustomUserモデルの管理画面での表示方法を定義します。
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """カスタムユーザーモデルの管理画面定義"""

    list_display = ('email', 'full_name', 'booth_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'full_name', 'booth_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('ブース情報'), {'fields': ('booth_name', 'booth_summary', 'booth_description', 'flyer_image')}),
        (_('個人情報'), {'fields': ('full_name', 'phone', 'postal_code', 'address')}),
        (_('権限'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('重要な日付'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
