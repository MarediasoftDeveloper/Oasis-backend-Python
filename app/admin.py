from django.contrib import admin
from .models import Customer, Customer_profile
from .Models.otp_requests import OTP_Code
from .Models.referrals import Referrals
from .Models.raffles_entry import Raffles_Entry
from .Models.rewards_achiever import Rewards_Achiever
from .Models.challenge_achiever import Challenge_Achiever
from .Models.social_media_accounts import Social_Media_Accounts
from .Models.users_interests import User_Interest
from .Models.interests import Customer_Interest     
from .Models.posts import Post
from .Models.points_spent import Points_Spent
from .Models.earned_points import Earned_Points
from .Models.notifications import Notifications
from .Models.friendships import Friendships
from .Models.earned_badges_by_user import Earned_Badges
# Register your models here.

admin.site.register(Customer)
admin.site.register(OTP_Code)
admin.site.register(User_Interest)
admin.site.register(Customer_Interest)
admin.site.register(Customer_profile)
admin.site.register(Social_Media_Accounts)
admin.site.register(Referrals)
admin.site.register(Raffles_Entry)
admin.site.register(Rewards_Achiever)
admin.site.register(Challenge_Achiever)
admin.site.register(Post)
admin.site.register(Points_Spent)
admin.site.register(Earned_Points)
admin.site.register(Notifications)
admin.site.register(Friendships)
admin.site.register(Earned_Badges)