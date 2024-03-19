from django.urls import path
from myapp import views


urlpatterns = [
    path('', views.index_view),
    path('feed/', views.feed_view),
    path('cadastro/',views.cadastro_view),
    path('validacao/',views.validacao_view),
    path('login/', views.login_view),
    path('matriculas/',views.matriculas_view),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
  
    
]
    
    
