from django.urls import path

from account import views

app_name = "account"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("edit/<user_id>", views.edit_profile, name="edit_profile"),
    path("<user_id>/", views.index, name="view")
]
