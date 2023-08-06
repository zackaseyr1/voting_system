from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('vote/<int:event_id>/', views.vote, name='vote'),
    path('results/<int:event_id>/', views.results, name='results'),
    path('view_events', views.view_events, name='view_events'),
    path('teams/', views.team_list, name='team_list'),
    path('team/<int:team_id>/', views.team_view, name='team_view'),
    path('get_latest_voting_results/<int:event_id>/', views.get_latest_voting_results, name='get_latest_voting_results'),

]
