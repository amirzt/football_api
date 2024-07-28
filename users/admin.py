from django.contrib import admin

# Register your models here.
from users.models import CustomUser, Admob, CustomAd


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'expire_date', 'date_joint')
    search_fields = ('email__startswith', 'name__startswith')
    fields = (
        'email', 'name', 'score', 'credit', 'is_visible', 'is_active', 'is_staff', 'app_type', 'version', 'expire_date')


@admin.register(Admob)
class AdmobAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'active')
    fields = ('type', 'code', 'active')


@admin.register(CustomAd)
class CustomAdAdmin(admin.ModelAdmin):
    list_display = ('name', 'banner', 'link', 'active')
    fields = ('name', 'banner', 'link', 'active')


@admin.register(CustomAd)
class LotteryAdmin(admin.ModelAdmin):
    list_display = ('fa_title', 'active', 'price')
    fields = ('fa_title', 'fa_description', 'en_title', 'en_description', 'active', 'price')
