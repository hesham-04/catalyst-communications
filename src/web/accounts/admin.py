from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Custom UserAdmin
class UserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'username', 'email', 'password', 'bio', 'role', 'image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'bio', 'role', 'image', 'is_staff', 'is_active')}
        ),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'role')
    ordering = ('username',)

# Register the model with the custom admin
admin.site.register(User, UserAdmin)
