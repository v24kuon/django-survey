from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('survey.urls')),
    path('accounts/', include('accounts.urls')),  # カスタムビュー用
    path('accounts/', include('django.contrib.auth.urls')),  # 標準認証ビュー用
]
