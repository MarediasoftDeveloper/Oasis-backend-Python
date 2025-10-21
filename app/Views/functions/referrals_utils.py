from app.Models.earned_points import Earned_Points
from app.models import Customer_profile
from staff.models.set_refferal_points import Set_Refferal_Points
from app.Models.points_spent import Points_Spent

def get_reward_points():
    """Fetch the current reward point configuration."""
    points_setting = Set_Refferal_Points.objects.first()
    return points_setting.reward_points if points_setting else 0


def record_earned_points(sender, receiver, points):
    """Create Earned_Points records for both sender and receiver."""
    Earned_Points.objects.create(customer=sender, points_earned=points)
    Earned_Points.objects.create(customer=receiver, points_earned=points)




def record_spent_points(customer, points):
    """Create Earned_Points records for both sender and receiver."""
    Points_Spent.objects.create(customer=customer, points_spent=points)


def update_customer_profiles_after_refferal_completion(sender, receiver, points):
    """Update both users’ total redeemed points."""
    sender_profile, _ = Customer_profile.objects.get_or_create(customer=sender)
    receiver_profile, _ = Customer_profile.objects.get_or_create(customer=receiver)

    sender_profile.total_redeemed_points += points
    sender_profile.save()

    receiver_profile.total_redeemed_points += points
    receiver_profile.save()


def add_points_to_user(customer, points):

    Earned_Points.objects.create(customer=customer, points_earned=points)
    customer_profile, _ = Customer_profile.objects.get_or_create(customer=customer)

    customer_profile.total_redeemed_points += points
    customer_profile.save()

    