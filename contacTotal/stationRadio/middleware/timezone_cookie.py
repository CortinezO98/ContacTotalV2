import pytz
from django.utils import timezone as djtz

class ActivateUserTimezoneMiddleware:
    """
    Activa la zona horaria del usuario leída de la cookie 'user_tz' (si es válida).
    Fallback: TZ por defecto del proyecto (settings.TIME_ZONE).
    """
    COOKIE_NAME = "user_tz"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get(self.COOKIE_NAME)
        if tzname:
            try:
                djtz.activate(pytz.timezone(tzname))
                request.user_timezone = tzname 
            except Exception:
                request.user_timezone = None
        else:
            request.user_timezone = None
        return self.get_response(request)
