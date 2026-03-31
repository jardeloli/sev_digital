from django.core.exceptions import ValidationError
from ..models import Servidor, Perfil

class ServidorService:
    @staticmethod
    def criar_servidor(siape, nome, cpf, data_nascimento, email, senha, id_perfil):
        
        if Servidor.objects.filter(cpf=cpf).exists():
            raise ValidationError("CPF já existe.")
    
        if Servidor.objects.filter(email=email).exists():
            raise ValidationError("Email já existe.")
        
        perfil = Perfil.objects.get(pk=id_perfil)

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
    
    