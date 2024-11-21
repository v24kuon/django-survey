"""
認証関連のURL設定

カスタムビュー（ユーザー登録、メール認証）のURLパターンを定義します。
標準の認証ビューは django.contrib.auth.urls で提供されます。
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import EmailAuthenticationForm
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('login/', auth_views.LoginView.as_view(
        form_class=EmailAuthenticationForm,
        template_name='registration/login.html'
    ), name='login'),
]
