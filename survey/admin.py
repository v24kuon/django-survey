"""
アンケート管理画面の設定

django-nested-adminを使用して、アンケート、質問、選択肢の3階層の編集を可能にします。
"""

from django.contrib import admin
from django.forms import ModelForm
import nested_admin
from .models import Survey, Question, QuestionChoice, Answer, SurveyCategory
from django.db.models import Max

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
    list_display = ('user', 'question', 'text', 'created_at')
    list_filter = ('question__survey', 'user', 'created_at')
    search_fields = ('text', 'user__email', 'question__text')
    readonly_fields = ('created_at', 'updated_at')

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
