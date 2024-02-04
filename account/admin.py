from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account


# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'uname', 'date_joined', 'last_login', 'is_staff', 'is_admin', 'is_superuser')
    search_fields = ('email', 'uname')
    readonly_fields = ('id', 'date_joined', 'last_login')
    filter_horizontal = ()
    ordering = ('uname',)
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)
