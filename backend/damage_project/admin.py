from django.contrib import admin
from .models import PhoneUser, DamageAssessment, DamagePhoto, Calculation, SparePart, RepairWork


@admin.register(PhoneUser)
class PhoneUserAdmin(admin.ModelAdmin):
    list_display = ['phone', 'is_verified', 'created_at', 'last_login']
    list_filter = ['is_verified']
    search_fields = ['phone']


class DamagePhotoInline(admin.TabularInline):
    model = DamagePhoto
    extra = 0


@admin.register(DamageAssessment)
class DamageAssessmentAdmin(admin.ModelAdmin):
    list_display = ['vin', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['vin', 'user__phone']
    inlines = [DamagePhotoInline]


class SparePartInline(admin.TabularInline):
    model = SparePart
    extra = 1


class RepairWorkInline(admin.TabularInline):
    model = RepairWork
    extra = 1


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'total_cost', 'created_at']
    inlines = [SparePartInline, RepairWorkInline]
