from django.urls import path
from . import views


urlpatterns = [
    path("", views.index_page, name="index-page"),
    path("personal", views.personal_page, name="personal-page"),
    path("personal/<my_list>", views.personal_page, name="personal-page"),
    path("action/<int:task_id>", views.action_page, name="action-page"),
    path("register", views.register_page, name="register-page"),
    path("login", views.login_page, name="login-page"),
    path("logout", views.logout_page, name="logout-page"),
    path("delete-task/<int:task_id>", views.delete_task, name="delete-task"),
    path("delete-list/<int:list_id>", views.delete_list, name="delete-list"),
    path("completed-list/<int:list_id>", views.completed_list, name="completed-list"),
    path("progress-list/<int:list_id>", views.progress_list, name="progress-list")
]
