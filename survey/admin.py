from django.contrib import admin
from .models import Survey, Question, QuestionChoice, Answer

class QuestionChoiceInline(admin.TabularInline):
    """質問編集画面で選択肢を追加できるようにするインライン"""
    model = QuestionChoice
    extra = 3

class QuestionInline(admin.TabularInline):
    """アンケート編集画面で質問を追加できるようにするインライン"""
    model = Question
    extra = 3
    show_change_link = True

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """アンケート管理画面の設定"""
    list_display = ('title', 'start_date', 'end_date', 'created_at')
    search_fields = ('title', 'description', 'summary')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """質問管理画面の設定"""
    list_display = ('text', 'survey', 'question_type', 'order', 'is_required')
    list_filter = ('survey', 'question_type', 'is_required')
    search_fields = ('text', 'survey__title')
    inlines = [QuestionChoiceInline]

    def get_inlines(self, request, obj=None):
        """選択式質問の場合のみ選択肢を表示"""
        if obj and obj.question_type in ['radio', 'checkbox', 'select']:
            return [QuestionChoiceInline]
        return []
