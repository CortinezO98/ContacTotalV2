from .models import EdicionRevista

def latest_edicion(request):
    return {
        "latest_edicion": (
            EdicionRevista.objects
            .filter(status="published")                
            .order_by("-fecha_publicacion", "-id")
            .first()
        )
    }
