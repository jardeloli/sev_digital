from django.core.exceptions import ValidationError
from ..models import Servico

class ServicoService:
    @staticmethod
    def criar_servico(nome_servico, descricao=''):

        if Servico.objects.filter(nome_servico=nome_servico).exists():
            raise ValidationError(f"Serviço com nome '{nome_servico}' já existe.")
        
        servico = Servico.objects.create(
            nome_servico = nome_servico,
            descricao = descricao
        )

        servico.save()
        return servico
    
    def deletar_servico(nome_servico):
        if not Servico.objects.filter(pk=nome_servico).exists():
            raise ValidationError(f"Serviço com nome '{nome_servico}' não existe.")
        
        Servico.objects.get(pk=nome_servico).delete()

        return "Serviço deletado com sucesso."
    
    def listar_servicos():
        return Servico.objects.all()
    
    def buscar_servico(nome_servico):
        if not Servico.objects.filter(pk=nome_servico).exists():
            raise ValidationError(f"Serviço com nome '{nome_servico}' não existe.") 
        
        return Servico.objects.get(pk=nome_servico)
    