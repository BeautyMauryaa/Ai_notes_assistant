from django.http import JsonResponse


def health_check(request):
    """Basic liveness endpoint for uptime monitors / load balancers."""
    return JsonResponse({"status": "ok"})
