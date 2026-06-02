from .models import AnnouncementBar


def announcement_bars(request):
    bars = AnnouncementBar.objects.filter(is_active=True)
    return {"announcement_bars": bars}
