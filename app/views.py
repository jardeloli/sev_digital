from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Servidor, Veiculo, RegistroSev, Servico

from .services.auth_service import AuthService
from .services.veiculo_service import VeiculoService
from .services.servidor_service import ServidorService
from .services.registroSev_service import RegistroSevService
from .services.servico_service import ServicoService


def usuario_logado(request):
    return request.session.get('user_id')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if not email or not senha:
            messages.error(request, 'Preencha todos os campos')
            return redirect('login')

        try:
            user = AuthService.login(email, senha)
            request.session['user_id'] = user.siape
            return redirect('dashboard')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def dashboard(request):
    if not usuario_logado(request):
        return redirect('login')

    return render(request, 'dashboard.html')


def cadastrar_veiculo(request):
    if not usuario_logado(request):
        return redirect('login')

    if request.method == 'POST':
        try:
            VeiculoService.criar_veiculo(
                placa=request.POST.get('placa'),
                modelo=request.POST.get('modelo'),
                marca=request.POST.get('marca'),
                ano=request.POST.get('ano')
            )

            messages.success(request, 'Veículo cadastrado com sucesso')
            return redirect('lista_veiculos')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'cadastrar_veiculo.html')


def lista_veiculos(request):
    if not usuario_logado(request):
        return redirect('login')

    veiculos = VeiculoService.listar_veiculos()
    return render(request, 'lista_veiculos.html', {'veiculos': veiculos})


def cadastrar_servidor(request):
    if request.method == 'POST':
        try:
            ServidorService.criar_servidor(
                siape=request.POST.get('siape'),
                nome=request.POST.get('nome'),
                cpf=request.POST.get('cpf'),
                data_nascimento='2000-01-01',
                email=request.POST.get('email'),
                senha=request.POST.get('senha'),
                id_perfil=1
            )

            messages.success(request, 'Conta criada com sucesso')
            return redirect('login')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'cadastrar_servidor.html')


def registrar_sev(request):
    if not usuario_logado(request):
        return redirect('login')

    servidores = ServidorService.listar_servidores()
    veiculos = VeiculoService.listar_veiculos()
    servicos = ServicoService.listar_servicos()

    if request.method == 'POST':
        try:
            RegistroSevService.criar_registro_sev(
                siape=request.POST.get('servidor'),
                placa=request.POST.get('veiculo'),
                id_servico=request.POST.get('servico'),
                origem=request.POST.get('origem'),
                data_inicio=request.POST.get('data_inicio'),
                km_inicio=int(request.POST.get('km_inicio')),
                detino=request.POST.get('destino'),
                data_fim=request.POST.get('data_fim'),
                km_fim=int(request.POST.get('km_fim')),
            )

            messages.success(request, 'Registro criado com sucesso')
            return redirect('lista_sev')

        except ValidationError as e:
            messages.error(request, e.message)
        except Exception:
            messages.error(request, 'Erro ao registrar serviço')

    return render(request, 'registrar_sev.html', {
        'servidores': servidores,
        'veiculos': veiculos,
        'servicos': servicos
    })


def lista_sev(request):
    if not usuario_logado(request):
        return redirect('login')

    registros = RegistroSevService.listar_registros_sev()
    return render(request, 'lista_sev.html', {'registros': registros})