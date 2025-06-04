from django.urls import path
from .views import user_view, register_view, login_view, logout_view, refresh_jwt, google_login_view, update_username, upload_profile_picture, forgot_password, verify_code, reset_password
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("user", user_view, name="user-detail"),
    path('update-username', update_username, name='update-username'),
    path("profile-picture", upload_profile_picture, name="update-profile-picture"),
    path("register", register_view, name="register"),
    path("refresh", refresh_jwt, name="refresh"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("google", google_login_view, name="google-login"),
    path("forgot-password", forgot_password, name="forgot-password"),
    path("verify-code", verify_code, name="verify-code"),
    path("reset-password", reset_password, name="reset-password"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
