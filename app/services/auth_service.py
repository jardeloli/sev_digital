from django.core.exceptions import ValidationError
from ..models import Servidor

class AuthService:
    @staticmethod
    def login(email, senha):
        try:
            servidor = Servidor.objects.select_related('perfil').get(email=email)

        except Servidor.DoesNotExist:
            raise ValidationError("Credenciais inválidas")
        
        if not servidor.check_password(senha):
            raise ValidationError("Credenciais inválidas")
        
        return servidor
    