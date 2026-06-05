from django.core.exceptions import ValidationError
from ..models import Servico, RegistroSev

class ServicoService:
    @staticmethod
    def criar_servico(nome_servico, descricao='', categoria='OUTROS',
    status='ATIVO'):

        if Servico.objects.filter(nome_servico=nome_servico).exists():
            raise ValidationError(f"Serviço com nome '{nome_servico}' já existe.")
        
        servico = Servico.objects.create(
            nome_servico = nome_servico,
            descricao = descricao,
            categoria=categoria,
            status=status
        )

        servico.save()
        return servico
    
    @staticmethod
    def deletar_servico(id_servico):

        try:

            servico = Servico.objects.get(
                pk=id_servico
            )

        except Servico.DoesNotExist:

            raise ValidationError(
                "Serviço não encontrado."
            )

        if RegistroSev.objects.filter(
            servico=servico
        ).exists():

            raise ValidationError(
                "Não é possível excluir este serviço porque ele possui registros vinculados."
            )

        servico.delete()

        return "Serviço excluído com sucesso."
    
    def listar_servicos():
        return Servico.objects.all()
    
    def buscar_servico(nome_servico):
        if not Servico.objects.filter(nome_servico=nome_servico).exists():
            raise ValidationError(f"Serviço com nome '{nome_servico}' não existe.") 
        
        return Servico.objects.get(nome_servico=nome_servico)
    
