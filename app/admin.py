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
from .Models.stamps import Stamps
from .Models.reporting_and_complains import ReportingAndComplains
from .Models.users_blocking import UserBlocking
from .Models.terms_and_conditions_accept import TermsAndConditionsAccept
from .Models.DeviceFcmToken import DeviceFCM
from .Models.post_venues_tags import PostVenueTag
from .Models.user_current_app_version import UserCurrentAppVersion
from .Models.referrals_Users import ReferralsUsers
from .Models.events import Events, EventCategory
from .Models.event_attendees import EventAttendees
from .Models.event_posts import EventPosts
from .Models.venues_participating_in_event import VenuesParticipatingEvents
from .Models.trails.trailModel import Trail
from .Models.trails.trailSteps import TrailStep
from .Models.trails.trailRecord import TrailRecord
from .Models.trails.trailStepsRecord import TrailStepRecord

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
admin.site.register(Stamps)
admin.site.register(ReportingAndComplains)
admin.site.register(UserBlocking)
admin.site.register(TermsAndConditionsAccept)
admin.site.register(DeviceFCM)
admin.site.register(PostVenueTag)
admin.site.register(ReferralsUsers)
admin.site.register(UserCurrentAppVersion)

admin.site.register(Events)
admin.site.register(EventCategory)
admin.site.register(EventAttendees)
admin.site.register(EventPosts)
admin.site.register(VenuesParticipatingEvents)
admin.site.register(Trail)
admin.site.register(TrailStep)
admin.site.register(TrailRecord)
admin.site.register(TrailStepRecord)