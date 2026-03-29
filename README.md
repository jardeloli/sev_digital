SEV Digital

Proposta do Sistema

O **SEV Digital** (Sistema de Controle de Serviço Externo de Veículos) tem como objetivo gerenciar e registrar o uso de veículos oficiais por servidores em atividades administrativas e de campo.

O sistema permite:
- Cadastro de servidores, veículos, serviços e perfis
- Registro de deslocamentos (SEV)
- Controle de quilometragem dos veículos
- Cálculo automático de KM rodado e horas trabalhadas

---

Roadmap de Desenvolvimento

Etapa 1 - Modelagem
- Levantamento de requisitos
- Criação do DER (Diagrama Entidade-Relacionamento)

Etapa 2 - Implementação Inicial
- Configuração do ambiente
- Criação do repositório
- Implementação dos models (Django ORM)
- Integração com banco de dados MySQL

Etapa 3 - Em andamento
- Implementação da lógica de negócio
- Validações de dados
- Criação de APIs (REST)
- Implementação de controllers/views

Etapa 4 - Futuro

- Interface gráfica (frontend)
- Testes automatizados

Equipe

- Jardel Santos
- Gustavo Noleto
- Miqueias do Nascimento
- Wallaci Araújo

Tecnologias Utilizadas

- Python
- Django
- MySQL
- Git/GitHub


Como configurar e executar o projeto:

 1 - Criar e ativar o ambiente virtual:
  
  - Criar ambiente: python -m venv venv
  - Ativar no Windows: venv\Scripts\activate
    
 2 - Instalar as dependências:
   - pip install -r requirements.txt

 3 - Configurar o banco de dados:
   No arquivo core/settings.py, configure a conexão com o MySQL:
         DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.mysql',
              'NAME': 'sev_digital',
              'USER': 'seu_usuario',
              'PASSWORD': 'sua_senha',
              'HOST': 'localhost',
              'PORT': '3306',
          }
        }
 4 - Crie o banco de dados no MySQL:
   - CREATE DATABASE sev_digital

 5 - Aplicar as migrations:
   - python manage.py migrate


Executar:




Paradigmas

Paradigma Orientado a Objetos (POO)
Toda a estrutura do projeto é construída sobre POO. Cada entidade do sistema — Servidor, Veiculo, RegistroSev, Perfil, Permissao e Servico — é representada como uma classe que herda de models.Model, encapsulando seus atributos e comportamentos:
  class Servidor(models.Model):
      siape = models.IntegerField(primary_key=True)
      nome_servidor = models.CharField(max_length=45)
      senha = models.CharField(max_length=255
      
As services também são classes, organizando os métodos de negócio de forma coesa e reutilizável por meio de @staticmethod, evitando a necessidade de instanciar objetos desnecessariamente.

Separação de Responsabilidades
O projeto aplica o princípio Single Responsibility separando explicitamente o que cada camada faz:

Model — calcula valores derivados dos próprios dados do objeto, como km_rodado() e horas_trabalhadas(), além de fazer o hash da senha no save() do Servidor
Service — orquestra operações que envolvem múltiplos models, como atualizar o km_total do veículo após a criação de um RegistroSev
View — recebe a requisição HTTP, chama o service correspondente e retorna a resposta ao usuário

Herança e Polimorfismo
Todas as models herdam de models.Model, aproveitando automaticamente métodos como save(), delete(), objects.all(), objects.get() e objects.filter(). Quando necessário, o método save() é sobrescrito (polimorfismo) para adicionar comportamento extra sem perder o comportamento original.

Paradigma Declarativo
A definição do banco de dados segue um estilo declarativo — em vez de escrever SQL manualmente, os campos e relacionamentos são declarados como atributos de classe, e o Django gera automaticamente as queries e migrations:

class RegistroSev(models.Model):
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    veiculo  = models.ForeignKey(Veiculo,  on_delete=models.CASCADE)
    servico  = models.ForeignKey(Servico,  on_delete=models.CASCADE)

