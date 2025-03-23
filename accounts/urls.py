from django.urls import path
from .views import user_view, register_view,login_view,logout_view

urlpatterns = [
    path("user/", user_view, name="user-detail"),
    path("register/",register_view,name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
