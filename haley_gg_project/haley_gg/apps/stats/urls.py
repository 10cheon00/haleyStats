from django.urls import path

from haley_gg.apps.stats import views


app_name = 'stats'

urlpatterns = [
    path('', views.ResultListView.as_view(), name='result_list'),
    path('new/', views.ResultCreateView.as_view(), name='create_result'),
    path('proleague/', views.ProleagueView.as_view(), name='proleague'),
    path('player/<name>', views.PlayerDetailView.as_view(), name='player'),
]
