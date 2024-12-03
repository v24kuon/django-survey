from django.views.generic import TemplateView, ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Survey, SurveyCategory, Question, Answer, QuestionChoice

class BaseContextMixin:
    """
    全てのビューで共通して使用するコンテキストを提供するMixin
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey_categories'] = SurveyCategory.objects.all().order_by('order', 'name')

        # ログインユーザーの回答済みアンケートを取得
        if self.request.user.is_authenticated:
            answered_surveys = set(
                Answer.objects.filter(
                    user=self.request.user
                ).values_list('question__survey_id', flat=True).distinct()
            )
            context['answered_surveys'] = answered_surveys
        return context

class HomeView(BaseContextMixin, TemplateView):
    """
    ホーム画面を表示するビュー
    """
    template_name = 'survey/home.html'

class CategorySurveyListView(BaseContextMixin, ListView):
    """
    カテゴリー別のアンケート一覧を表示するビュー
    """
    model = Survey
    template_name = 'survey/category_survey_list.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        """カテゴリーに属するアンケートを取得"""
        self.category = get_object_or_404(SurveyCategory, pk=self.kwargs.get('category_id'))
        return self.category.surveys.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class SurveyDetailView(LoginRequiredMixin, BaseContextMixin, DetailView):
    """
    アンケート詳細・回答ページを表示するビュー
    """
    model = Survey
    template_name = 'survey/survey_detail.html'
    context_object_name = 'survey'
    login_url = 'accounts:login'

    def get(self, request, *args, **kwargs):
        # ユーザーがすでにこのアンケートに回答済みか確認
        survey_id = self.kwargs['pk']
        if Answer.objects.filter(user=request.user, question__survey_id=survey_id).exists():
            return redirect('home')  # 回答済みの場合はホームにリダイレクト
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all().order_by('order')
        return context

    def get_queryset(self):
        """公開期間中のアンケートのみ取得"""
        now = timezone.now()
        return Survey.objects.filter(
            pk=self.kwargs['pk'],
            start_date__lte=now,
            end_date__gte=now
        )

class SurveyAnswerView(LoginRequiredMixin, View):
    """
    アンケートの回答を処理するビュー
    """
    def post(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        user = request.user

        try:
            for question in survey.questions.all():
                # 質問タイプに応じて回答データを取得
                if question.question_type in ['radio', 'select']:
                    answer_text = ''
                    answer_choices = [request.POST.get(f'question_{question.id}')]
                elif question.question_type == 'checkbox':
                    answer_text = ''
                    answer_choices = request.POST.getlist(f'question_{question.id}')
                else:  # text, textarea
                    answer_text = request.POST.get(f'question_{question.id}', '')
                    answer_choices = []

                # 回答を保存
                answer = Answer.objects.create(
                    user=user,
                    question=question,
                    text=answer_text
                )

                # 選択肢がある場合は保存
                if answer_choices and any(answer_choices):
                    choices = QuestionChoice.objects.filter(
                        id__in=answer_choices,
                        question=question
                    )
                    answer.choices.set(choices)

        except Exception as e:
            return redirect('survey_detail', survey.id)

        return redirect('survey_complete')

class SurveyCompleteView(BaseContextMixin, TemplateView):
    """
    アンケート回答完了ページを表示するビュー
    """
    template_name = 'survey/survey_complete.html'
