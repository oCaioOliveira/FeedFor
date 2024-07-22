# Descrição

Esse projeto é uma API, com o objetivo de ser integrado a sistemas de educação, relacionados a aplicações de questionários. O caso de uso testado foram questionários applicados no Microsoft Forms, facilitando a integração usando fluxos no Microsoft Automate.

Com as configurações e acessos necessários, essa API é capaz de receber informações sobre testes realizados com alunos e construir um Feedback Formativo individual que será enviado no e-mail do estudante indicando seus erros e acertos, além de indicar possíveis pontos de aperfeiçoamento.

Além disso, é capaz de armazenar as informações sobre os questionários na sua base de dados, sendo possível solicitar um relatório em excel que será enviado para o professor da disciplina relacionada ao questionário.

# Como Rodar

Para rodar a aplicação primeiro precisa ser configurado o `.env` na raiz do projeto:

```
# EMAIL CREDENTIALS
EMAIL_HOST_USER=youremail@hotmail.com
EMAIL_HOST_PASSWORD=yourpassword

# DATABASE LOCAL SETTINGS
DB_NAME=feedfordb
DB_USER=feedfordbuser
DB_PASSWORD=feedfordbpassword
DB_HOST=feedfordb
DB_PORT=5432
```

Acima está um exemplo de `.env` que armazena as configurações das credenciais do serviço de e-mail e do banco de dados local. As credenciais do serviço de e-mail servem para conseguirmos enviar um e-mail com o Feedback Formativo dos alunos ou os relatórios para professores. As configurações do banco de dados são usadas na inicialização do projeto para identificar um serviço de armazenamento de dados que será usado, se o desejado for local, pode ser copiado e colados as configurações, caso o objetivo seja conectar com algum serviço externo como um banco de dados na nuvem por exemplo, é necessário recuperar as informações desse serviço e preencher nos campos corretamente.

Após configurar o `.env` da aplicação, basta rodar o comando `docker-compose up` para inicializar o projeto (requisito mínimo seria ter uma máquina que suporta Docker).
