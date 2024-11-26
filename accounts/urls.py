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

class AnonymousUserLoginView(views.AnonymousUserRequiredMixin, auth_views.LoginView):
    """未ログインユーザー専用のログインビュー"""
    form_class = EmailAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('login/', AnonymousUserLoginView.as_view(), name='login'),
    path('update/', views.UserUpdateView.as_view(), name='update'),
    path('email/change/', views.EmailChangeView.as_view(), name='email-change'),
    path('email/verify/<str:token>/', views.VerifyEmailChangeView.as_view(), name='verify-email-change'),
]
