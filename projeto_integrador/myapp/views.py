from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from .models import Aprovado, Cadastro
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def index_view(request):
    return HttpResponseRedirect('/feed')

def feed_view(request):
    return render(request, 'feed.html') 
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html', {
            'incorrect_login': False
        })
    elif request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/matriculas')
        else:
            return render(request, 'login.html', {
                'incorrect_login': True
            })  
    else:
        return HttpResponseBadRequest()
    
@login_required(login_url='/login')   
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/feed')


@login_required(login_url='/login') 
def matriculas_view(request):
    cadastros = Cadastro.objects.all()  # Obter apenas o primeiro cadastro
    aprovados = Aprovado.objects.all()
    cpfs_cadastrados = list(Cadastro.objects.values_list('aprovados__cpf', flat=True))
    return render(request, 'matriculas.html', {'cadastros': cadastros, 'aprovados': aprovados, 'cpfs_cadastrados': cpfs_cadastrados})


def validacao_view(request):
    if request.method == "GET":
        return render(request, 'validacao.html', {"aprovado": False})
    elif request.method == "POST":
        cadastros = Cadastro.objects.all()
        cpf = request.POST.get('cpf')

        if Cadastro.objects.filter(aprovados__cpf=cpf).exists():
            return render(request, 'validacao.html',{'cadastros': cadastros}, )

            
        # Verificar se o CPF digitado está presente no modelo Aprovado
        elif Aprovado.objects.filter(cpf=cpf).exists() :
            # Se o CPF existe, armazenar as informações na sessão
            aprovado = Aprovado.objects.get(cpf=cpf)
            request.session['cpf_validado'] = cpf
            request.session['nome_aprovado'] = aprovado.name
            request.session['curso_aprovado'] = aprovado.curso
            return redirect("/cadastro")
        else:
            return render(request, 'validacao.html', {"aprovado": True})  # Renderizar uma página informando que o CPF é inválido
    else:
        return HttpResponseBadRequest()
    
    
def cadastro_view(request):
    if request.method == 'GET':
        cpf_validado = request.session.get('cpf_validado')

        if cpf_validado:
            try:
                aprovado = Aprovado.objects.get(cpf=cpf_validado)
                return render(request, 'cadastro.html', {'aprovado': aprovado})
            except Aprovado.DoesNotExist:
                return render(request, 'cadastro.html', {'aprovado': None})
        else:
            return HttpResponseBadRequest("Nenhum CPF validado encontrado na sessão.")

    elif request.method == 'POST':
        escola = request.POST.get("escola", "")
        email = request.POST.get("email", "")
        nascimento = request.POST.get("nascimento", "")
        endereco = request.POST.get("endereco", "")
        cidade = request.POST.get("cidade", "")
        arquivo = request.FILES.get('arquivo', None)
        cpf_validado = request.session.get('cpf_validado')

    if escola and email and nascimento and endereco and cidade and arquivo and cpf_validado:
        try:
            aprovado = Aprovado.objects.get(cpf=cpf_validado)
            cadastro = Cadastro.objects.create(
                escola=escola,
                email=email,
                aprovados=aprovado,
                nascimento=nascimento,
                endereco=endereco,
                cidade=cidade,
                arquivo=arquivo
            )
            return redirect('/feed')
        except Aprovado.DoesNotExist:
            return HttpResponseBadRequest("Nenhum registro aprovado encontrado com o CPF validado.")
    else:
        return HttpResponseBadRequest("Todos os campos obrigatórios devem ser preenchidos.")