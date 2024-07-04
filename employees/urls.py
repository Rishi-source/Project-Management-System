from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('login', views.loginView, name='login'),
    path('login_user', views.login_user, name='login_user'),
    path('logout', views.logout_user, name='logout'),

    path('forgot_password', auth_views.PasswordChangeView.as_view(template_name='forgot_password.html'), name='forgot_password'),

 # This 'Z' character should not be here.

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

 ]





    # -------------------- PROJECTS --------------------#


