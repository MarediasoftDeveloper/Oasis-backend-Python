from django.contrib import admin
from .models import staff_info, set_refferal_points
from .models.set_points_price import PointsPricing 
# Register your models here.

admin.site.register(staff_info.Staff_Info)
admin.site.register(set_refferal_points.Set_Refferal_Points)

@admin.register(PointsPricing)
class PointsPricingAdmin(admin.ModelAdmin):
    list_display = ("price_per_point", "updated_at")

    def has_add_permission(self, request):
        return not PointsPricing.objects.exists()
