# Backend Chindler

Base do sistema administrativo e da API do Balcão de Imóveis, construída com Django.

## Estrutura

- `manage.py`: comandos administrativos locais.
- `chindler_backend/settings/base.py`: configurações compartilhadas.
- `chindler_backend/settings/local.py`: desenvolvimento local com SQLite.
- `chindler_backend/settings/production.py`: produção com PostgreSQL e proteções HTTPS.
- `chindler_backend/urls.py`: painel administrativo e rota de verificação de saúde.
- `properties`: modelos de imóveis, imagens e histórico de alterações.
- `leads`: modelo de solicitações de interessados e retenção LGPD.

## Preparação local

1. Entre na pasta `backend`.
2. Crie e ative um ambiente virtual Python.
3. Instale as dependências de `requirements.txt`.
4. Copie `.env.example` para `.env` e ajuste os valores locais, se necessário.
5. Execute as migrações iniciais.
6. Inicie o servidor Django.

Sem `DATABASE_URL`, o desenvolvimento usa SQLite automaticamente. Em produção, a configuração exige PostgreSQL por meio dessa variável.

## PostgreSQL local

O arquivo `compose.yaml` fornece uma instância PostgreSQL isolada para desenvolvimento. Ele exige Docker Desktop ou outra instalação compatível com Docker Compose.

1. Copie `postgres.env.example` para um arquivo local que não será versionado e defina uma senha própria.
2. Inicie o serviço `database` usando esse arquivo de ambiente.
3. Copie a `DATABASE_URL` correspondente para o arquivo `.env` do Django.
4. Execute as migrações e o comando `database_status`.

O volume `chindler_postgres_data` mantém os dados entre reinicializações do contêiner. O serviço aceita conexões somente pelo endereço local da máquina.

## Verificação do banco

O comando administrativo `database_status` executa uma consulta simples e informa qual banco está conectado. A rota `/health/database/` permite que a futura hospedagem verifique se o serviço também consegue acessar o banco.

## Backups

Os utilitários em `scripts` oferecem backup e restauração do PostgreSQL usando `pg_dump` e `pg_restore`. Eles exigem `DATABASE_URL` e as ferramentas do cliente PostgreSQL instaladas no ambiente em que forem executados.

Em produção, deverá ser mantido um backup automático diário com retenção de 30 dias. A restauração deve ser executada somente por um administrador responsável e sempre após confirmar o banco de destino.

## Endereços locais previstos

- Painel administrativo: `http://localhost:8000/admin/`
- API de imóveis: `http://localhost:8000/api/v1/properties/`
- Opções dos filtros: `http://localhost:8000/api/v1/properties/filters/`
- Verificação de saúde: `http://localhost:8000/health/`
- Verificação do banco: `http://localhost:8000/health/database/`
- Frontend atual: `http://localhost:3000/`

## Painel administrativo

O painel permite gerenciar imóveis, galerias, destaques, situações, lixeira, histórico e contatos de interessados. Para o primeiro acesso local, crie um superusuário com o comando padrão `createsuperuser` do Django e abra `/admin/`.

Como alternativa, o comando `create_chindler_user` cria um usuário da equipe, solicita a senha sem exibi-la no terminal e associa o perfil escolhido. Informe nome de usuário, e-mail e `--role Administrador` ou `--role Editor`.

Dois grupos são mantidos automaticamente:

- `Administrador`: gerencia imóveis, contatos, usuários, grupos e exclusões definitivas.
- `Editor`: cadastra, edita, publica, arquiva e envia imóveis para a lixeira, além de acompanhar contatos; não administra usuários.

Imóveis novos começam como rascunho. A publicação é feita pelas ações da listagem e exige pelo menos uma imagem definida como capa, além dos campos obrigatórios.

## Imagens dos imóveis

No desenvolvimento, os uploads são salvos em `backend/media` e servidos pelo Django. Em produção, `CLOUDINARY_URL` é obrigatório e ativa automaticamente o armazenamento Cloudinary.

São aceitos arquivos JPG, PNG e WebP com até 15 MB e 40 milhões de pixels. Antes de salvar, o sistema corrige a orientação, limita a imagem a 2400 × 1800 pixels e gera um JPEG progressivo otimizado.

