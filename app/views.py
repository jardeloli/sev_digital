from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Servidor, Veiculo, RegistroSev, Servico, Perfil, Permissao, PerfilPermissao

from .services.auth_service import AuthService
from .services.veiculo_service import VeiculoService
from .services.servidor_service import ServidorService
from .services.registroSev_service import RegistroSevService
from .services.servico_service import ServicoService
from app.services.perfil_service import PerfilService

def usuario_logado(request):
    return request.session.get('user_id')


def usuario_atual(request):
    user_id = usuario_logado(request)

    if not user_id:
        return None

    return Servidor.objects.select_related('perfil').filter(siape=user_id).first()


def usuario_admin(request):
    usuario = usuario_atual(request)
    return usuario and usuario.perfil.nome_perfil == 'Admin'


def base_context(request, **extra):
    context = {'usuario': usuario_atual(request)}
    context.update(extra)
    return context


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

    return render(request, 'cadastrar_veiculo.html', base_context(request))


def lista_veiculos(request):
    if not usuario_logado(request):
        return redirect('login')

    veiculos = VeiculoService.listar_veiculos().order_by('placa')

    context = base_context(
        request,
        veiculos=veiculos,
        total_veiculos=veiculos.count(),
        total_ativos=Veiculo.objects.filter(status='ATIVO').count(),
        total_manutencao=Veiculo.objects.filter(status='MANUTENCAO').count(),
        total_em_uso=Veiculo.objects.filter(status='EM_USO').count()
    )

    return render(request, 'lista_veiculos.html', context)


def lista_servidores(request):
    if not usuario_logado(request):
        return redirect('login')

    servidores = Servidor.objects.select_related('perfil').order_by('nome_servidor')

    return render(
        request,
        'lista_servidores.html',
        base_context(request, servidores=servidores)
    )


def lista_servicos(request):
    if not usuario_logado(request):
        return redirect('login')

    servicos = ServicoService.listar_servicos().order_by('nome_servico')

    return render(
        request,
        'lista_servicos.html',
        base_context(request, servicos=servicos)
    )


def cadastrar_servico(request):
    if not usuario_logado(request):
        return redirect('login')

    if request.method == 'POST':
        try:
            ServicoService.criar_servico(
                nome_servico=request.POST.get('nome_servico'),
                descricao=request.POST.get('descricao')
            )

            messages.success(request, 'Serviço cadastrado com sucesso.')
            return redirect('lista_servicos')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'cadastrar_servico.html', base_context(request))


def cadastrar_servidor(request):
    primeiro_cadastro = not Servidor.objects.exists()

    if not primeiro_cadastro and not usuario_logado(request):
        return redirect('login')

    if not primeiro_cadastro and not usuario_admin(request):
        messages.error(request, 'Apenas administradores podem cadastrar servidores.')
        return redirect('dashboard')

    perfis = PerfilService.listar_perfis()

    if primeiro_cadastro:
        perfis = perfis.filter(nome_perfil='Admin')

    if request.method == 'POST':
        try:
            perfil_id = request.POST.get('perfil_id')

            if primeiro_cadastro:
                perfil_admin = Perfil.objects.filter(nome_perfil='Admin').first()

                if not perfil_admin:
                    raise ValidationError('Perfil Admin nao encontrado. Execute as migrations.')

                perfil_id = perfil_admin.id_perfil

            ServidorService.criar_servidor(
                siape=request.POST.get('siape'),
                nome=request.POST.get('nome'),
                cpf=request.POST.get('cpf'),
                data_nascimento=request.POST.get('dt_nasc'),
                email=request.POST.get('email'),
                senha=request.POST.get('senha'),
                id_perfil=perfil_id
            )

            messages.success(request, 'Conta criada com sucesso')
            return redirect('login' if primeiro_cadastro else 'dashboard')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'cadastrar_servidor.html', {
        'perfis': perfis,
        'primeiro_cadastro': primeiro_cadastro
    })


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
                local_ori=request.POST.get('local_ori'),
                data_inicio=request.POST.get('data_inicio'),
                km_inicio=request.POST.get('km_inicio'),
                destino=request.POST.get('destino'),
                local_dest=request.POST.get('local_dest'),
                data_fim=request.POST.get('data_fim'),
                km_fim=request.POST.get('km_fim'),
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
            Q(veiculo__placa__icontains=busca)|
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

    if not usuario_logado(request):
        return redirect('login')

    registro = RegistroSevService.buscar_registro(id)

    if request.method == 'POST':

        try:

            RegistroSevService.editar_registro(
                registro=registro,
                local_dest=request.POST.get('local_dest'),
                data_fim=request.POST.get('data_fim'),
                km_fim=request.POST.get('km_fim')
            )

            messages.success(
                request,
                'Registro atualizado com sucesso.'
            )

        except ValidationError as e:

            messages.error(
                request,
                e.message
            )

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

    if not usuario_logado(request):
        return redirect('login')

    RegistroSevService.cancelar_registro(id)

    messages.success(request, 'Registro cancelado com sucesso.')

    return redirect('lista_sev')


def cadastrar_perfil(request):

    if not usuario_logado(request):
        return redirect('login')

    if not usuario_admin(request):
        messages.error(request, 'Apenas administradores podem cadastrar perfis.')
        return redirect('dashboard')

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
    if not usuario_logado(request):
        return redirect('login')

    if not usuario_admin(request):
        messages.error(request, 'Apenas administradores podem visualizar perfis.')
        return redirect('dashboard')

    perfis = PerfilService.listar_perfis()

    return render(
        request,
        'lista_perfis.html',
        base_context(request, perfis=perfis)
    )


def lista_permissoes(request):
    if not usuario_logado(request):
        return redirect('login')

    if not usuario_admin(request):
        messages.error(request, 'Apenas administradores podem visualizar permissoes.')
        return redirect('dashboard')

    permissoes = Permissao.objects.all().order_by('nome_permissao')
    vinculos = PerfilPermissao.objects.select_related('perfil', 'permissao').order_by(
        'perfil__nome_perfil',
        'permissao__nome_permissao'
    )

    return render(
        request,
        'lista_permissoes.html',
        base_context(request, permissoes=permissoes, vinculos=vinculos)
    )


def editar_usuario(request):
    if not usuario_logado(request):
        return redirect('login')

    usuario = usuario_atual(request)

    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            cpf = request.POST.get('cpf')

            if Servidor.objects.exclude(pk=usuario.pk).filter(email=email).exists():
                raise ValidationError('Email ja existe.')

            if Servidor.objects.exclude(pk=usuario.pk).filter(cpf=cpf).exists():
                raise ValidationError('CPF ja existe.')

            usuario.nome_servidor = request.POST.get('nome')
            usuario.cpf = cpf
            usuario.email = email
            usuario.data_nascimento = ServidorService._parse_data_nascimento(
                request.POST.get('dt_nasc')
            )

            senha = request.POST.get('senha')
            if senha:
                usuario.set_password(senha)

            usuario.save()
            messages.success(request, 'Usuario atualizado com sucesso.')
            return redirect('meu_perfil')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(
        request,
        'editar_usuario.html',
        base_context(request)
    )


def meu_perfil(request):
    if not usuario_logado(request):
        return redirect('login')

    vinculos = PerfilPermissao.objects.select_related('permissao').filter(
        perfil=usuario_atual(request).perfil
    ).order_by('permissao__nome_permissao')

    return render(
        request,
        'meu_perfil.html',
        base_context(request, vinculos=vinculos)
    )
