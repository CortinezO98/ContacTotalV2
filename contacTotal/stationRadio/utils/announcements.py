from django.db.models import Q
from stationRadio.models import Announcement

def get_announcements(position, view_slug, limit=None):
    qs = (Announcement.objects.running()
          .filter(position=position)
          .filter(Q(show_in_all=True) | Q(placements__slug=view_slug))
          .distinct()
          .order_by('-date_created'))
    return qs[:limit] if limit else qs
