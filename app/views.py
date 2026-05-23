from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Servidor, Veiculo, RegistroSev, Servico

from .services.auth_service import AuthService
from .services.veiculo_service import VeiculoService
from .services.servidor_service import ServidorService
from .services.registroSev_service import RegistroSevService
from .services.servico_service import ServicoService
from app.services.perfil_service import PerfilService

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

    registros = RegistroSev.objects.filter(status='ABERTO').order_by('-data_inicio')[:10]

    usuario = Servidor.objects.select_related(
        'perfil'
    ).get(
        siape=request.session['user_id']
    )

    context = {

        # cards
        'total_veiculos': Veiculo.objects.filter(status='ATIVO').count(),
        'total_servidores': Servidor.objects.filter(status='ATIVO').count(),
        'total_registros': RegistroSev.objects.filter(status='ABERTO').count(),


        'usuario': usuario,

        # tabela
        'registros': registros,

        # badge "abertos"
        'registros_abertos': RegistroSev.objects.filter(
            data_fim__isnull=False
        ).count()
    }

    return render(request, 'dashboard.html', context)


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
                data_nascimento=request.POST.get('dt_nasc'),
                email=request.POST.get('email'),
                senha=request.POST.get('senha'),
                id_perfil=request.POST.get('perfil_id')
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

    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')

    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    filtro_local = request.GET.get('filtro_local', '')
    cidade = request.GET.get('cidade', '')

    registros = RegistroSev.objects.all()

    
    if busca:

        registros = registros.filter(

            Q(servidor__nome_servidor__icontains=busca) |
            Q(veiculo__placa__icontains=busca) |
            Q(servico__nome_servico__icontains=busca)

        )

   
    if status:

        registros = registros.filter(
            status=status
        )

    if data_inicio and data_fim:

        registros = registros.filter(
            data_inicio__date__range=[data_inicio, data_fim]
        )

    if filtro_local and cidade:

        if filtro_local == 'origem':

            registros = registros.filter(
                local_ori__icontains=cidade
            )

        elif filtro_local == 'destino':

            registros = registros.filter(
                local_dest__icontains=cidade
            )


    registros = registros.order_by('-data_inicio')


    paginator = Paginator(registros, 15)

    page = request.GET.get('page')

    registros = paginator.get_page(page)

    context = {

        'registros': registros,

        'busca': busca,
        'status': status,

        'data_inicio': data_inicio,
        'data_fim': data_fim,

        'filtro_local': filtro_local,
        'cidade': cidade,

    }

    return render(request, 'lista_sev.html', context)

def editar_registro(request, id):

    registro = get_object_or_404(
        RegistroSev,
        id_sev=id
    )

    if request.method == 'POST':

        local_dest = request.POST.get('local_dest')
        data_fim = request.POST.get('data_fim')
        km_fim = request.POST.get('km_fim')


        if not local_dest or not data_fim or not km_fim:

            messages.error(
                request,
                'Preencha todos os campos.'
            )

            return redirect('lista_sev')

        if int(km_fim) <= int(registro.km_inicio):

            messages.error(
                request,
                'KM final deve ser maior que KM inicial.'
            )

            return redirect('lista_sev')

        registro.local_dest = local_dest
        registro.data_fim = data_fim
        registro.km_fim = km_fim


        registro.status = 'FINALIZADO'

        registro.save()

        messages.success(
            request,
            'Registro finalizado com sucesso.'
        )

        return redirect('lista_sev')

    return redirect('lista_sev')

def finalizar_sev(request, id):

    if not usuario_logado(request):
        return redirect('login')
    
    registro = RegistroSev.objects.get(pk=id)

    if not registro.destino or not registro.local_dest or not registro.data_fim or not registro.km_fim:
        raise ValidationError("Preencha todos os campos antes de finalizar.")

    RegistroSevService.finalizar_registro(id)

    messages.success(request, 'Registro finalizado com sucesso.')

    return redirect('lista_sev')


def cancelar_sev(request, id):

    registro = get_object_or_404(
        RegistroSev,
        id_sev=id
    )

    if request.method == 'POST':

        motivo = request.POST.get(
            'motivo_cancelamento',
            ''
        ).strip()

        # mínimo 15 caracteres

        if len(motivo) < 15:

            messages.error(
                request,
                'O motivo deve ter pelo menos 15 caracteres.'
            )

            return redirect('lista_sev')

        registro.status = 'CANCELADO'

        registro.motivo_cancelamento = motivo

        registro.save()

        messages.success(
            request,
            'Registro cancelado com sucesso.'
        )

    return redirect('lista_sev')


def cadastrar_perfil(request):

    if not usuario_logado(request):
        return redirect('login')

    if request.method == 'POST':

        try:

            PerfilService.criar_perfil(
                nome=request.POST.get('nome_perfil'),
                descricao=request.POST.get('descricao')
            )

            messages.success(
                request,
                'Perfil cadastrado com sucesso.'
            )

            return redirect('lista_perfis')

        except ValidationError as e:

            messages.error(request, e.message)

        except Exception as e:

            print(e)

            messages.error(
                request,
                'Erro ao cadastrar perfil.'
            )

    return render(
        request,
        'cadastrar_perfil.html'
    )

def lista_perfis(request):

    perfis = PerfilService.listar_perfis()

    return render(
        request,
        'lista_perfis.html',
        {'perfis': perfis}
    )