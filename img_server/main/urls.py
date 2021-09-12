from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add, name="add"),
    path("compute/<str:ops>", views.compute, name="compute"),
    path("convolute/", views.convolute, name="convolute")
]
