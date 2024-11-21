"""
アンケートモデル

このモジュールでは、アンケートの質問と回答を管理するモデルを定義します。
質問は管理者のみが作成でき、回答は認証済みユーザーのみが行えます。
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Question(models.Model):
    """質問モデル"""
    text = models.CharField(
        _('質問文'),
        max_length=200,
        help_text=_('質問の内容を200文字以内で入力してください。')
    )
    created_at = models.DateTimeField(
        _('作成日時'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('更新日時'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('質問')
        verbose_name_plural = _('質問')
        ordering = ['-created_at']

    def __str__(self):
        return self.text

class Answer(models.Model):
    """回答モデル"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('回答者'),
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        verbose_name=_('質問'),
        on_delete=models.CASCADE,
        related_name='answers'
    )
    text = models.TextField(
        _('回答'),
        help_text=_('質問に対する回答を入力してください。')
    )
    created_at = models.DateTimeField(
        _('回答日時'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('更新日時'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('回答')
        verbose_name_plural = _('回答')
        ordering = ['-created_at']
        # 1ユーザーにつき1質問に1回だけ回答可能
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                name='unique_user_question'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.question}'
