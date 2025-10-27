from django.contrib import admin
from .models.badge_category import Badge_Category
from .models.badges import Badges
from .models.menu import Menu_Items
from .models.menu_categories import Food_Menu_Category
from .models.venue_info import Venue_Info
from .models.venue_opening_hours import Venue_Opening_Hours
from .models.challenges import Challenges
from .models.rewards import Rewards
from .models.raffles import Raffles
from .models.qr_info_model import QR_Info
from .models.venue_badges import Venue_Badges

# Register your models here.
admin.site.register(Venue_Badges)
admin.site.register(Venue_Info)
admin.site.register(Venue_Opening_Hours)
admin.site.register(Food_Menu_Category)
admin.site.register(Menu_Items)
admin.site.register(Badge_Category)
admin.site.register(Badges)
admin.site.register(Challenges)
admin.site.register(Raffles)
admin.site.register(Rewards)
admin.site.register(QR_Info)