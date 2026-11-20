from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView)

from user.views import CreateUserView, ManagerUserView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", ManagerUserView.as_view(), name="me"),
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="get-token"
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh"
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify")

]

app_name = "user"
