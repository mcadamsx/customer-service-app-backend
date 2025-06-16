from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AdminUser

class CustomAdminUserAdmin(UserAdmin):
    model = AdminUser
    list_display = ('company_email', 'company_name', 'is_active')
    search_fields = ('company_email', 'company_name')
    readonly_fields = ('registration_token',)
    ordering = ['company_email']  # ✅ fix: use valid field name

    # Define what fields show up in the admin "edit user" page
    fieldsets = (
        (None, {'fields': ('company_email', 'password')}),
        ('Company Info', {'fields': ('company_name', 'registration_token')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Define what fields show up when adding a new user via the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('company_email', 'company_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(AdminUser, CustomAdminUserAdmin)
