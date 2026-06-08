from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q, Case, When, IntegerField
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count

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
    return usuario and usuario.perfil.nome_perfil == 'Administrador'

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



def dashboard(request):
    if not usuario_logado(request):
        return redirect('login')

    registros =  RegistroSevService.listar_registros_sev().annotate(
        ordem_status=Case(
            When(status='Aberto', then=0),
            When(status='Finalizado', then=1),
            When(status='Cancelado', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by(
        'ordem_status',
        '-data_inicio'   
    )[:10]

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




def lista_veiculos(request):

    if not usuario_logado(request):
        return redirect('login')
    
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')

    veiculos = VeiculoService.listar_veiculos().annotate(
        ordem_status=Case(
            When(status='ATIVO', then=0),
            When(status='EM USO', then=1),
            When(status='MANUTENCAO', then=2),
            When(status='INATIVO', then=3),
            default=4,
            output_field=IntegerField()
        ),

        qtd_abertos=Count(
            'registrosev',
            distinct=True,
            filter=Q(registrosev__status='ABERTO')
        ),

        qtd_registros=Count(
            'registrosev',
            distinct=True
        )
    ).order_by(
        'ordem_status',
        'placa'
    )

    if busca:

        veiculos = veiculos.filter(

            Q(placa__icontains=busca) |
            Q(marca__icontains=busca) |
            Q(modelo__icontains=busca)

        )

    if status:

        veiculos = veiculos.filter(
            status=status
        )

    
    paginator = Paginator(
        veiculos,
        15
    )

    page = request.GET.get(
        'page'
    )

    veiculos = paginator.get_page(
        page
    )

    context = base_context(
        request,
        veiculos=veiculos,
        busca=busca,
        status=status,
        total_veiculos=Veiculo.objects.count(),
        total_ativos=Veiculo.objects.filter(status='ATIVO').count(),
        total_manutencao=Veiculo.objects.filter(status='MANUTENCAO').count(),
        total_em_uso=Veiculo.objects.filter(status='EM_USO').count()
    )

    for v in veiculos:
        if v.placa == 'SJA5B81':
            print(v.placa, v.qtd_abertos)

    return render(request, 'lista_veiculos.html', context)

def lista_servidores(request):

    if not usuario_logado(request):
        return redirect('login')

    if not usuario_admin(request):
        return redirect('dashboard')
    
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')

    servidores = Servidor.objects.select_related(
        'perfil'
    )

    if busca:

        servidores = servidores.filter(

            Q(siape__icontains=busca) |
            Q(nome_servidor__icontains=busca) |
            Q(cpf__icontains=busca) 

        )

    if status:

        servidores = servidores.filter(
            status=status
        )

    servidores = servidores.order_by(
        'nome_servidor'
    )

    paginator = Paginator(
        servidores,
        15
    )

    page = request.GET.get('page')

    servidores = paginator.get_page(
        page
    )

    context = base_context(

        request,

        servidores=servidores,

        busca=busca,
        status=status,

        total_servidores=Servidor.objects.count(),

        total_ativos=Servidor.objects.filter(
            status='ATIVO'
        ).count(),

        total_afastados=Servidor.objects.filter(
            status='AFASTADO'
        ).count(),

        total_desligados=Servidor.objects.filter(
            status='DESLIGADO'
        ).count()

    )

    return render(
        request,
        'lista_servidores.html',
        context
    )

def lista_servicos(request):

    if not usuario_logado(request):
        return redirect('login')

    busca = request.GET.get(
        'busca',
        ''
    )

    categoria = request.GET.get(
        'categoria',
        ''
    )

    status = request.GET.get(
        'status',
        ''
    )

    servicos = ServicoService.listar_servicos().annotate(
        qtd_registros=Count('registrosev')
    )

    if busca:

        servicos = servicos.filter(
            nome_servico__icontains=busca
        )

    if categoria:

        servicos = servicos.filter(
            categoria=categoria
        )

    if status:

        servicos = servicos.filter(
            status=status
        )
    

    servicos = servicos.order_by(
        'nome_servico'
    )

    paginator = Paginator(
        servicos,
        15
    )

    page = request.GET.get(
        'page'
    )

    servicos = paginator.get_page(
        page
    )

    return render(
        request,
        'lista_servicos.html',
        base_context(
            request,
            servicos=servicos,
            busca=busca,
            categoria=categoria,
            status=status
        )
    )

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


    registros = registros.annotate(
        ordem_status=Case(
            When(status='ABERTO', then=0),
            When(status='FINALIZADO', then=1),
            When(status='CANCELADO', then=2),
            default=3,
            output_field=IntegerField()
        )
    ).order_by(
        'ordem_status',
        '-data_inicio'
    )


    paginator = Paginator(registros, 15)

    page = request.GET.get('page')

    registros = paginator.get_page(page)

    servidores = Servidor.objects.all()

    veiculos = Veiculo.objects.filter(
        status='ATIVO'
    )

    servicos = Servico.objects.all()

    context = base_context(

        request,

        registros=registros,

        servidores=servidores,
        veiculos=veiculos,
        servicos=servicos,

        busca=busca,
        status=status,

        data_inicio=data_inicio,
        data_fim=data_fim,

        filtro_local=filtro_local,
        cidade=cidade,

    )

    return render(
        request,
        'lista_sev.html',
        context
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




def cadastrar_servico(request):
    if not usuario_logado(request):
        return redirect('login')
    
    if not usuario_admin(request):
        return redirect('dashboard')

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
        perfis = perfis.filter(nome_perfil='Administrador')

    if request.method == 'POST':
        try:
            perfil_id = request.POST.get('perfil_id')

            if primeiro_cadastro:
                perfil_admin = Perfil.objects.filter(nome_perfil='Administrador').first()

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

            messages.success(request, 'Servidor cadastrado com sucesso')
            return redirect('lista_servidores')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'cadastrar_servidor.html', {
        'usuario': usuario_atual(request),
        'perfis': perfis,
        'primeiro_cadastro': primeiro_cadastro
    })

def cadastrar_veiculo(request):
    if not usuario_logado(request):
        return redirect('login')
    
    if not usuario_admin(request):
        return redirect('dashboard')

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

def registrar_sev(request):

    if not usuario_logado(request):
        return redirect('login')

    usuario = usuario_atual(request)

    servidores = ServidorService.listar_servidores()
    veiculos = Veiculo.objects.filter(status='ATIVO')
    servicos = ServicoService.listar_servicos()

    if request.method == 'POST':
        try:

            if usuario_admin(request):

                siape = request.POST.get('servidor')

            else:

                siape = usuario.siape

            RegistroSevService.criar_registro_sev(
                siape=siape,
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

            messages.success(
                request,
                'Registro criado com sucesso'
            )

            return redirect('lista_sev')

        except ValidationError as e:

            messages.error(
                request,
                e.message
            )

        except Exception:

            messages.error(
                request,
                'Erro ao registrar serviço'
            )

    return render(
        request,
        'registrar_sev.html',
        {
            'usuario': usuario,
            'servidores': servidores,
            'veiculos': veiculos,
            'servicos': servicos
        }
    )




def editar_registro(request, id):
    
    registro = get_object_or_404(
        RegistroSev,
        id_sev=id
    )
    usuario = usuario_atual(request)

    if (
        not usuario_admin(request)
        and registro.servidor.siape != usuario.siape
    ):

        messages.error(
            request,
            'Você só pode editar registros criados por você.'
        )

        return redirect('lista_sev')

    if registro.status == 'CANCELADO':

        messages.error(
            request,
            'Registros cancelados não podem ser alterados.'
        )

        return redirect('lista_sev')

    if (
        registro.status == 'FINALIZADO'
        and not usuario_admin(request)
    ):

        messages.error(
            request,
            'Apenas administradores podem cancelar registros finalizados.'
        )

        return redirect('lista_sev')
    
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
        
        agora = timezone.localtime()

        registro.data_fim = agora.replace(
            year=int(data_fim[:4]),
            month=int(data_fim[5:7]),
            day=int(data_fim[8:10])
        )

        registro.local_dest = local_dest
        registro.km_fim = km_fim

        registro.veiculo.km_total = int(km_fim)
        registro.status = 'FINALIZADO'
        
        registro.veiculo.status = 'ATIVO'
        registro.veiculo.save()

        registro.save()

        messages.success(
            request,
            'Registro finalizado com sucesso.'
        )

        return redirect('lista_sev')

    return redirect('lista_sev')

def editar_usuario(request):
    if not usuario_logado(request):
        return redirect('login')

    usuario = usuario_atual(request)

    context = {
        'usuario': usuario,
        'perfis': Perfil.objects.all()
    }

    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            cpf_com_masc = request.POST.get('cpf')
            cpf = cpf_com_masc.replace('.', '').replace('-', '')

            if Servidor.objects.exclude(pk=usuario.pk).filter(email=email).exists():
                raise ValidationError('Email já existe.')

            if Servidor.objects.exclude(pk=usuario.pk).filter(cpf=cpf).exists():
                raise ValidationError('CPF já existe.')

            
            usuario.nome_servidor = request.POST.get('nome')
            usuario.cpf = cpf
            usuario.email = email
            usuario.perfil_id = request.POST.get('perfil')
            usuario.status = request.POST.get('status')
            usuario.data_nascimento = ServidorService._parse_data_nascimento(
                request.POST.get('dt_nasc')
            )

            senha = request.POST.get('senha')
            if senha:
                usuario.set_password(senha)

            usuario.save()
            messages.success(request, 'Servidor atualizado com sucesso.')
            return redirect('lista_servidores')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(
        request,
        'editar_usuario.html',
        base_context(
            request,
            usuario=usuario,
            perfis=Perfil.objects.all()
        )
    )

def editar_servidor(request, siape):
    if not usuario_logado(request):
        return redirect('login')

    if not usuario_admin(request):
        return redirect('dashboard')
    
    usuario = get_object_or_404(
        Servidor,
        pk=siape
    )

    context = {
        'usuario': usuario,
        'perfis': Perfil.objects.all()
    }

    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            cpf_com_masc = request.POST.get('cpf')
            cpf = cpf_com_masc.replace('.', '').replace('-', '')

            if Servidor.objects.exclude(pk=usuario.pk).filter(email=email).exists():
                raise ValidationError('Email já existe.')

            if Servidor.objects.exclude(pk=usuario.pk).filter(cpf=cpf).exists():
                raise ValidationError('CPF já existe.')

            
            usuario.nome_servidor = request.POST.get('nome')
            usuario.cpf = cpf
            usuario.email = email
            usuario.perfil_id = request.POST.get('perfil')
            usuario.status = request.POST.get('status')
            usuario.data_nascimento = ServidorService._parse_data_nascimento(
                request.POST.get('dt_nasc')
            )

            senha = request.POST.get('senha')
            if senha:
                usuario.set_password(senha)

            usuario.save()
            messages.success(request, 'Servidor atualizado com sucesso.')
            return redirect('lista_servidores')

        except ValidationError as e:
            messages.error(request, e.message)

    return render(
        request,
        'editar_usuario.html',
        base_context(
            request,
            usuario=usuario,
            perfis=Perfil.objects.all()
        )
    )

def editar_servico(request, id):

    if not usuario_logado(request):
        return redirect('login')
    
    if not usuario_admin(request):
        return redirect('dashboard')

    servico = get_object_or_404(
        Servico,
        pk=id
    )

    if request.method == 'POST':

        try:

            nome_servico = request.POST.get(
                'nome_servico'
            )

            if Servico.objects.exclude(
                pk=servico.pk
            ).filter(
                nome_servico=nome_servico
            ).exists():

                raise ValidationError(
                    'Já existe um serviço com esse nome.'
                )

            servico.nome_servico = nome_servico
            servico.descricao = request.POST.get(
                'descricao'
            )

            servico.categoria = request.POST.get(
                'categoria'
            )

            novo_status = request.POST.get(
                'status'
            )

            if novo_status == 'INATIVO':

                possui_registros_abertos = RegistroSev.objects.filter(
                    servico=servico,
                    status='ABERTO'
                ).exists()

                if possui_registros_abertos:

                    raise ValidationError(
                        'Não é possível inativar um serviço que possui registros em aberto.'
                    )

            servico.status = novo_status

            servico.status = request.POST.get(
                'status'
            )

            servico.save()

            messages.success(
                request,
                'Serviço atualizado com sucesso.'
            )

            return redirect(
                'lista_servicos'
            )

        except ValidationError as e:

            messages.error(
                request,
                e.message
            )

    return render(

        request,

        'editar_servico.html',

        base_context(

            request,

            servico=servico

        )

    )

def editar_veiculo(request, placa):

    if not usuario_logado(request):
        return redirect('login')

    if not usuario_admin(request):
        return redirect('dashboard')
    
    veiculo = get_object_or_404(
        Veiculo,
        pk=placa
    )

    if request.method == 'POST':

        try:

            veiculo.marca = request.POST.get('marca')
            veiculo.modelo = request.POST.get('modelo')
            veiculo.ano = request.POST.get('ano')
            veiculo.km_total = request.POST.get('km_total')
            veiculo.status = request.POST.get('status')

            veiculo.save()

            messages.success(
                request,
                'Veículo atualizado com sucesso.'
            )

            return redirect(
                'lista_veiculos'
            )

        except ValidationError as e:

            messages.error(
                request,
                e.message
            )

    return render(
        request,
        'editar_veiculo.html',
        base_context(
            request,
            veiculo=veiculo
        )
    )



def deletar_veiculo(request, placa):

    if not usuario_logado(request):
        return redirect('login')

    if not usuario_admin(request):
        return redirect('dashboard')
    try:

        VeiculoService.deletar_veiculo(
            placa
        )

        messages.success(
            request,
            'Veículo excluído com sucesso.'
        )

    except ValidationError as e:

        messages.error(
            request,
            e.message
        )

    return redirect(
        'lista_veiculos'
    )

def deletar_servico(request, id):

    if not usuario_logado(request):
        return redirect('login')
    
    if not usuario_admin(request):
        return redirect('dashboard')

    if request.method == 'POST':

        try:

            ServicoService.deletar_servico(id)

            messages.success(
                request,
                'Serviço excluído com sucesso.'
            )

        except ValidationError as e:

            messages.error(
                request,
                e.message
            )

    return redirect('lista_servicos')

def cancelar_sev(request, id):

    registro = get_object_or_404(
        RegistroSev,
        id_sev=id
    )

    usuario = usuario_atual(request)

    if (
        not usuario_admin(request)
        and registro.servidor.siape != usuario.siape
    ):

        messages.error(
            request,
            'Você só pode cancelar registros criados por você.'
        )

        return redirect('lista_sev')
    
    if registro.status == 'CANCELADO':

        messages.error(
            request,
            'Registros cancelados não podem ser alterados.'
        )

        return redirect('lista_sev')

    if (
        registro.status == 'FINALIZADO'
        and not usuario_admin(request)
    ):

        messages.error(
            request,
            'Apenas administradores podem cancelar registros finalizados.'
        )

        return redirect('lista_sev')

    if request.method == 'POST':

        motivo = request.POST.get(
            'motivo_cancelamento',
            ''
        ).strip()

        if len(motivo) < 15:

            messages.error(
                request,
                'O motivo deve ter pelo menos 15 caracteres.'
            )

            return redirect('lista_sev')

        registro.status = 'CANCELADO'
        registro.motivo_cancelamento = motivo

        registro.save()

        registro.veiculo.status = 'ATIVO'
        registro.veiculo.save()

        messages.success(
            request,
            'Registro cancelado com sucesso.'
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








