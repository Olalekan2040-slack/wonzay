from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("collections/", views.CollectionListView.as_view(), name="collection_list"),
    path("collections/<slug:slug>/", views.CollectionDetailView.as_view(), name="collection_detail"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
