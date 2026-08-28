# Publicação do backend no Render

Este projeto usa um Blueprint para criar três recursos integrados:

- `chindler-backend`: painel administrativo e API Django;
- `chindler-database`: PostgreSQL persistente;
- `chindler-anonymize-expired-leads`: anonimização diária de contatos vencidos.

## Antes de aplicar

O Blueprint seleciona planos pagos adequados a uma aplicação permanente: `starter` para o serviço e a rotina e `basic-256mb` para o PostgreSQL. Confira os preços exibidos pelo Render antes de confirmar; nenhum recurso ou cobrança é criado apenas pela presença do arquivo no repositório.

Crie também uma conta no Cloudinary e copie a variável `CLOUDINARY_URL`. Ela contém credenciais e nunca deve ser colocada no código ou nas variáveis públicas do GitHub Pages.

## Criar os serviços

1. Envie todas as alterações deste projeto para o repositório GitHub.
2. No Render, abra **New → Blueprint** e conecte `Thomas022/law-site-chindler`.
3. Confirme que o Blueprint encontrado é `render.yaml` e revise os três recursos e seus custos.
4. Informe `CLOUDINARY_URL` para o serviço web e para a rotina de anonimização.
5. Aplique o Blueprint e aguarde banco, migrações, arquivos estáticos e serviço web ficarem disponíveis.

O serviço detecta automaticamente seu domínio `.onrender.com`. Para um domínio personalizado, acrescente o host em `DJANGO_ALLOWED_HOSTS` e sua origem HTTPS em `CSRF_TRUSTED_ORIGINS` quando necessário.

## Criar o primeiro administrador

Abra o Shell do serviço `chindler-backend` e execute:

```text
python manage.py create_chindler_user administrador email@empresa.com --role Administrador --settings=chindler_backend.settings.production
```

O comando solicitará a senha sem mostrá-la. Depois, abra `https://ENDERECO-DO-BACKEND/admin/`.

## Conectar o GitHub Pages

1. No GitHub, abra **Settings → Secrets and variables → Actions → Variables**.
2. Crie ou atualize `API_URL` com `https://ENDERECO-DO-BACKEND`, sem barra no final.
3. Execute novamente o workflow **Publicar no GitHub Pages**.
4. Confirme no Render que `CORS_ALLOWED_ORIGINS` contém `https://thomas022.github.io`.

## Verificações após a publicação

- `/health/` deve responder com estado `ok`;
- `/health/database/` deve informar PostgreSQL;
- `/admin/` deve abrir somente por HTTPS;
- o cadastro deve enviar imagens ao Cloudinary;
- um imóvel publicado deve aparecer no GitHub Pages;
- o formulário deve criar um interessado no painel;
- a rotina diária deve aparecer com a próxima execução programada para 03:00 UTC.

O imóvel e a fotografia cadastrados localmente não são copiados automaticamente. O caminho mais seguro para o primeiro lançamento é cadastrá-los novamente no painel de produção, fazendo com que as imagens já sejam enviadas ao Cloudinary.
