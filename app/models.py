from django.db import models

class Perfil(models.Models):
    id_perfil = models.SmallAutoField(primary_key=True)
    nome_perfil = models.CharField(max_length=10)
    descricao = models.CharField(max_length=45, blank=True)

    def __str__(self):
        return self.nome_perfil

class Permissao(models.Models):
    id_permissao = models.SmallAutoField(primary_key=True)
    nome_permissao = models.CharField(max_length=10)
    descricao = models.CharField(max_length=45, blank=True)

    def __str__(self):
        return self.nome_permissao
    
class PerfilPermissao(models.Models):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    permissao = models.ForeignKey(Permissao, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.perfil.nome_perfil} - {self.permissao.nome_permissao}"
    
class Servidor(models.Models):
    siape = models.IntegerField(primary_key=True)
    nome_servidor = models.CharField(max_length=45)
    cpf = models.CharField(max_length=11)
    data_nascimento = models.DateField()
    email = models.EmailField(max_length=45, unique=True)
    senha = models.CharField(max_length=255)
  

    perfil_id = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome_servidor
    
class Veiculo(models.Models):
    placa = models.CharField(max_length=7, primary_key=True)
    modelo = models.CharField(max_length=10)
    marca = models.CharField(max_length=15)
    ano = models.YearField()
    km_total = models.IntegerField()


class Servico(models.Models):
    id_servico = models.SmallAutoField(primary_key=True)
    nome_servico = models.CharField(max_length=25)
    descricao = models.CharField(max_length=45, blank=True)

    def __str__(self):
        return self.nome_servico

    
class RegistroSev(models.Models):
    id_sev = models.SmallAutoField(primary_key=True)
    id_servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    id_veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    id_servico = models.ForeignKey(Servico, on_delete=models.CASCADE)

    origem = models.CharField(max_length=25)
    data_inicio = models.DateTimeField()
    km_inicio = models.IntegerField()

    destino = models.CharField(max_length=25)
    data_fim = models.DateTimeField()
    km_fim = models.IntegerField()

    def km_rodado(self):
        return  self.km_fim - self.km_inicio
    
    def save(self, *args, **kwargs):
        eh_novo = self.pk is None
        super().save(*args, **kwargs)

        if eh_novo:
            self.atualizar_km_total()

    def atualizar_km_total(self):
        veiculo = self.id_veiculo
        veiculo.km_total += self.km_rodado()
        veiculo.save()          

    def horas_trabalhadas(self):
        return (self.data_fim - self.data_inicio).total_seconds() / 3600

    def __str__(self):
        return f"Servidor: {self.id_sev} - {self.origem} para {self.destino}"
