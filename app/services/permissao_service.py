from django.core.exceptions import ValidationError
from ..models import Permissao, PerfilPermissao, Perfil

class PermissaoService:
    @staticmethod
    def criar_permissao(nome, descricao=''):

        if not nome:
            raise ValidationError("O nome da permissão é obrigatório.")
        
        if Permissao.objects.filter(nome_permissao=nome).exists():
            raise ValidationError("Permissão com esse nome já existe.")
        
        permissao = Permissao.objects.create(
            nome_permissao=nome,
            descricao=descricao
        )

        permissao.save()

        return permissao
    
    def deletar_permissao(permissao_id):
        if not Permissao.objects.filter(id_permissao=permissao_id).exists():
            raise ValidationError("Permissão não encontrada.")
        
        Permissao.objects.get(pk=permissao_id).delete()

        return "Permissão deletada com sucesso."
    
    def listar_permissoes():
        return Permissao.objects.all()
    
    def buscar_permissao(permissao_id):
        if not Permissao.objects.filter(id_permissao=permissao_id).exists():
            raise ValidationError("Permissão não encontrada.")
        
        return Permissao.objects.get(pk=permissao_id)
    
    def associar_permissao_perfil(permissao_id, perfil_id):
        if not Permissao.objects.filter(id_permissao=permissao_id).exists():
            raise ValidationError("Permissão não encontrada.")
        
        if not Perfil.objects.filter(id_perfil=perfil_id).exists():
            raise ValidationError("Perfil não encontrado.")
        
        perfil = Perfil.objects.get(pk=perfil_id)
        permissao = Permissao.objects.get(pk=permissao_id)

        if PerfilPermissao.objects.filter(id_perfil=perfil, id_permissao=permissao).exists():
            raise ValidationError("Permissão já associada ao perfil.")
        
        perfil_permissao = PerfilPermissao.objects.create(
            id_perfil=perfil,
            id_permissao=permissao
        )

        perfil_permissao.save()

        return "Permissão associada ao perfil com sucesso."
    
    def desassociar_permissao_perfil(permissao_id, perfil_id):
        if not Permissao.objects.filter(id_permissao=permissao_id).exists():
            raise ValidationError("Permissão não encontrada.")
        
        if not Perfil.objects.filter(id_perfil=perfil_id).exists():
            raise ValidationError("Perfil não encontrado.")
        
        perfil = Perfil.objects.get(pk=perfil_id)
        permissao = Permissao.objects.get(pk=permissao_id)

        if not PerfilPermissao.objects.filter(id_perfil=perfil, id_permissao=permissao).exists():
            raise ValidationError("Permissão não associada ao perfil.")
        
        PerfilPermissao.objects.filter(id_perfil=perfil, id_permissao=permissao).delete()

        return "Permissão desassociada do perfil com sucesso."