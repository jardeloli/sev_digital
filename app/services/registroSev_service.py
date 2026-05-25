from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from ..models import RegistroSev, Servidor, Veiculo, Servico


class RegistroSevService:
    @staticmethod
    def criar_registro_sev(
        siape,
        placa,
        id_servico,
        origem,
        local_ori,
        data_inicio,
        km_inicio,
        destino,
        local_dest='',
        data_fim=None,
        km_fim=None
    ):
        data_inicio = RegistroSevService._parse_datetime(data_inicio, "data de inicio")
        data_fim = RegistroSevService._parse_datetime(data_fim, "data de fim", required=False)
        km_inicio = RegistroSevService._parse_int(km_inicio, "KM inicial")
        km_fim = RegistroSevService._parse_int(km_fim, "KM final", required=False)

        if km_fim is not None and km_fim <= km_inicio:
            raise ValidationError("A quilometragem final deve ser maior que a inicial.")

        if data_fim and data_fim <= data_inicio:
            raise ValidationError("A data de fim deve ser posterior a data de inicio.")

        registro = RegistroSev.objects.create(
            servidor=Servidor.objects.get(pk=siape),
            veiculo=Veiculo.objects.get(pk=placa),
            servico=Servico.objects.get(pk=id_servico),
            origem=origem,
            local_ori=local_ori or '',
            data_inicio=data_inicio,
            km_inicio=km_inicio,
            destino=destino,
            local_dest=local_dest or '',
            data_fim=data_fim,
            km_fim=km_fim
        )

        if km_fim is not None:
            RegistroSevService.atualizar_km_total(registro)

        return registro

    @staticmethod
    def editar_registro(registro, local_dest, data_fim, km_fim):
        if not local_dest:
            raise ValidationError("Preencha o Local Destino.")

        data_fim = RegistroSevService._parse_datetime(data_fim, "data de fim")
        km_fim = RegistroSevService._parse_int(km_fim, "KM final")

        if km_fim <= registro.km_inicio:
            raise ValidationError("A quilometragem final deve ser maior que a inicial.")

        if data_fim <= registro.data_inicio:
            raise ValidationError("A data de fim deve ser posterior a data de inicio.")

        km_rodado_anterior = registro.km_rodado()

        registro.local_dest = local_dest
        registro.data_fim = data_fim
        registro.km_fim = km_fim
        registro.save()

        diferenca_km = registro.km_rodado() - km_rodado_anterior
        registro.veiculo.km_total += diferenca_km
        registro.veiculo.save()

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

        return "Quilometragem total do veiculo atualizada com sucesso."

    @staticmethod
    def listar_registros_sev():
        return RegistroSev.objects.all()

    @staticmethod
    def buscar_registro(id):
        if not RegistroSev.objects.filter(pk=id).exists():
            raise ValidationError("Registro nao encontrado.")

        return RegistroSev.objects.get(pk=id)

    @staticmethod
    def _parse_datetime(value, field_name, required=True):
        if not value:
            if required:
                raise ValidationError(f"Informe uma {field_name} valida.")
            return None

        parsed = parse_datetime(value) if isinstance(value, str) else value

        if not parsed and isinstance(value, str):
            try:
                parsed = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                parsed = None

        if not parsed:
            raise ValidationError(f"Informe uma {field_name} valida.")

        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed)

        return parsed

    @staticmethod
    def _parse_int(value, field_name, required=True):
        if value in (None, ''):
            if required:
                raise ValidationError(f"Informe o {field_name}.")
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError(f"Informe um valor valido para {field_name}.")
