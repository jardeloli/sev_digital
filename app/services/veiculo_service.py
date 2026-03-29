from django.core.exceptions import ValidationError
from ..models import Veiculo

class VeiculoService:
    @staticmethod
    def criar_veiculo(placa, modelo, marca, ano, km_total=0):

        if Veiculo.objects.filter(placa=placa).exists():
            raise ValidationError("Veículo com esta placa já existe.")
        
        veiculo = Veiculo.objects.create(
            placa = placa,
            modelo = modelo,
            marca = marca,
            ano = ano,
            km_total = km_total
        )

        veiculo.save()
        return veiculo
    
    def deletar_veiculo(placa):
        if not Veiculo.objects.filter(pk=placa).exists():
            raise ValidationError("Veículo com esta placa não existe.")
        
        Veiculo.objects.get(pk=placa).delete()

        return "Veículo deletado com sucesso."
    
    def listar_veiculos():
        return Veiculo.objects.all()
    
    def buscar_veiculo(placa):
        if not Veiculo.objects.filter(pk=placa).exists():
            raise ValidationError("Veículo com esta placa não existe.")
        
        return Veiculo.objects.get(pk=placa)