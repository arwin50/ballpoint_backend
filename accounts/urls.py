from django.urls import path
from .views import user_view, register_view,login_view,logout_view,refresh_jwt,google_login_view, update_username

urlpatterns = [
    path("user", user_view, name="user-detail"),
    path('user/update-username', update_username, name='update-username'),
    path("register",register_view,name="register"),
    path("refresh",refresh_jwt, name="refresh"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("google", google_login_view, name="google-login"), 
]
