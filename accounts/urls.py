from django.urls import path
from .views import user_view, register_view,login_view,logout_view,refresh_jwt,google_login_view, update_username, upload_profile_picture
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("user", user_view, name="user-detail"),
    path('update-username', update_username, name='update-username'),
    path("profile-picture", upload_profile_picture, name="update-profile-picture"),
    path("register",register_view,name="register"),
    path("refresh",refresh_jwt, name="refresh"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("google", google_login_view, name="google-login"), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
