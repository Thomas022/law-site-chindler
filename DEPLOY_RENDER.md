# Publicação do backend no Render

Este projeto usa um Blueprint de demonstração para criar dois recursos integrados:

- `chindler-backend`: painel administrativo e API Django;
- `chindler-database`: PostgreSQL gratuito para testes.

## Antes de aplicar

O Blueprint seleciona o plano `free` para o serviço web e para o PostgreSQL. Antes de confirmar, confira se os dois recursos aparecem como gratuitos; esse ambiente é apenas para testes, porque o banco gratuito expira 30 dias após a criação e não possui backups.

O serviço web pode entrar em suspensão quando fica inativo, tornando o primeiro acesso mais lento. A rotina automática de anonimização não faz parte deste Blueprint gratuito e deverá ser executada manualmente durante os testes.

Crie também uma conta no Cloudinary e copie a variável `CLOUDINARY_URL`. Ela contém credenciais e nunca deve ser colocada no código ou nas variáveis públicas do GitHub Pages.

## Criar os serviços

1. Envie todas as alterações deste projeto para o repositório GitHub.
2. No Render, abra **New → Blueprint** e conecte `Thomas022/law-site-chindler`.
3. Confirme que o Blueprint encontrado é `render.yaml` e revise os dois recursos; ambos devem exibir o plano gratuito.
4. Informe `CLOUDINARY_URL` quando o Render solicitar o valor secreto do serviço web.
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
- durante o teste, execute manualmente `python manage.py anonymize_expired_leads --settings=chindler_backend.settings.production` em um ambiente conectado ao banco quando for necessário testar a anonimização.

O imóvel e a fotografia cadastrados localmente não são copiados automaticamente. O caminho mais seguro para o primeiro lançamento é cadastrá-los novamente no painel de produção, fazendo com que as imagens já sejam enviadas ao Cloudinary.
