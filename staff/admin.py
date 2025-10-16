from django.contrib import admin
from .models import staff_info, set_refferal_points, set_points_price
# Register your models here.

admin.site.register(staff_info.Staff_Info)
admin.site.register(set_refferal_points.Set_Refferal_Points)
admin.site.register(set_points_price.Set_Point_Price)
