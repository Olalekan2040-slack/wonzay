from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("submit/<slug:product_slug>/", views.SubmitReviewView.as_view(), name="submit"),
]
