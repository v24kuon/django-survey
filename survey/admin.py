"""
アンケート管理画面の設定

django-nested-adminを使用して、アンケート、質問、選択肢の3階層の編集を可能にします。
"""

from django.contrib import admin
from django.forms import ModelForm
import nested_admin
from .models import Survey, Question, QuestionChoice, Answer, SurveyCategory
from django.db.models import Max
from django.utils.safestring import mark_safe

class QuestionChoiceInline(nested_admin.NestedTabularInline):
    """質問編集画面で選択肢を追加できるようにするインライン"""
    model = QuestionChoice
    extra = 1
    min_num = 0
    sortable_field_name = "order"

class QuestionInlineForm(ModelForm):
    """質問フォームのカスタマイズ"""
    class Meta:
        model = Question
        fields = '__all__'

    class Media:
        js = ('js/admin_survey.js',)

class QuestionInline(nested_admin.NestedTabularInline):
    """アンケート編集画面で質問を追加できるようにするインライン"""
    model = Question
    form = QuestionInlineForm
    extra = 1
    inlines = [QuestionChoiceInline]
    fields = ('text', 'question_type', 'order', 'is_required')
    sortable_field_name = "order"

class SurveyAdmin(nested_admin.NestedModelAdmin):
    """アンケート管理画面の設定"""
    list_display = ('title', 'start_date', 'end_date', 'created_at')
    search_fields = ('title', 'description', 'summary')
    inlines = [QuestionInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """回答管理画面の設定"""
    list_display = ('survey_title', 'user_full_name', 'user_email', 'answer_date')
    list_filter = ('question__survey', 'user', 'created_at')
    search_fields = ('question__survey__title', 'user__email', 'text')
    readonly_fields = (
        'survey_title', 'user_full_name', 'user_email',
        'created_at', 'updated_at', 'all_answers'
    )
    date_hierarchy = 'created_at'

    fieldsets = (
        ('回答者情報', {
            'fields': ('user_full_name', 'user_email')
        }),
        ('アンケート情報', {
            'fields': ('survey_title', 'all_answers')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def all_answers(self, obj):
        """ユーザーの全回答を表示"""
        survey = obj.question.survey
        user = obj.user
        answers = Answer.objects.filter(
            question__survey=survey,
            user=user
        ).select_related('question').order_by('question__order')

        html = ['<table class="table">']
        html.append('<thead><tr><th>質問</th><th>回答</th></tr></thead>')
        html.append('<tbody>')

        for answer in answers:
            question_text = answer.question.text
            if answer.question.question_type in ['radio', 'checkbox', 'select']:
                answer_text = ', '.join([choice.text for choice in answer.choices.all()])
            else:
                answer_text = answer.text

            html.append(f'<tr><td>{question_text}</td><td>{answer_text}</td></tr>')

        html.append('</tbody></table>')
        return mark_safe(''.join(html))
    all_answers.short_description = '回答内容'

    def survey_title(self, obj):
        """アンケートのタイトルを表示"""
        return obj.question.survey.title
    survey_title.short_description = 'アンケート'
    survey_title.admin_order_field = 'question__survey__title'

    def user_full_name(self, obj):
        """回答者の氏名を表示"""
        return obj.user.full_name
    user_full_name.short_description = '氏名'
    user_full_name.admin_order_field = 'user__full_name'

    def user_email(self, obj):
        """回答者のメールアドレスを表示"""
        return obj.user.email
    user_email.short_description = 'メールアドレス'
    user_email.admin_order_field = 'user__email'

    def answer_date(self, obj):
        """回答日時を表示"""
        return obj.created_at
    answer_date.short_description = '回答日'
    answer_date.admin_order_field = 'created_at'

    def get_queryset(self, request):
        """同じユーザーの同じアンケートへの回答をまとめて表示"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'question__survey',
            'user'
        ).filter(
            question__order=1
        ).order_by(
            'question__survey',
            'user',
            '-created_at'
        )

    def has_add_permission(self, request):
        """追加権限を無効化"""
        return False

    def has_change_permission(self, request, obj=None):
        """変更権限を無効化"""
        return False

@admin.register(SurveyCategory)
class SurveyCategoryAdmin(admin.ModelAdmin):
    """アンケートカテゴリー管理画面の設定"""
    list_display = ('name', 'order', 'created_at')
    search_fields = ('name', 'description')
    ordering = ['order', 'name']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # 新規作成時のみ
            max_order = SurveyCategory.objects.aggregate(Max('order'))['order__max']
            form.base_fields['order'].initial = (max_order or 0) + 1
        return form

admin.site.register(Survey, SurveyAdmin)
