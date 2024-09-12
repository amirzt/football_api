from django.contrib import admin

# Register your models here.
from shop.models import ZarinpalCode, Plan, Transaction, LotteryChance


@admin.register(ZarinpalCode)
class ZarinpalCodeAdmin(admin.ModelAdmin):
    list_display = ('code',)
    fields = ('code', 'is_available',)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title__startswith',)
    fields = ('title', 'description', 'price', 'is_available', 'duration', 'zarinpal_url')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'state', 'tracking_code')
    # search_fields = ('title__startswith',)
    fields = ('user', 'description', 'price', 'gateway', 'gateway_code', 'tracking_code', 'plan', 'state',)


@admin.register(LotteryChance)
class LotteryChanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'state', 'result', 'transaction', 'created_at', 'updated_at')
    # search_fields = ('title__startswith',)
    fields = ('user', 'state', 'result',)
