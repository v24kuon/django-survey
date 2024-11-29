"""
アンケートモデル

このモジュールでは、アンケートの質問と回答を管理するモデルを定義します。
質問は管理者のみが作成でき、回答は認証済みユーザーのみが行えます。
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class SurveyCategory(models.Model):
    """アンケートカテゴリーモデル"""
    name = models.CharField(
        _('カテゴリー名'),
        max_length=100,
        help_text=_('カテゴリー名を100文字以内で入力してください。')
    )
    description = models.TextField(
        _('説明'),
        blank=True,
        help_text=_('カテゴリーの説明を入力してください。')
    )
    order = models.IntegerField(
        _('表示順'),
        default=0
    )
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        verbose_name = _('アンケートカテゴリー')
        verbose_name_plural = _('アンケートカテゴリー')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """保存時に表示順を自動設定"""
        if self._state.adding:  # 新規作成時のみ
            # 現在の最大値を取得
            max_order = SurveyCategory.objects.aggregate(
                models.Max('order'))['order__max']
            # None の場合は0、それ以外は最大値+1
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)

class Survey(models.Model):
    """アンケートモデル"""
    title = models.CharField(
        _('タイトル'),
        max_length=200,
        help_text=_('アンケートのタイトルを200文字以内で入力してください。')
    )
    category = models.ForeignKey(
        SurveyCategory,
        verbose_name=_('カテゴリー'),
        on_delete=models.PROTECT,
        related_name='surveys'
    )
    description = models.TextField(
        _('説明'),
        help_text=_('アンケートの詳細な説明を入力してください。')
    )
    summary = models.TextField(
        _('概要'),
        max_length=500,
        help_text=_('アンケートの概要を500文字以内で入力してください。')
    )
    start_date = models.DateTimeField(_('公開開始日時'))
    end_date = models.DateTimeField(_('公開終了日時'))
    created_at = models.DateTimeField(_('作成日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        verbose_name = _('アンケート')
        verbose_name_plural = _('アンケート')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Question(models.Model):
    """質問モデル"""
    QUESTION_TYPES = (
        ('text', _('一行テキスト')),
        ('textarea', _('複数行テキスト')),
        ('radio', _('ラジオボタン')),
        ('checkbox', _('チェックボックス')),
        ('select', _('セレクトボックス')),
    )

    survey = models.ForeignKey(
        Survey,
        verbose_name=_('アンケート'),
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.CharField(
        _('質問文'),
        max_length=200,
        help_text=_('質問の内容を200文字以内で入力してください。')
    )
    question_type = models.CharField(
        _('質問タイプ'),
        max_length=20,
        choices=QUESTION_TYPES,
        default='text'
    )
    order = models.IntegerField(
        _('表示順'),
        default=0
    )
    is_required = models.BooleanField(
        _('必須'),
        default=True
    )

    class Meta:
        verbose_name = _('質問')
        verbose_name_plural = _('質問')
        ordering = ['survey', 'order']

    def __str__(self):
        return f'{self.survey.title} - {self.text}'

class QuestionChoice(models.Model):
    """質問の選択肢モデル"""
    question = models.ForeignKey(
        Question,
        verbose_name=_('質問'),
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(
        _('選択肢'),
        max_length=200,
        help_text=_('選択肢の内容を200文字以内で入力してください。')
    )
    order = models.IntegerField(
        _('表示順'),
        default=0
    )

    class Meta:
        verbose_name = _('選択肢')
        verbose_name_plural = _('選択肢')
        ordering = ['question', 'order']

    def __str__(self):
        return f'{self.question.text} - {self.text}'

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
    choices = models.ManyToManyField(
        QuestionChoice,
        verbose_name=_('選択された選択肢'),
        blank=True,
        related_name='answers'
    )
    created_at = models.DateTimeField(_('回答日時'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新日時'), auto_now=True)

    class Meta:
        verbose_name = _('回答')
        verbose_name_plural = _('回答')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                name='unique_user_question'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.question}'
