from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('login', views.loginView, name='login'),
    path('login_user', views.login_user, name='login_user'),
    path('logout', views.logout_user, name='logout'),
    path('forgot_password', auth_views.PasswordChangeView.as_view(template_name='forgot_password.html'), name='forgot_password'),
    # -------------------- PROJECTS --------------------#
    path('projects', views.projects, name='projects'),
    path('register/', views.register, name='register'),
    path('register_user/', views.register_user, name='register_user'),
    path('project/add', views.add_project, name='add_project'),
    path('project/<int:project_id>/edit', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/add_amountrecieved', views.add_amount_received, name='add_amount_recieved'),
    path('project/<int:project_id>/add_amountreleased', views.add_amount_released, name='add_amount_released'),
    path('project/<int:project_id>/add_progress', views.add_progress, name='add_progress'),
    path('project/<int:project_id>/add_expenditure', views.add_total_expenditure, name='add_expenditure'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/', views.view_project, name='view_project'),
    path('edit_date_of_completion/<int:project_id>/', views.edit_stipulated_date, name='edit_date_of_completion'),
    path('mark_project_completed/<int:project_id>/', views.mark_project_completed, name='mark_project_completed'),
    path('mark_project_handedover/<int:project_id>/', views.mark_project_handedover, name='mark_project_handedover'),
    path('project/<int:project_id>/amount_received/', views.amount_received, name='amount_received'),
    path('project/<int:project_id>/edit_amount_received/', views.edit_amount_received, name='edit_amount_received'),
    path('edit_amount_received/<int:project_id>/delete/', views.delete_amount_received, name='delete_amount_received'),
    path('project/<int:project_id>/edit_amount_released/', views.edit_amount_released, name='edit_amount_released'),
    path('project/<int:project_id>/delete_amount_released/', views.delete_amount_released, name='delete_amount_released'),
    path('project/<int:project_id>/edit_physical_progress/', views.edit_physical_progress, name='edit_physical_progress'),
    path('project/<int:project_id>/delete_physical_progress/', views.delete_physical_progress, name='delete_physical_progress'),
    path('project/<int:project_id>/edit_expenditure/', views.edit_expenditure, name='edit_expenditure'),
    path('project/<int:project_id>/delete_expenditure/', views.delete_expenditure, name='delete_expenditure'),
    path('project/amount_released_analysis', views.amount_released_analysis, name='amount_released_analysis'),
    path('project/amount_recieved_analysis', views.amount_recieved_analysis, name='amount_recieved_analysis'),
    path('project/expenditure_analysis', views.expenditure_analysis, name='expenditure_analysis'),
    path('project/expenditure_analysis_client', views.expenditure_analysis_client, name='expenditure_analysis_client'),
    path('project/amount_released_analysis_client', views.amount_released_analysis_client, name='amount_released_analysis_client'),
    path('project/amount_recieved_analysis_client', views.amount_recieved_analysis_client, name='amount_recieved_analysis_client'),
    path('notifications/', views.notification, name='notification'),
    path('project/<int:pk>/pdf/', views.GenerateProjectPDF.as_view(), name='generate_project_pdf'),
    path('not_allowed/', views.not_allowed, name='not_allowed'),
    path('project/<int:project_id>/add_split_projects', views.add_split_project, name='add_split_projects'),
    path('project/<int:project_id>/edit_split_project', views.edit_split_project, name='edit_split_project'),
    path('project/<int:project_id>/add_split_amountrecieved', views.add_split_amountrecieved, name='add_split_amountrecieved'),
    path('project/<int:project_id>/add_split_amountreleased', views.add_split_amountreleased, name='add_split_amountreleased'),
    path('project/<int:project_id>/add_split_expenditure', views.add_split_expenditure, name='add_split_expenditure'),
    path('project/<int:project_id>/add_split_progress', views.add_split_progress, name='add_split_progress'),
    path('project/<int:project_id>/edit_project', views.edit_sproject, name='edit_sproject'),
    path('project/<int:project_id>/edit_split_amount_received/', views.edit_split_amount_received, name='edit_split_amount_received'),
    path('edit_amount_received/<int:project_id>/split_delete/', views.delete_split_amount_received, name='delete_split_amount_received'),
    path('project/<int:project_id>/edit_split_amount_released/', views.edit_split_amount_released, name='edit_split_amount_released'),
    path('project/<int:project_id>/delete_split_amount_released/', views.delete_split_amount_released, name='delete_split_amount_released'),
    path('project/<int:project_id>/edit_split_physical_progress/', views.edit_split_physical_progress, name='edit_split_physical_progress'),
    path('project/<int:project_id>/delete_split_physical_progress/', views.delete_split_physical_progress, name='delete_split_physical_progress'),
    path('project/<int:project_id>/edit_split_expenditure/', views.edit_split_expenditure, name='edit_split_expenditure'),
    path('project/<int:project_id>/delete_split_expenditure/', views.delete_split_expenditure, name='delete_split_expenditure'),
    path('project/<int:project_id>/view_split_project/', views.view_split_project, name='view_split_project'),
    path('project/<int:project_id>/add_split_dates/', views.add_split_dates, name='add_split_dates'),
    path('project/<int:project_id>/view_split_details', views.view_split_details, name='view_split_details'),
    path('project/<int:pk>/split_pdf/', views.splitGenerateProjectPDF.as_view(), name='generate_split_project_pdf'),

 ]
    # -------------------- PROJECTS --------------------#


