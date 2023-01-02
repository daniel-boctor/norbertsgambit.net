from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    #user routes
    path("login", auth_views.LoginView.as_view(template_name="NG/user/login.html"), name="login"),
    path("logout", auth_views.LogoutView.as_view(template_name="NG/user/logout.html"), name="logout"),
    path("password-reset", auth_views.PasswordResetView.as_view(template_name="NG/user/password_reset.html"), name="password_reset"),
    path("password-reset/done", auth_views.PasswordResetDoneView.as_view(template_name="NG/user/password_reset_done.html"), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(template_name="NG/user/password_reset_confirm.html"), name="password_reset_confirm"),
    path("password-complete", auth_views.PasswordResetCompleteView.as_view(template_name="NG/user/password_reset_complete.html"), name="password_reset_complete"),
    path("register", views.register, name="register"),
    path("user/<str:username>", views.user, name="user"),

    path("", views.norberts_gambit, name="index"),
    path("scrape_spreads/<str:ticker>", views.scrape_spreads, name="scrape_spreads"),
    path("api", views.norberts_gambit_api, name="norberts_gambit_api"),
    path("tax", views.norberts_gambit_tax, name="norberts_gambit_tax"),
    path("<str:crudop>", views.norberts_gambit, name="norberts_gambit"),
    path("<str:crudop>/<str:name>", views.norberts_gambit, name="norberts_gambit")
]