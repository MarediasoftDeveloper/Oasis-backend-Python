
from app.Models.earned_badges_by_user import Earned_Badges
from venue.models.badges import BadgesLevel
from app.Models.earned_points import Earned_Points
from app.models import Customer_profile













def get_level_points_per_task_and_save_it(user, badge):

    earned_badges = Earned_Badges.objects.filter(user=user, badge=badge).count()
    badge_category = BadgesLevel.objects.filter(badge=badge)
    points=0
    for category in badge_category:
            if category.category.num_of_task_to_achieve_badge < earned_badges:
                points= category.points_per_task
                print(points)
                break
            else:
                points= category.points_per_task
                print(points)
                 
                 

    Earned_Points.objects.create(customer=user, points_earned=points)
    Earned_Badges.objects.create(user=user, badge=badge)
    customer_profile, _ = Customer_profile.objects.get_or_create(customer=user)

    customer_profile.total_redeemed_points += points
    customer_profile.save()

    return True
