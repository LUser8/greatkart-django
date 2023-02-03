from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'date_joined', 'last_login', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined',)
    ordering = ('-date_joined',)
    search_fields = ('email', 'username')

    filter_horizontal = ()
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'username', 'last_login')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser')})
    )


admin.site.register(User, UserAdmin)
