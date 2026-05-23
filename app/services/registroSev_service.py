from django.core.exceptions import ValidationError
from datetime import datetime
from ..models import RegistroSev, Servidor, Veiculo, Servico


class RegistroSevService:
    @staticmethod
    def criar_registro_sev(siape, placa, id_servico, origem,local_ori, data_inicio, km_inicio, detino,local_dest, data_fim, km_fim):

        if km_fim <= km_inicio:
            raise ValidationError("A quilometragem final deve ser maior que a inicial.")
        if data_fim <= data_inicio:
            raise ValidationError("A data de fim deve ser posterior à data de início.")
        
        registro = RegistroSev.objects.create(
            servidor = Servidor.object.get(pk=siape),
            veiculo = Veiculo.objects.get(pk=placa),
            servico = Servico.objects.get(pk=id_servico),
            origem = origem,
            local_ori = local_ori,
            data_inicio = data_inicio,
            km_inicio = km_inicio,
            destino = detino,
            local_dest = local_dest,
            data_fim = data_fim,
            km_fim = km_fim
        )

        RegistroSevService.atualizar_km_total(registro)

        return registro
    
    

    @staticmethod
    def editar_registro(registro, local_dest, data_fim, km_fim):

        # VALIDAÇÕES

        if not local_dest:
            raise ValidationError(
                "Preencha o Local Destino."
            )

        if not data_fim:
            raise ValidationError(
                "Preencha a Data Fim."
            )

        if not km_fim:
            raise ValidationError(
                "Preencha o KM Fim."
            )

        # ATRIBUIÇÕES

        registro.local_dest = local_dest

        registro.data_fim = datetime.strptime(
            data_fim,
            '%Y-%m-%d'
        )

        registro.km_fim = km_fim

        registro.save()

        return registro
    
    @staticmethod
    def finalizar_registro(id):

        registro = RegistroSev.objects.get(pk=id)

        registro.status = 'FINALIZADO'

        registro.save()

        return registro


    @staticmethod
    def cancelar_registro(id):

        registro = RegistroSev.objects.get(pk=id)

        registro.status = 'CANCELADO'

        registro.save()

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

        