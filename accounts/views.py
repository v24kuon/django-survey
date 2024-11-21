"""
認証関連のビュー

ユーザー登録とメール認証機能を提供します。
一般ユーザーの登録時はメール認証が必要です。
"""

from django.contrib.auth import login
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.utils import timezone
from .forms import GeneralUserCreationForm
from .models import UserActivateToken

class SignUpView(CreateView):
    """ユーザー登録ビュー"""
    form_class = GeneralUserCreationForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        try:
            # ユーザーを作成（メール認証前なのでis_active=False）
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # アクティベーショントークンを生成し、認証メールを送信
            token = UserActivateToken.create_token(user)
            verification_url = self.request.build_absolute_uri(
                reverse('accounts:verify-email', kwargs={'token': token.token})
            )
            user.send_verification_email(verification_url)

            return render(self.request, 'registration/signup_done.html', {
                'email': user.email
            })
        except Exception:
            messages.error(self.request, '登録処理中にエラーが発生しました。')
            return self.form_invalid(form)

class VerifyEmailView(TemplateView):
    """メール認証ビュー"""
    template_name = 'registration/verify_email.html'

    def get(self, request, *args, **kwargs):
        try:
            # トークンが有効かつ未認証ユーザーのトークンを取得
            activate_token = UserActivateToken.objects.select_related('user').get(
                token=kwargs.get('token'),
                expired_at__gte=timezone.now(),
                user__is_active=False
            )

            # ユーザーを有効化
            user = activate_token.user
            user.is_active = True
            user.email_verified = True
            user.save()

            # 使用済みトークンを削除
            activate_token.delete()

            # 認証完了後、自動ログイン
            login(request, user)
            return render(request, self.template_name, {'success': True})

        except UserActivateToken.DoesNotExist:
            return render(request, self.template_name, {'success': False})
