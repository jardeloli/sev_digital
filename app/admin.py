from django.contrib import admin
from .models import Perfil, Permissao, PerfilPermissao, Servidor, Veiculo, Servico, RegistroSev

admin.site.register(Perfil)
admin.site.register(Permissao)
admin.site.register(PerfilPermissao)
admin.site.register(Servidor)
admin.site.register(Veiculo)
admin.site.register(Servico)
admin.site.register(RegistroSev)