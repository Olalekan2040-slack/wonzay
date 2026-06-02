from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from .models import NewsletterSubscriber
import requests


class SubscribeView(View):
    def post(self, request):
        email = request.POST.get("email", "").strip().lower()
        first_name = request.POST.get("first_name", "").strip()
        source = request.POST.get("source", "popup")
        if not email:
            return JsonResponse({"success": False, "error": "Email required."})
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"first_name": first_name, "source": source}
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
        if settings.MAILCHIMP_WEBHOOK_URL:
            try:
                requests.post(settings.MAILCHIMP_WEBHOOK_URL, json={"email": email}, timeout=3)
            except Exception:
                pass
        return JsonResponse({"success": True, "created": created})


class UnsubscribeView(View):
    def get(self, request, token):
        subscriber = get_object_or_404(NewsletterSubscriber, unsubscribe_token=token)
        subscriber.is_active = False
        subscriber.save()
        from django.shortcuts import render
        return render(request, "newsletter/unsubscribed.html")
