
from django.shortcuts import redirect




def trail_scan_link(request, code):
    return redirect("https://apps.venue-myoasis.co.nz/")


def challenge_scan_link(request, code):
    return redirect("https://apps.venue-myoasis.co.nz/")


def open_app_link(request):
    return redirect(
        "https://apps.venue-myoasis.co.nz/"
    )