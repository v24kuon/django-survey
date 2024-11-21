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
