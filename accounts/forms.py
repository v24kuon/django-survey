"""
ユーザーフォーム

一般ユーザー（ブース出展者）の登録に使用するフォームを定義します。
管理者はコマンドラインからのみ作成可能なため、管理者用フォームは不要です。
ログインはメールアドレスで行うため、メールアドレス認証フォームを定義します。
"""

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import CustomUser
from django import forms

class GeneralUserCreationForm(UserCreationForm):
    """一般ユーザー作成用フォーム"""
    class Meta:
        model = CustomUser
        fields = (
            'email', 'password1', 'password2',
            'full_name', 'phone', 'postal_code', 'address',
            'flyer_image'
        )

class EmailAuthenticationForm(AuthenticationForm):
    """メールアドレスでログインするためのフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['name'] = 'email'

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            if self.user_cache is None:
                raise ValidationError(
                    'メールアドレスまたはパスワードが正しくありません。',
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class UserUpdateForm(forms.ModelForm):
    """ユーザー情報更新用フォーム"""
    class Meta:
        model = CustomUser
        fields = (
            'organization_name', 'representative_name',
            'booth_name', 'booth_summary', 'booth_description',
            'full_name', 'phone', 'postal_code', 'address',
            'flyer_image'
        )

class EmailChangeForm(forms.Form):
    """メールアドレス変更用フォーム"""
    current_password = forms.CharField(
        label='現在のパスワード',
        widget=forms.PasswordInput,
        help_text='セキュリティのため、現在のパスワードを入力してください。'
    )
    new_email = forms.EmailField(
        label='新しいメールアドレス',
        help_text='確認メールを送信します。'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError('パスワードが正しくありません。')
        return current_password

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if CustomUser.objects.filter(email=new_email).exists():
            raise ValidationError('このメールアドレスは既に登録されています。')
        if new_email == self.user.email:
            raise ValidationError('現在のメールアドレスと同じです。')
        return new_email
