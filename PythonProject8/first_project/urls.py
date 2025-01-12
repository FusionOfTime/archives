"""
URL configuration for first_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from first import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home_page'),
    path('voting/', views.voting_page, name='voting_page'),
    path('voting/create', views.create_voting, name='create_voting'),
    path('voting/<int:voting_id>/', views.view_voting, name='view_voting'),
    path('voting/<int:voting_id>/edit/', views.edit_voting, name='edit_voting'),
    path('voting/<int:voting_id>/add_option/', views.add_option, name='add_option'),
    path('voting/<int:voting_id>/options/', views.view_options, name='view_options'),
    path('voting/<int:voting_id>/option/<int:option_id>/edit/', views.edit_option, name='edit_option'),
    path('voting/<int:voting_id>/results/', views.view_results, name='view_results'),
    path('votings/', views.list_votings, name='list_votings'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/history/', views.profile_history, name='profile_history'),
    path('complaints/create/', views.create_complaint, name='create_complaint'),
    path('complaints/status/', views.complaint_status, name='complaint_status'),
    path('complaints/', views.complaints, name='complaints'),
    path('voting/<int:voting_id>/add_likes/', views.add_likes, name='add_likes'),
    path('voting/<int:voting_id>/add_comment/', views.add_comment, name='add_comment'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('', include('first.urls'))
]