
from app.Models.earned_badges_by_user import Earned_Badges
from app.Models.event_badges_earned import EventBadgesEarned
from app.Models.event_attendees import EventAttendees
from venue.models.badges import BadgesLevel
from app.Models.earned_points import Earned_Points
from app.models import Customer_profile






def get_level_points_per_task(user, badge):

    earned_badges = Earned_Badges.objects.filter(user=user, badge=badge).count()
    badge_category = BadgesLevel.objects.filter(badge=badge)
    points=0
    for category in badge_category:
            if category.category.num_of_task_to_achieve_badge < earned_badges:
                points= category.points_per_task
                
                break
            else:
                points= category.points_per_task
               


from django.db import transaction
from django.db.models import F

def get_level_points_per_task_and_save_it(user, badge):

    if not user:
        raise ValueError("User is required")

    if not badge:
        raise ValueError("Badge is required")

    # Count how many times this user earned this badge before
    earned_badges_count = Earned_Badges.objects.filter(
        user=user,
        badge=badge
    ).count()

    # Get badge levels ordered by required tasks
    badge_levels = (
        BadgesLevel.objects
        .filter(badge=badge)
        .select_related("category")
        .order_by("category__num_of_task_to_achieve_badge")
    )

    if not badge_levels.exists():
        # No levels defined → give zero points
        points = 0
    else:
        points = 0
        for level in badge_levels:
            required_tasks = level.category.num_of_task_to_achieve_badge or 0
            level_points = level.points_per_task or 0
            earned_badges_count = earned_badges_count+1
            if required_tasks < earned_badges_count:
                points = level_points
            else:
                points = level_points
                # Stop once we hit a level not yet reached
                break

    # Atomic transaction to avoid race conditions
    with transaction.atomic():

        # Create earned badge
        Earned_Badges.objects.create(user=user, badge=badge)

        # Create earned points entry
        Earned_Points.objects.create(customer=user, points_earned=points)

        # Update profile safely
        profile, _ = Customer_profile.objects.select_for_update().get_or_create(customer=user)
        current_points = profile.total_redeemed_points or 0
        profile.total_redeemed_points = current_points + points

        profile.save()

    return points


def get_level_points_per_task_for_events(user, event, badge):

    if not user:
        raise ValueError("User is required")

    if not badge:
        raise ValueError("Badge is required")

    # Count how many times this user earned this badge before
    earned_badges_count = EventBadgesEarned.objects.filter(
        user=user,
        event=event
    ).count()

    # Get badge levels ordered by required tasks
    badge_levels = (
        BadgesLevel.objects
        .filter(badge=badge)
        .select_related("category")
        .order_by("category__num_of_task_to_achieve_badge")
    )

    if not badge_levels.exists():
        # No levels defined → give zero points
        points = 0
    else:
        points = 0
        for level in badge_levels:
            required_tasks = level.category.num_of_task_to_achieve_badge or 0
            level_points = level.points_per_task or 0
            earned_badges_count = earned_badges_count+1
            if required_tasks < earned_badges_count:
                points = level_points
            else:
                points = level_points
                # Stop once we hit a level not yet reached
                break

    # Atomic transaction to avoid race conditions
    with transaction.atomic():

        # Create earned points entry
        Earned_Points.objects.create(customer=user, points_earned=points)
        EventAttendees.objects.filter(user=user, event=event).update(attended=True)

        # Update profile safely
        profile, _ = Customer_profile.objects.select_for_update().get_or_create(customer=user)
        current_points = profile.total_redeemed_points or 0
        profile.total_redeemed_points = current_points + points

        profile.save()

    return points





# def get_level_points_per_task_for_events(user, badge):
    
#     if not user:
#         raise ValueError("User is required")

#     if not badge:
#         raise ValueError("Badge is required")


#     earned_badges = EventBadgesEarned.objects.filter(user=user, badge=badge).count()
#     badge_category = BadgesLevel.objects.filter(badge=badge)
#     points=0
#     for category in badge_category:
#         if category.category.num_of_task_to_achieve_badge < earned_badges:
#             points = category.points_per_task
#             break
#         else:
#             points= category.points_per_task

#     return points






# def get_level_points_per_task_and_save_it(user, badge):

#     earned_badges = Earned_Badges.objects.filter(user=user, badge=badge).count()
#     badge_category = BadgesLevel.objects.filter(badge=badge)
#     points=0
#     for category in badge_category:
#             if category.category.num_of_task_to_achieve_badge < earned_badges:
#                 points= category.points_per_task
#                 print(points)
#                 break
#             else:
#                 points= category.points_per_task
#                 print(points)
                 
                 

#     Earned_Points.objects.create(customer=user, points_earned=points)
#     Earned_Badges.objects.create(user=user, badge=badge)
#     customer_profile, _ = Customer_profile.objects.get_or_create(customer=user)

#     customer_profile.total_redeemed_points += points
#     customer_profile.save()

#     return points
