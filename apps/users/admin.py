# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User

# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'nom ', 'prenom ', 'user_type', 'is_staff')
#     list_filter = ('user_type', 'is_staff', 'is_active')
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Informations personnelles', {'fields': ('nom', 'last_name', 'email', 'phone_number')}),
#         ('Rôle', {'fields': ('user_type',)}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
#         }),
#     )
#     search_fields = ('username', 'email', 'nom', 'last_name')
#     ordering = ('username',)

# admin.site.register(User, CustomUserAdmin) 