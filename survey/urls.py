from django.urls import path
from .views import (
    HomeView,
    CategorySurveyListView,
    SurveyDetailView,
    SurveyAnswerView,
    SurveyCompleteView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<int:category_id>/', CategorySurveyListView.as_view(), name='category_survey_list'),
    path('survey/<int:pk>/', SurveyDetailView.as_view(), name='survey_detail'),
    path('survey/<int:pk>/answer/', SurveyAnswerView.as_view(), name='survey_answer'),
    path('survey/complete/', SurveyCompleteView.as_view(), name='survey_complete'),
]
