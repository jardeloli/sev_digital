from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from ..models import Servidor, Perfil

class ServidorService:
    @staticmethod
    def criar_servidor(siape, nome, cpf, data_nascimento, email, senha, id_perfil):
        if not all([siape, nome, cpf, data_nascimento, email, senha, id_perfil]):
            raise ValidationError("Preencha todos os campos obrigatorios.")

        data_nascimento = ServidorService._parse_data_nascimento(data_nascimento)

        if Servidor.objects.filter(siape=siape).exists():
            raise ValidationError("SIAPE ja existe.")

        if Servidor.objects.filter(cpf=cpf).exists():
            raise ValidationError("CPF já existe.")
    
        if Servidor.objects.filter(email=email).exists():
            raise ValidationError("Email já existe.")
        
        try:
            perfil = Perfil.objects.get(pk=id_perfil)
        except Perfil.DoesNotExist:
            raise ValidationError("Perfil nao encontrado.")

        servidor = Servidor.objects.create(
            siape = siape,
            nome_servidor = nome,
            cpf = cpf,
            data_nascimento = data_nascimento,
            email = email,
            senha = senha,
            perfil = perfil
        )

        

        return servidor

    @staticmethod
    def _parse_data_nascimento(value):
        data = parse_date(value)

        if data:
            return data

        try:
            from datetime import datetime
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValidationError("Data de nascimento invalida. Use o formato YYYY-MM-DD ou DD/MM/YYYY.")
    
    @staticmethod
    def deletar_servidor(siape):
       if not Servidor.objects.filter(siape=siape).exists():
            raise ValidationError("Servidor não encontrado.")
       
       Servidor.objects.get(pk=siape).delete()

       return "Servidor deletado com sucesso."
    
    @staticmethod
    def listar_servidores():
        return Servidor.objects.all()
    
    @staticmethod
    def buscar_servidor(siape):
        if not Servidor.objects.filter(siape=siape).exists():
            raise ValidationError("Servidor não encontrado.")
        
        return Servidor.objects.get(pk=siape)
    
    
