# Descrição

Esse projeto é uma API, com o objetivo de ser integrado a sistemas de educação, relacionados a aplicações de questionários.

Com as configurações e acessos necessários, essa API é capaz de receber informações sobre testes realizados com estudantes e construir um Feedback Formativo individual que será enviado ao e-mail indicando, com informações como justificativas em questões diferentes do gabarito e indicar possíveis pontos de aperfeiçoamento.

Além disso, é capaz de armazenar as informações sobre os questionários na sua base de dados, sendo possível solicitar um relatório em excel que será enviado para o professor da disciplina relacionada ao questionário.

# Execução

Esse vídeo é uma demonstração e tutorial de como utilizar o projeto FeedFor: [Link para o Vídeo](https://youtu.be/KL6FrNapAPk)

# Como Rodar

Para rodar a aplicação primeiro precisa ser configurado o `.env` na raiz do projeto:

```
# EMAIL CREDENTIALS
EMAIL_HOST_USER=youremail@hotmail.com
EMAIL_HOST_PASSWORD=yourpassword
```

Acima está um exemplo de `.env` que armazena as configurações das credenciais do serviço de e-mail e do banco de dados local. As credenciais do serviço de e-mail servem para conseguirmos enviar um e-mail com o Feedback Formativo dos alunos ou os relatórios para professores. As configurações do banco de dados são usadas na inicialização do projeto para identificar um serviço de armazenamento de dados que será usado, se o desejado for local, pode ser copiado e colados as configurações, caso o objetivo seja conectar com algum serviço externo como um banco de dados na nuvem por exemplo, é necessário recuperar as informações desse serviço e preencher nos campos corretamente.

Após configurar o `.env` da aplicação, basta rodar o comando `docker-compose up -d` para inicializar o projeto, sendo o `-d` opcional para evitar a lotação do terminal com informações desnecessárias (requisito mínimo seria ter uma máquina que suporta Docker).

Quando a aplicação iniciar completamente pela **primeira vez**, é necessário executar alguns comandos para configurações do ambiente. Primeiro seria o comando `docker exec -it feedfor_web_1 python manage.py migrate` para aplicar as alterações no banco de dados do projeto. O segundo seria o `docker exec -it feedfor_web_1 python manage.py createsuperuser` para criar um super usuário no nosso banco para poder acessar a página de administrador que o Django nos proporciona.

**Atenção:** 
- A primeira vez que for executado demorará um pouco mais para fazer o download das imagens com o Docker, após isso a inicialização será sempre rápida;
- Tenha certeza de colocar as credenciais de e-mail corretas, caso contrário os e-mails com Feedbacks não serão enviados;
- Para verificar se e-mails estão sendo enviados ou não por meio dos logs da aplicação, basta acessar os logs do container `feedfor_celery_1`, por meio do comando `docker logs feedfor_celery_1 -f`, sendo o `-f` opcional para acompanhar os logs em tempo real.