O banco registra largura, altura, tamanho final e formato. Arquivos substituídos ou excluídos também são removidos do armazenamento após a confirmação da transação do banco.

As miniaturas do painel usam o arquivo otimizado localmente ou uma transformação responsiva do Cloudinary. As credenciais do Cloudinary devem existir apenas nas variáveis protegidas da hospedagem.

## Autenticação

O painel aceita login pelo nome de usuário ou pelo e-mail cadastrado. Após cinco tentativas inválidas para a mesma identificação e endereço de origem, novas tentativas ficam bloqueadas por 15 minutos.

As senhas devem ter pelo menos 12 caracteres e atender aos validadores de segurança do Django. A sessão administrativa dura até oito horas e é encerrada quando o navegador é fechado.

A recuperação de senha está disponível na tela de login. Em desenvolvimento, o e-mail aparece no terminal; em produção, as variáveis `EMAIL_*` devem apontar para um provedor SMTP real.

## API pública

A API oferece apenas imóveis publicados e fora da lixeira. A listagem aceita paginação e os filtros `purpose`, `property_type`, `city`, `neighborhood`, `bedrooms`, `parking_spaces`, `min_price`, `max_price`, `featured`, `search` e `ordering`.

As ordenações disponíveis são `featured`, `newest`, `price_asc` e `price_desc`. Cada detalhe usa o identificador público UUID em `/api/v1/properties/<id>/`; endereços, mapas e preços respeitam as opções de privacidade escolhidas no painel.

Por segurança, a API nunca entrega coordenadas exatas, usuários internos ou dados administrativos. Consultas anônimas são limitadas a 120 requisições por minuto e páginas têm 24 registros, permitindo no máximo 60.

## Próxima etapa

A infraestrutura da Etapa 15 está preparada em `render.yaml`. A aplicação efetiva do Blueprint depende da conta Render, da confirmação dos planos e da credencial Cloudinary; consulte `DEPLOY_RENDER.md` na raiz.

## Integração com o frontend

O Balcão de Imóveis consulta a API diretamente pelo navegador. No desenvolvimento local, a ausência de `NEXT_PUBLIC_API_URL` faz o frontend utilizar automaticamente `http://127.0.0.1:8000`.

No GitHub Pages, crie a variável de repositório `API_URL` com a URL HTTPS pública do Django, sem barra no final. No backend publicado, inclua a origem completa do GitHub Pages em `CORS_ALLOWED_ORIGINS`; credenciais ou chaves privadas nunca devem ser colocadas nessa variável pública.

## Formulário de interesse

A página individual envia os contatos para `/api/v1/properties/<id>/interest/`. O endpoint aceita somente imóveis publicados, valida nome, telefone, e-mail, mensagem e consentimento, limita cada origem a cinco envios por hora e utiliza um campo-armadilha contra robôs.

Os contatos são cadastrados como `Novo` na seção Interessados do painel, preservando o título do anúncio e o registro da versão e data do consentimento.

## Privacidade e retenção

A versão do consentimento é definida por `PRIVACY_POLICY_VERSION`. A página pública `/privacidade/` explica finalidade, dados tratados, retenção e direitos do titular, e está ligada ao formulário e aos rodapés.

O comando `anonymize_expired_leads --dry-run` simula a limpeza dos contatos vencidos. Sem `--dry-run`, ele anonimiza dados pessoais cujo último atendimento ocorreu há mais de 730 dias; em produção, esse comando deverá ser agendado diariamente pela hospedagem.

Administradores também podem anonimizar contatos selecionados pelo painel. A operação remove os dados pessoais de forma irreversível, preservando somente informações operacionais mínimas.

## Validação completa

A suíte pode ser executada dentro de `backend` com `python manage.py test --settings=chindler_backend.settings.test`. Ela inclui uma jornada integrada que cria um imóvel com imagem, publica, consulta listagem e detalhe, recebe um interessado e valida a anonimização.

Antes de implantar, também devem ser executados `makemigrations --check --dry-run`, `migrate --check`, `check --deploy`, a checagem TypeScript, o lint e o build do frontend.
