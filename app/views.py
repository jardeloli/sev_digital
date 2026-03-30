from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Servidor, Veiculo, RegistroSev, Servico

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
            user = Servidor.objects.get(email=email)

            if user.check_password(senha):
                request.session['user_id'] = user.siape
                return redirect('dashboard')
            else:
                messages.error(request, 'Senha inválida')

        except Servidor.DoesNotExist:
            messages.error(request, 'Usuário não encontrado')

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
        placa = request.POST.get('placa')
        modelo = request.POST.get('modelo')
        marca = request.POST.get('marca')
        ano = request.POST.get('ano')

        if not all([placa, modelo, marca, ano]):
            messages.error(request, 'Preencha todos os campos')
            return redirect('cadastrar_veiculo')

        if Veiculo.objects.filter(placa=placa).exists():
            messages.error(request, 'Veículo já cadastrado')
            return redirect('cadastrar_veiculo')

        Veiculo.objects.create(
            placa=placa,
            modelo=modelo,
            marca=marca,
            ano=ano
        )

        messages.success(request, 'Veículo cadastrado com sucesso')
        return redirect('lista_veiculos')

    return render(request, 'cadastrar_veiculo.html')


def lista_veiculos(request):
    if not usuario_logado(request):
        return redirect('login')

    veiculos = Veiculo.objects.all()
    return render(request, 'lista_veiculos.html', {'veiculos': veiculos})


def cadastrar_servidor(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        siape = request.POST.get('siape')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if not all([nome, siape, cpf, email, senha]):
            messages.error(request, 'Preencha todos os campos')
            return redirect('cadastrar_servidor')

        if Servidor.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado')
            return redirect('cadastrar_servidor')

        if Servidor.objects.filter(cpf=cpf).exists():
            messages.error(request, 'CPF já cadastrado')
            return redirect('cadastrar_servidor')

        servidor = Servidor(
            nome_servidor=nome,
            siape=siape,
            cpf=cpf,
            email=email,
            senha=senha,
            data_nascimento='2000-01-01',
            perfil_id=1
        )
        servidor.save()

        messages.success(request, 'Conta criada com sucesso')
        return redirect('login')

    return render(request, 'cadastrar_servidor.html')


def registrar_sev(request):
    if not usuario_logado(request):
        return redirect('login')

    servidores = Servidor.objects.all()
    veiculos = Veiculo.objects.all()
    servicos = Servico.objects.all()

    if request.method == 'POST':
        try:
            km_inicio = int(request.POST.get('km_inicio'))
            km_fim = int(request.POST.get('km_fim'))

            if km_fim < km_inicio:
                messages.error(request, 'KM final não pode ser menor que o inicial')
                return redirect('registrar_sev')

            RegistroSev.objects.create(
                servidor_id=request.POST.get('servidor'),
                veiculo_id=request.POST.get('veiculo'),
                servico_id=request.POST.get('servico'),
                origem=request.POST.get('origem'),
                destino=request.POST.get('destino'),
                data_inicio=request.POST.get('data_inicio'),
                data_fim=request.POST.get('data_fim'),
                km_inicio=km_inicio,
                km_fim=km_fim,
            )

            messages.success(request, 'Registro criado com sucesso')
            return redirect('lista_sev')

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

    registros = RegistroSev.objects.select_related('servidor', 'veiculo').all()
    return render(request, 'lista_sev.html', {'registros': registros})