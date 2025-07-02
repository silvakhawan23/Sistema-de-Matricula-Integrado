from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from .models import Aprovado, Cadastro
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from reportlab.lib.colors import HexColor





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
    
    
def download_comprovante_view(request):
    cpf = request.session.get('cpf_validado')

    if not cpf:
        return redirect('/ValidacaoAluno')

    try:
        aprovado = Aprovado.objects.get(cpf=cpf)
        cadastro = Cadastro.objects.get(aprovados=aprovado)

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Cores do tema IFMT
        verde_escuro = HexColor("#006400")
        verde_medio = HexColor("#228B22")
        verde_claro = HexColor("#E0F2E9")

        # Título
        p.setFont("Helvetica-Bold", 18)
        p.setFillColor(verde_escuro)
        p.drawString(100, 750, "COMPROVANTE DE MATRÍCULA")

        # Linha separadora
        p.setStrokeColor(verde_medio)
        p.line(100, 735, 500, 735)

        # Retângulo de fundo dos dados
        p.setFillColor(verde_claro)
        p.rect(90, 250, 420, 470, fill=True, stroke=False)

        # Dados do aluno
        p.setFillColorRGB(0, 0, 0)  # Cor do texto preta
        p.setFont("Helvetica", 12)
        y_position = 700

        dados = [
            f"Nome: {aprovado.name}",
            f"CPF: {aprovado.cpf}",
            f"Curso: {aprovado.curso}",
            f"Matrícula: {cadastro.matricula}",
            f"Email: {cadastro.email}",
            f"Telefone: {cadastro.telefone}",
            f"Escola: {cadastro.escola}",
            f"Endereço: {cadastro.endereco}",
            f"Cidade: {cadastro.cidade}",
        ]

        for dado in dados:
            p.drawString(100, y_position, dado)
            y_position -= 25

        # Rodapé
        p.setStrokeColor(verde_medio)
        p.line(100, y_position - 20, 500, y_position - 20)
        p.setFont("Helvetica-Oblique", 10)
        p.setFillColor(verde_escuro)
        p.drawString(100, y_position - 40, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprovante_matricula_{cadastro.matricula}.pdf"'
        return response

    except (Aprovado.DoesNotExist, Cadastro.DoesNotExist):
        return redirect('/ValidacaoAluno')
    
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
        telefone = request.POST.get("telefone", "")
        email = request.POST.get("email", "")
        nascimento = request.POST.get("nascimento", "")
        endereco = request.POST.get("endereco", "")
        cidade = request.POST.get("cidade", "")
        arquivo = request.FILES.get('arquivo', None)
        cpf_validado = request.session.get('cpf_validado')
        print(telefone)
    if escola and email and nascimento and endereco and cidade and arquivo and cpf_validado:
        try:
            aprovado = Aprovado.objects.get(cpf=cpf_validado)
            cadastro = Cadastro.objects.create(
                escola=escola,
                telefone=telefone,
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

        
def CentralAluno_view(request):
    from django.shortcuts import render, redirect
from .models import Aprovado, Cadastro

def CentralAluno_view(request):
    cpf = request.session.get('cpf_validado')

    if not cpf:
        return redirect('/ValidacaoAluno')  # se alguém tentar acessar direto

    try:
        aprovado = Aprovado.objects.get(cpf=cpf)
        cadastro = Cadastro.objects.get(aprovados=aprovado)

        context = {
            "nome": aprovado.name,
            "telefone": cadastro.telefone,
            "matricula": cadastro.matricula,
            "cpf":aprovado.cpf,
            "curso": aprovado.curso,
            "email": cadastro.email,
            "escola": cadastro.escola,
            "nascimento": cadastro.nascimento,
            "endereco": cadastro.endereco,
            "cidade": cadastro.cidade,
            "arquivo_url": cadastro.arquivo.url if cadastro.arquivo else None
        }

        return render(request, 'CentralAluno.html', context)

    except (Aprovado.DoesNotExist, Cadastro.DoesNotExist):
        return redirect('/ValidacaoAluno')  # fallback se algo estiver errado




def editar_perfil_view(request):
    cpf = request.session.get('cpf_validado')
    
    if not cpf:
        return redirect('/ValidacaoAluno')
    
    try:
        aprovado = Aprovado.objects.get(cpf=cpf)
        cadastro = Cadastro.objects.get(aprovados=aprovado)
        
        if request.method == 'GET':
            context = {
                "cadastro": cadastro,
                "aprovado": aprovado
            }
            return render(request, 'editar_perfil.html', context)
        
        elif request.method == 'POST':
            # Atualizar apenas campos editáveis
            cadastro.email = request.POST.get('email', cadastro.email)
            cadastro.telefone = request.POST.get('telefone', cadastro.telefone)
            cadastro.endereco = request.POST.get('endereco', cadastro.endereco)
            cadastro.cidade = request.POST.get('cidade', cadastro.cidade)
            cadastro.escola = request.POST.get('escola', cadastro.escola)
            
            cadastro.save()
            
            return redirect('/CentralAluno')
            
    except (Aprovado.DoesNotExist, Cadastro.DoesNotExist):
        return redirect('/ValidacaoAluno')

def ValidacaoAluno_view(request):
    if request.method == "GET":
        return render(request, 'ValidacaoAluno.html', {"aprovado": False})
    
    elif request.method == "POST":
        cpf = request.POST.get('cpf')
        print("CPF recebido:", cpf)

        try:
            aprovado = Aprovado.objects.get(cpf=cpf)

            # Verifica se há um Cadastro vinculado a esse Aprovado
            if Cadastro.objects.filter(aprovados=aprovado).exists():
                # Salva na sessão os dados
                request.session['cpf_validado'] = cpf
                request.session['nome_aprovado'] = aprovado.name
                request.session['curso_aprovado'] = aprovado.curso
                return redirect("/CentralAluno")
            else:
                # Está aprovado, mas ainda não fez matrícula
                return render(request, 'ValidacaoAluno.html', {"aprovado": True, "erro": "Aluno aprovado, mas ainda não realizou matrícula."})

        except Aprovado.DoesNotExist:
            # CPF não está nem aprovado
            return render(request, 'ValidacaoAluno.html', {"aprovado": True, "erro": "CPF não encontrado na lista de aprovados."})
    
    else:
        return HttpResponseBadRequest()