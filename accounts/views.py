"""
認証関連のビュー

ユーザー登録とメール認証機能を提供します。
一般ユーザーの登録時はメール認証が必要です。
"""

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, FormView
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .forms import GeneralUserCreationForm, UserUpdateForm, EmailChangeForm
from .models import UserActivateToken, CustomUser
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class AnonymousUserRequiredMixin(UserPassesTestMixin):
    """未ログインユーザーのみアクセス可能なミックスイン"""
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('home')

class SignUpView(AnonymousUserRequiredMixin, CreateView):
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

class UserUpdateView(LoginRequiredMixin, UpdateView):
    """ユーザー情報更新ビュー"""
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'registration/update.html'
    success_url = reverse_lazy('accounts:update')

    def get_object(self, queryset=None):
        """編集対象のユーザーを取得"""
        return self.request.user

    def form_valid(self, form):
        """フォームのバリデーションが成功した時の処理"""
        response = super().form_valid(form)
        messages.success(self.request, '登録情報を更新しました。')
        return response

    def form_invalid(self, form):
        """フォームのバリデーションが失敗した時の処理"""
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class EmailChangeView(LoginRequiredMixin, FormView):
    """メールアドレス変更ビュー"""
    form_class = EmailChangeForm
    template_name = 'registration/email_change.html'
    success_url = reverse_lazy('accounts:update')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            user = self.request.user
            new_email = form.cleaned_data['new_email']

            # アクティベーショントークンを生成
            token = UserActivateToken.create_token(user)
            verification_url = self.request.build_absolute_uri(
                reverse('accounts:verify-email-change', kwargs={'token': token.token})
            )

            # 新しいメールアドレスを一時的に保存
            token.extra_data = new_email
            token.save()

            # 確認メールを送信
            user.send_verification_email(verification_url, new_email)

            messages.success(
                self.request,
                f'確認メールを {new_email} に送信しました。'
                'メール内のリンクをクリックして、メールアドレスの変更を完了してください。'
            )
            return super().form_valid(form)

        except Exception:
            # エラーが発生した場合、トークンを削除（存在する場合）
            if 'token' in locals():
                token.delete()
            messages.error(self.request, 'メール送信中にエラーが発生しました。')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """フォームのバリデーションが失敗した時の処理"""
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class VerifyEmailChangeView(LoginRequiredMixin, TemplateView):
    """メールアドレス変更確認ビュー"""
    template_name = 'registration/verify_email_change.html'

    def get(self, request, *args, **kwargs):
        """GETリクエストの処理"""
        try:
            # トークンが有効なものを取得
            activate_token = UserActivateToken.objects.select_related('user').get(
                token=kwargs.get('token'),
                expired_at__gte=timezone.now(),
                user=request.user
            )

            # メールアドレスを更新
            user = activate_token.user
            new_email = activate_token.extra_data
            old_email = user.email
            user.email = new_email
            user.save()

            # 使用済みトークンを削除
            activate_token.delete()

            # 古いメールアドレスに通知を送信
            context = {
                'user': user,
                'old_email': old_email,
                'new_email': new_email,
            }
            subject = 'メールアドレスが変更されました'
            text_message = render_to_string('registration/email/email_change_notification.txt', context)
            html_message = render_to_string('registration/email/email_change_notification.html', context)

            send_mail(
                subject=subject,
                message=text_message,
                from_email=None,
                recipient_list=[old_email],
                html_message=html_message
            )

            messages.success(request, 'メールアドレスを変更しました。')
            return render(request, self.template_name, {'success': True})

        except UserActivateToken.DoesNotExist:
            messages.error(request, '無効なトークンです。')
            return render(request, self.template_name, {'success': False})
