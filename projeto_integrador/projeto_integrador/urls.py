from django.urls import path
from myapp import views
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view),
    path('feed/', views.feed_view),
    path('cadastro/',views.cadastro_view),
    path('validacao/',views.validacao_view),
    path('login/', views.login_view),
    path('matriculas/',views.matriculas_view),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('CentralAluno/', views.CentralAluno_view),
    path('editar-perfil/', views.editar_perfil_view, name='editar_perfil'),
    path('download-comprovante/', views.download_comprovante_view, name='download_comprovante'),
    path('ValidacaoAluno/', views.ValidacaoAluno_view),
    
]
    
    
