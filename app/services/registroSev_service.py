from django.core.exceptions import ValidationError
from ..models import RegistroSev, Servidor, Veiculo, Servico

class RegistroSevService:
    @staticmethod
    def criar_registro_sev(siape, placa, id_servico, origem, data_inicio, km_inicio, detino, data_fim, km_fim):

        if km_fim <= km_inicio:
            raise ValidationError("A quilometragem final deve ser maior que a inicial.")
        if data_fim <= data_inicio:
            raise ValidationError("A data de fim deve ser posterior à data de início.")
        
        registro = RegistroSev.objects.create(
            servidor = Servidor.object.get(pk=siape),
            veiculo = Veiculo.objects.get(pk=placa),
            servico = Servico.objects.get(pk=id_servico),
            origem = origem,
            data_inicio = data_inicio,
            km_inicio = km_inicio,
            destino = detino,
            data_fim = data_fim,
            km_fim = km_fim
        )

        RegistroSevService.atualizar_km_total(registro)

        return registro

    @staticmethod
    def atualizar_km_total(registro):
        veiculo = registro.veiculo
        veiculo.km_total += registro.km_rodado()
        veiculo.save()

        return "Quilometragem total do veículo atualizada com sucesso."
    
    def listar_registros_sev():
        return RegistroSev.objects.all()
    
    def buscar_registro(id):
        if not RegistroSev.objects.filter(pk=id).exists():
            raise ValidationError(f"Registro não encontrado.")
        
        return RegistroSev.objects.get(pk=id)

        