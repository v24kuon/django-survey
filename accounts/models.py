"""
カスタムユーザーモデルとアクティベーショントークン

このモジュールでは、メールアドレス認証を使用したカスタムユーザーモデルと
アクティベーショントークンモデルを定義します。
"""

import os
import uuid
from datetime import timedelta
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string

def get_image_path(instance, filename):
    """チラシ画像のアップロードパスを生成"""
    unique_id = uuid.uuid4()
    extension = filename.split('.')[-1]
    return os.path.join('flyers', str(unique_id), f"{uuid.uuid4()}.{extension}")

class UserActivateToken(models.Model):
    """ユーザーアクティベーショントークンモデル"""
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    class Meta:
        verbose_name = _('アクティベーショントークン')
        verbose_name_plural = _('アクティベーショントークン')

    def __str__(self):
        return f"{self.user.email}のトークン"

    @classmethod
    def create_token(cls, user):
        """トークンを生成"""
        expired_at = timezone.now() + timedelta(hours=24)
        return cls.objects.create(user=user, expired_at=expired_at)

class CustomUserManager(BaseUserManager):
    """カスタムユーザーマネージャー"""
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル"""
    email = models.EmailField(
        _('メールアドレス'),
        unique=True,
        error_messages={'unique': _('このメールアドレスは既に登録されています。')},
    )
    # 後から入力可能なフィールド
    organization_name = models.CharField(_('団体名'), max_length=255, blank=True, null=True)
    representative_name = models.CharField(_('代表者名'), max_length=255, blank=True, null=True)
    booth_name = models.CharField(_('ブース名'), max_length=255, blank=True, null=True)
    booth_summary = models.TextField(_('ブースの概要'), blank=True, null=True)
    booth_description = models.TextField(_('ブースの詳細情報'), blank=True, null=True)

    # 新規登録時に必須のフィールド
    full_name = models.CharField(_('氏名'), max_length=255)
    phone = models.CharField(_('電話番号'), max_length=20)
    postal_code = models.CharField(_('郵便番号'), max_length=8)
    address = models.CharField(_('住所'), max_length=255)
    flyer_image = models.ImageField(
        _('チラシ画像'),
        upload_to=get_image_path,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
    )

    is_active = models.BooleanField(_('有効'), default=False)
    is_staff = models.BooleanField(_('管理者'), default=False)
    email_verified = models.BooleanField(_('メール認証済み'), default=False)
    date_joined = models.DateTimeField(_('登録日'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('ユーザー')
        verbose_name_plural = _('ユーザー')

    def send_verification_email(self, verification_url):
        """認証メールを送信"""
        context = {
            'user': self,
            'verification_url': verification_url,
            'expire_hours': 24,
        }
        subject = 'メールアドレスの確認'
        text_message = render_to_string('registration/email/verification.txt', context)
        html_message = render_to_string('registration/email/verification.html', context)

        send_mail(
            subject=subject,
            message=text_message,
            from_email=None,
            recipient_list=[self.email],
            html_message=html_message
        )
