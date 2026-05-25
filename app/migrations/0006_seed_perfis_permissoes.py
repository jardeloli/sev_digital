from django.db import migrations


def seed_perfis_permissoes(apps, schema_editor):
    Perfil = apps.get_model('app', 'Perfil')
    Permissao = apps.get_model('app', 'Permissao')
    PerfilPermissao = apps.get_model('app', 'PerfilPermissao')

    permissoes = {
        'VISUALIZAR': 'Pode visualizar registros',
        'CADASTRAR': 'Pode realizar cadastros basicos',
        'EDITAR': 'Pode editar registros',
        'USUARIOS': 'Pode gerenciar usuarios',
    }

    permissoes_criadas = {}
    for nome, descricao in permissoes.items():
        permissao, _ = Permissao.objects.get_or_create(
            nome_permissao=nome,
            defaults={'descricao': descricao}
        )
        permissoes_criadas[nome] = permissao

    perfis = {
        'Servidor': {
            'descricao': 'Usuario operacional',
            'permissoes': ['VISUALIZAR', 'CADASTRAR'],
        },
        'Admin': {
            'descricao': 'Administrador do sistema',
            'permissoes': ['VISUALIZAR', 'CADASTRAR', 'EDITAR', 'USUARIOS'],
        },
    }

    for nome, dados in perfis.items():
        perfil, _ = Perfil.objects.get_or_create(
            nome_perfil=nome,
            defaults={'descricao': dados['descricao']}
        )

        for nome_permissao in dados['permissoes']:
            PerfilPermissao.objects.get_or_create(
                perfil=perfil,
                permissao=permissoes_criadas[nome_permissao]
            )


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_registrosev_data_fim_alter_registrosev_km_fim_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_perfis_permissoes, migrations.RunPython.noop),
    ]
