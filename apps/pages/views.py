from django.views.generic import TemplateView, DetailView, View
from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .models import StaticPage


class StaticPageView(DetailView):
    model = StaticPage
    template_name = "pages/static_page.html"
    context_object_name = "page"
    queryset = StaticPage.objects.filter(is_active=True)


class ContactView(View):
    template_name = "pages/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        subject = request.POST.get("subject", "Contact Form")
        message = request.POST.get("message", "")
        send_mail(
            subject=f"[Wonzays] {subject}",
            message=f"From: {name} <{email}>\n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
        return render(request, self.template_name, {"sent": True})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
