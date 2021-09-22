from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('home/', views.add_task, name='home'),
    path('home/end_task/<int:pk>', views.end_task, name='endTask'),
    # path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('', views.CustomLoginView.as_view(template_name='todolist/signin.html'), name='signin'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(template_name='todolist/logout.html'), name='logout'),
]
