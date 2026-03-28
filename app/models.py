from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Perfil(models.Model):
    id_perfil = models.SmallAutoField(primary_key=True)
    nome_perfil = models.CharField(max_length=10)
    descricao = models.CharField(max_length=45, blank=True)

    def __str__(self):
        return self.nome_perfil

class Permissao(models.Model):
    id_permissao = models.SmallAutoField(primary_key=True)
    nome_permissao = models.CharField(max_length=10)
    descricao = models.CharField(max_length=45, blank=True)

    def __str__(self):
        return self.nome_permissao
    
class PerfilPermissao(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    permissao = models.ForeignKey(Permissao, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.perfil.nome_perfil} - {self.permissao.nome_permissao}"
    
class Servidor(models.Model):
    siape = models.IntegerField(primary_key=True)
    nome_servidor = models.CharField(max_length=45)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    email = models.EmailField(max_length=45, unique=True)
    senha = models.CharField(max_length=255)
  

    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    #criptografa a senha
    def set_password(self, raw_password):
        self.senha = make_password(raw_password)

    #verifica a senha
    def check_password(self, raw_password):
        return check_password(raw_password, self.senha)
    
    #Salva o hash da senha
    def save(self, *args, **kwargs):
        if not self.senha.startswith('pbkdf2_sha256$'):
            self.set_password(self.senha)
        super().save(*args, **kwargs)

    #Retorna o nome do servidor 
    def __str__(self):
        return f"{self.nome_servidor} - {self.perfil}"

    
class Veiculo(models.Model):
    placa = models.CharField(max_length=7, primary_key=True)
    modelo = models.CharField(max_length=10)
    marca = models.CharField(max_length=15)
    ano = models.IntegerField()
    km_total = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"

class Servico(models.Model):
    id_servico = models.SmallAutoField(primary_key=True)
    nome_servico = models.CharField(max_length=25)
    descricao = models.CharField(max_length=45, blank=True)

    #Retorna o nome do serviço
    def __str__(self):
        return self.nome_servico

    
class RegistroSev(models.Model):
    id_sev = models.SmallAutoField(primary_key=True)
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)

    origem = models.CharField(max_length=25)
    data_inicio = models.DateTimeField()
    km_inicio = models.IntegerField()

    destino = models.CharField(max_length=25)
    data_fim = models.DateTimeField()
    km_fim = models.IntegerField()

    #Calcula a quilometragem rodada
    def km_rodado(self):
        return  self.km_fim - self.km_inicio
    
    #Sobrescreve o método save para atualizar o km_total do veículo quando um novo registro de serviço é criado
    def save(self, *args, **kwargs):
        eh_novo = self.pk is None
        super().save(*args, **kwargs)

        if eh_novo:
            self.atualizar_km_total()

    #Atualiza o km_total do veículo 
    def atualizar_km_total(self):
        veiculo = self.veiculo
        veiculo.km_total += self.km_rodado()
        veiculo.save()          

    #Calcula a quantidade de horas trabalhadas
    def horas_trabalhadas(self):
        return (self.data_fim - self.data_inicio).total_seconds() / 3600

    #Retorna uma string representando o registro de serviço
    def __str__(self):
        return f"Servidor: {self.servidor.nome_servidor} - {self.origem} para {self.destino}"
