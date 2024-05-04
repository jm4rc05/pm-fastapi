# _Scripts_ para criar imagens **AWS**

Estes _scripts_ criam images **AWS** para instâncias **EC2** de banco de dados Postgres.

> **Ob**.: _executar na raiz `podman compose down --volumes && podman compose up --detach` para limpar o ambiente rapidamente_

> **Obs**.: _os scripts criam um certificado digital que deve ser removido com `sudo` para poderem prosseguir corretamente_

* [ami.sh](./ami.sh) - Cria uma imagem, faz upload num _bucket_ **S3** e cria uma instância **EC2** a partir dela (_**LocalStack** não dá suporte à importação de imagens a partir de _buckets_ **S3**_)
* [ec2.sh](./ec2.sh) - Cria uma imagem rodando **PostgreSQL** (a partir do arquivo [PostgreSQL.dockerfile](./PostgreSQL.dockerfile)) e a executa

Para acessar a instância tentar com (obtendo o endereço _IP_ público no console do **LocalStack**):

```sh
ssh -i postgre-ec2-key.pem root@54.214.191.197
```
