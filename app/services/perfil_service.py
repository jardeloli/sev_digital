from django.core.exceptions import ValidationError
from ..models import Perfil

class PerfilService:
    @staticmethod
    def criar_perfil(nome, descricao=''):
        
        if not nome:
            raise ValidationError("O nome do perfil é obrigatório.")
        
        if Perfil.objects.filter(nome_perfil=nome).exists():
            raise ValidationError("Perfil com esse nome já existe.")
        
        perfil = Perfil.objects.create(
            nome_perfil=nome,
            descricao=descricao
        )

        perfil.save()

        return perfil
    
    def deletar_perfil(perfil_id):
        if not Perfil.objects.filter(id_perfil=perfil_id).exists():
            raise ValidationError("Perfil não encontrado.")
        
        Perfil.objects.filter(id_perfil=perfil_id).delete()

        return "Perfil deletado com sucesso."
    
    def listar_perfis():
        return Perfil.objects.all()
    
    def buscar_perfil(perfil_id):
        if not Perfil.objects.filter(id_perfil=perfil_id).exists():
            raise ValidationError("Perfil não encontrado.")
        
        return Perfil.objects.get(id_perfil=perfil_id)