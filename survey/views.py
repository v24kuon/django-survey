from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'survey/home.html'

class SurveyView(TemplateView):
    template_name = 'survey/survey.html'
