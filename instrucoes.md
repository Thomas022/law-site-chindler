# Instruções do Backend — Balcão de Imóveis Chindler

## 1. Objetivo

Desenvolver um backend em Python com Django para administrar o Balcão de Imóveis da Chindler. A ferramenta deverá permitir que a equipe cadastre, edite, publique, retire e arquive imóveis, gerencie imagens e acompanhe solicitações de interessados.

## 2. Finalidades e tipos de imóveis

Cada anúncio terá apenas uma finalidade:

- Venda
- Locação

Tipos disponíveis para cadastro:

- Apartamento
- Casa
- Cobertura
- Terreno
- Sala comercial
- Loja
- Prédio

## 3. Situação dos anúncios

Os imóveis poderão assumir as seguintes situações:

- Rascunho
- Publicado
- Reservado
- Vendido
- Alugado
- Arquivado

Rascunhos poderão ser salvos com dados incompletos. Imóveis enviados para exclusão deverão permanecer em uma lixeira recuperável, e somente administradores poderão realizar a exclusão definitiva.

## 4. Informações do imóvel

Cada anúncio deverá permitir o cadastro das seguintes informações:

- Título
- Descrição
- Finalidade
- Tipo de imóvel
- Preço
- Valor do condomínio
- Área total
- Quantidade de quartos
- Quantidade de suítes
- Quantidade de banheiros
- Quantidade de vagas de garagem
- Endereço completo
- Bairro
- Cidade
- Localização geográfica

Os campos de condomínio, quartos, suítes, banheiros e vagas serão opcionais. Não haverá campo de área útil nem código de referência na primeira versão.

## 5. Requisitos para publicação

Para publicar um anúncio, serão obrigatórios:

- Finalidade
- Tipo de imóvel
- Título
- Descrição
- Preço
- Localização
- Área total
- Pelo menos uma imagem

O anúncio poderá usar a opção “valor sob consulta”. Nesse caso, o preço poderá permanecer armazenado internamente para organização e filtros, sem ser exibido publicamente.

## 6. Endereço e mapa

O endereço completo será armazenado pelo sistema. A equipe poderá escolher se o anúncio mostrará o endereço completo ou somente o bairro e a cidade.

A coordenada exata ficará disponível apenas internamente. O mapa público poderá ser desativado ou exibir uma localização deslocada dentro de uma pequena área próxima ao imóvel, preservando o endereço exato.

## 7. Imagens

Cada imóvel poderá receber até 20 imagens. A equipe poderá escolher a foto principal e definir manualmente a ordem das imagens na galeria.

As imagens deverão ser armazenadas em um serviço externo apropriado, como Cloudinary. O sistema deverá validar os arquivos enviados e gerar versões otimizadas para o site.

## 8. Destaques e ordenação

Os anúncios poderão ser marcados como destaque. A equipe definirá manualmente a ordem em que os imóveis destacados aparecerão no site.

Os demais imóveis poderão ser apresentados do mais recente para o mais antigo. Não será necessário agendar datas de publicação ou retirada na primeira versão.

## 9. Usuários e permissões

O sistema terá dois perfis:

### Administrador

- Gerenciar imóveis
- Publicar, retirar e arquivar anúncios
- Recuperar ou excluir definitivamente imóveis
- Gerenciar usuários
- Alterar configurações gerais
- Exportar dados autorizados

### Editor

- Cadastrar imóveis
- Editar imóveis
- Publicar anúncios
- Retirar anúncios
- Arquivar imóveis
- Exportar dados autorizados

O editor não poderá administrar usuários nem alterar configurações gerais. A autenticação em dois fatores não será obrigatória na primeira versão, mas poderá ser acrescentada posteriormente.

## 10. Histórico de alterações

O sistema deverá registrar as alterações realizadas nos imóveis. O histórico mostrará o usuário responsável, a data da alteração e as informações modificadas.

Não será necessário manter um histórico detalhado das alterações feitas nos contatos de interessados.

## 11. Solicitações de interessados

O formulário de interesse deverá solicitar:

- Nome
- Telefone
- E-mail
- Mensagem

O sistema também registrará automaticamente o imóvel relacionado e a data do contato. Cada solicitação poderá ser atribuída a um administrador ou editor responsável.

Estados disponíveis para o atendimento:

- Novo
- Em atendimento
- Visita agendada
- Concluído
- Descartado

Quando uma nova solicitação for recebida, uma notificação será enviada para um endereço geral da Chindler. Esse endereço será definido posteriormente e deverá ser configurável.

## 12. Privacidade e LGPD

O formulário de interesse deverá exigir o consentimento para o tratamento de dados pessoais e apresentar um link para a política de privacidade. O sistema registrará a data e a versão do consentimento aceito.

Os dados dos interessados serão mantidos por dois anos após o último atendimento. Depois desse período, deverão ser excluídos ou anonimizados automaticamente.

## 13. Pesquisa e filtros

O backend deverá fornecer os dados necessários aos filtros que já existem no frontend do Balcão de Imóveis. A integração deverá preservar o comportamento e a apresentação atuais da plataforma pública.

## 14. Exportação e cadastro

Administradores e editores poderão exportar listas de imóveis e contatos nos formatos Excel ou CSV, respeitando as permissões de acesso. Os imóveis serão cadastrados individualmente pelo painel, sem importação em massa por planilhas na primeira versão.

## 15. Backups

O banco de dados deverá receber um backup automático diário. As cópias dos últimos 30 dias deverão permanecer disponíveis para recuperação.

## 16. Funcionalidades posteriores

As seguintes funcionalidades ficam planejadas para etapas futuras:

- Contato direto pelo WhatsApp da Chindler nas páginas dos imóveis
- Autenticação em dois fatores
- Importação em massa por planilhas, caso se torne necessária

## 17. Arquitetura inicialmente recomendada

- Backend e painel administrativo: Python com Django
- Banco de dados: PostgreSQL
- Armazenamento de imagens: Cloudinary ou serviço equivalente
- Hospedagem do backend: Render ou plataforma compatível
- Repositório e versionamento: GitHub

Este documento representa as decisões da Etapa 1 — Planejamento da estrutura. Alterações futuras deverão ser registradas aqui antes de serem incorporadas ao desenvolvimento.

## 18. Etapa 2 — Preparação do Django

Status: concluída.

O backend foi criado na pasta `backend`, separado do frontend existente. O projeto Django recebeu o nome `chindler_backend` e utiliza Python 3.12 com Django 5.2 LTS.

Foram preparados:

- Configuração compartilhada entre os ambientes
- Ambiente local com SQLite, depuração e e-mails exibidos no terminal
- Ambiente de produção preparado para PostgreSQL, HTTPS e variáveis protegidas
- Django REST Framework para a futura API
- Configuração de CORS para a comunicação com o frontend
- WhiteNoise para arquivos estáticos em produção
- Gunicorn para execução do backend em hospedagem
- Carregamento de variáveis por arquivo `.env`
- Painel administrativo padrão do Django
- Endpoint de verificação de saúde do serviço
- Ambiente virtual local isolado
- Migrações iniciais do Django
- Teste automatizado inicial

As dependências e instruções de inicialização estão documentadas em `backend/README.md`. A próxima etapa deverá criar os modelos de banco de dados definidos neste documento.

## 19. Etapa 3 — Criação do banco de dados

Status: concluída na estrutura do projeto.

O backend foi preparado para usar PostgreSQL como banco principal em produção. Para desenvolvimento, existe uma configuração PostgreSQL reproduzível por Docker Compose e permanece disponível a alternativa SQLite quando `DATABASE_URL` não for informada.

Foram preparados:

- Serviço PostgreSQL local isolado
- Volume persistente para preservar os dados locais
- Credenciais configuráveis por variáveis de ambiente
- Conexões persistentes com verificação automática de integridade
- Transações atômicas por requisição
- Suporte opcional a conexão SSL
- Comando administrativo para testar a conexão
- Endpoint de monitoramento da conexão com o banco
- Utilitários de backup e restauração do PostgreSQL
- Política prevista de backup diário com retenção de 30 dias
- Migrações iniciais do Django

O Docker Desktop instalado foi localizado e o PostgreSQL local foi iniciado com sucesso. As migrações iniciais e os testes automatizados foram executados diretamente no PostgreSQL, confirmando a conexão real do Django com o banco `chindler`.

A próxima etapa deverá criar os modelos de domínio que formarão as tabelas de imóveis, imagens e demais entidades do sistema.

## 20. Etapa 4 — Modelagem dos imóveis

Status: concluída.

Foram criados os modelos de domínio que representam as informações do Balcão de Imóveis no banco de dados.

### Imóveis

O modelo de imóvel contém finalidade, tipo, situação, título, descrição, preço, opção de valor sob consulta, condomínio, área total, características físicas, endereço completo, controles de privacidade, coordenadas privadas e aproximadas, destaque, ordem manual e datas operacionais.

Também foram incluídos identificador público, autoria da criação e atualização, lixeira recuperável, índices de pesquisa e restrições para impedir preços negativos e áreas inválidas.

### Imagens

Cada imóvel pode possuir até 20 imagens. O modelo permite selecionar uma única capa, ordenar a galeria, cadastrar texto alternativo e organizar os arquivos por imóvel.

### Histórico

O modelo de histórico registra o imóvel, título preservado, usuário responsável, ação realizada, alterações e data. A estrutura contempla criação, edição, alteração de situação, envio à lixeira, restauração e exclusão definitiva.

### Interessados

O modelo de interessados armazena imóvel relacionado, nome, telefone, e-mail, mensagem, situação do atendimento, responsável, consentimento LGPD e datas de acompanhamento. O prazo de retenção é calculado em dois anos após o último atendimento.

### Validação

As migrações foram aplicadas no PostgreSQL local. Oito testes automatizados passaram diretamente no PostgreSQL, cobrindo conexão, privacidade do endereço, mapa aproximado, ordem de destaques, limite de imagens, responsáveis e retenção LGPD.

A próxima etapa deverá preparar o painel administrativo para cadastrar e gerenciar essas informações.

## 21. Etapa 5 — Painel administrativo

Status: concluída.

O painel do Django foi personalizado com a identidade administrativa da Chindler e organizado para o uso cotidiano da equipe.

### Gestão de imóveis

O formulário foi dividido em informações principais, valores, características, endereço, mapa, destaque e controles internos. A galeria e o histórico aparecem dentro do próprio cadastro do imóvel.

A listagem possui pesquisa, filtros por situação, finalidade, tipo, destaque, cidade, bairro e lixeira. Também apresenta preço, atualização e estado do anúncio.

### Ações operacionais

Foram adicionadas ações para publicar, retirar da publicação, reservar, marcar como vendido ou alugado, arquivar, enviar para a lixeira, restaurar, exportar CSV e excluir definitivamente. A exclusão definitiva aparece somente para administradores e atua apenas sobre imóveis que já estejam na lixeira.

A publicação exige os dados obrigatórios, pelo menos uma imagem e uma foto principal. Rascunhos continuam aceitando cadastros incompletos.

### Imagens e histórico

O formulário permite até 20 imagens, uma única capa, ordenação manual e texto alternativo. As alterações realizadas pelo painel registram o usuário, a ação, os valores anteriores e os novos valores.

### Interessados

O painel de contatos permite pesquisar e filtrar solicitações, alterar a situação, atribuir um responsável e registrar a data do último atendimento. Os dados recebidos e o consentimento ficam protegidos contra edição acidental, e os contatos podem ser exportados em CSV.

### Perfis de acesso

Os grupos `Administrador` e `Editor` são criados e atualizados automaticamente. O Administrador recebeu 28 permissões e o Editor recebeu 11 permissões no banco local.

O Editor administra imóveis, imagens e atendimentos, mas não acessa usuários e grupos. O Administrador também controla usuários, permissões e exclusões definitivas.

### Validação

Dezenove testes automatizados passaram diretamente no PostgreSQL. Eles verificam regras dos modelos, publicação, lixeira, histórico, grupos, permissões, acesso às telas administrativas e presença da galeria no formulário.

A próxima etapa deverá reforçar a autenticação e os controles de acesso antes da exposição pública da API.

## 22. Etapa 6 — Login e permissões

Status: concluída.

O painel aceita autenticação pelo nome de usuário ou pelo e-mail cadastrado. A tela de login identifica claramente as duas possibilidades.

### Proteção de acesso

Após cinco tentativas inválidas para a mesma identificação e endereço de origem, o acesso fica temporariamente bloqueado por 15 minutos. Um login correto antes do limite limpa as tentativas anteriores.

As senhas exigem no mínimo 12 caracteres e continuam sujeitas às demais verificações do Django. As sessões duram até oito horas, usam cookies inacessíveis ao JavaScript e são encerradas quando o navegador é fechado.

### Recuperação de senha

O fluxo completo de recuperação foi adicionado ao painel, incluindo solicitação, envio, confirmação e conclusão. No ambiente local, as mensagens são exibidas no terminal; a produção está preparada para receber credenciais de um provedor SMTP por variáveis protegidas.

### Criação de usuários

Foi criado um comando administrativo que recebe usuário, e-mail e perfil, solicita a senha de forma oculta, valida sua segurança e associa automaticamente o grupo Administrador ou Editor. O comando impede nomes e e-mails duplicados.

### Validação

Vinte e seis testes automatizados passaram diretamente no PostgreSQL. Eles abrangem login por usuário e e-mail, bloqueio de tentativas, recuperação de senha, criação de usuários, grupos, permissões, painel, imóveis, imagens, lixeira, histórico e interessados.

A próxima etapa deverá integrar o armazenamento externo e o processamento das imagens dos imóveis.

## 23. Etapa 7 — Upload e gerenciamento de imagens

Status: concluída.

O sistema utiliza armazenamento local durante o desenvolvimento e seleciona automaticamente o Cloudinary em produção quando `CLOUDINARY_URL` está configurada. A produção exige essa variável para impedir o uso acidental de um disco temporário.

### Validação

São aceitas imagens JPG, PNG e WebP com até 15 MB e 40 milhões de pixels. Arquivos com extensão, conteúdo, tamanho ou resolução incompatíveis são recusados antes do armazenamento.

### Otimização

As imagens recebem correção automática de orientação, redução proporcional para no máximo 2400 × 1800 pixels e conversão para JPEG progressivo otimizado. O sistema registra largura, altura, tamanho final e formato no banco.

### Painel e galeria

O painel exibe miniaturas, dimensões e tamanho de cada fotografia. Continuam disponíveis a ordenação manual, o texto alternativo, a seleção de capa e o limite de 20 imagens por imóvel.

### Limpeza

Quando uma fotografia é substituída ou removida, o arquivo anterior é excluído somente depois que a transação do banco é confirmada. Isso funciona tanto no armazenamento local quanto no Cloudinary.

### Cloudinary

A integração utiliza o SDK oficial do Cloudinary. Em produção, os arquivos são enviados por conexão segura, organizados pelo imóvel e entregues com formato e qualidade automáticos por CDN.

### Validação técnica

A migração dos metadados foi aplicada no PostgreSQL. Trinta e dois testes passaram diretamente no banco, incluindo uploads locais, formatos inválidos, limites, redimensionamento, exclusão de arquivos, integração simulada com Cloudinary, autenticação, permissões e painel.

A próxima etapa deverá criar a API pública que fornecerá os imóveis publicados ao frontend.

## 24. Etapa 8 — API pública do Balcão de Imóveis

Status: concluída.

A API pública foi criada na versão `/api/v1/`, com uma rota paginada para listar imóveis, uma rota de detalhes por identificador UUID e uma rota auxiliar que fornece as opções disponíveis nos filtros.

### Consulta e filtros

A listagem aceita finalidade, tipo de imóvel, cidade, bairro, quantidade mínima de quartos e vagas, faixa de preço, destaque e busca textual. Também permite ordenar por destaques, publicação mais recente e preço crescente ou decrescente, com 24 resultados por página e limite máximo de 60.

### Privacidade

Somente anúncios publicados e fora da lixeira são entregues. A API nunca expõe coordenadas exatas, autoria, dados internos ou datas administrativas; endereço completo, preço e mapa aproximado aparecem apenas quando suas respectivas opções estiverem habilitadas no painel.

### Galeria e apresentação

Cada imóvel inclui a galeria na ordem definida pela equipe, indicação da capa, texto alternativo e dimensões da imagem. Os dados também incluem rótulos em português, preço já formatado e a mensagem “Sob consulta” quando o valor estiver oculto.

### Proteção e validação

Consultas anônimas são limitadas a 120 requisições por minuto. Quarenta testes automatizados passaram no PostgreSQL, incluindo publicação, rascunhos, filtros, detalhes, privacidade de endereço e mapa, preço oculto, imagens, autenticação, permissões e painel.

A próxima etapa deverá conectar o Balcão de Imóveis do frontend a esta API e definir a configuração do endereço do backend por ambiente.

## 25. Etapa 9 — Integração do frontend com a API

Status: concluída.

O Balcão de Imóveis deixou de utilizar os anúncios demonstrativos fixos e passou a consultar diretamente a API Django. Imóveis publicados ou retirados pelo painel passam a aparecer ou desaparecer do frontend sem uma nova publicação do site.

### Pesquisa e navegação

Finalidade, tipo, bairro e busca textual agora enviam filtros compatíveis com a API. A busca possui um pequeno intervalo antes da consulta para evitar requisições a cada tecla, e a paginação permite navegar por conjuntos maiores de anúncios.

### Estados da interface

A página apresenta carregamento, ausência de resultados, indisponibilidade da API e a opção de tentar novamente. Galerias, capa, preço sob consulta, finalidade, características e contagem total usam os dados fornecidos pelo painel.

### Ambientes e publicação

No ambiente local, o frontend utiliza `http://127.0.0.1:8000` automaticamente. No GitHub Pages, o workflow lê a variável de repositório `API_URL`, que deve conter o endereço HTTPS do backend, enquanto o Django deve autorizar a origem pública em `CORS_ALLOWED_ORIGINS`.

### Validação técnica

Os endpoints reais de listagem e filtros responderam com sucesso, o código integrado passou pela verificação do ESLint sem erros e o build estático das seis rotas foi concluído. O banco local não possui anúncios publicados no momento, portanto o estado vazio é o resultado esperado até a equipe publicar o primeiro imóvel.

A próxima etapa deverá criar uma página própria para os detalhes de cada imóvel, incluindo galeria completa, informações públicas e chamada de contato.

## 26. Etapa 10 — Página individual do imóvel

Status: concluída.

Cada cartão do Balcão agora direciona para uma página individual por meio do identificador público UUID. A rota estática `/imoveis/detalhes/` utiliza o parâmetro `id`, preservando a compatibilidade com o GitHub Pages sem expor o identificador interno do banco.

### Galeria e apresentação

A página exibe uma imagem principal, controles anterior e próximo, contador e miniaturas clicáveis. Quando não houver imagem disponível, o banner institucional é utilizado como alternativa visual.

### Informações do anúncio

Foram incluídos título, finalidade, tipo, descrição, preço ou valor sob consulta, condomínio, área total, quartos, suítes, banheiros, vagas e endereço conforme a privacidade configurada no painel.

### Localização e privacidade

O mapa aparece apenas quando a localização aproximada estiver habilitada e utiliza somente as coordenadas públicas. Caso contrário, a página orienta o visitante a entrar em contato, sem acessar ou revelar coordenadas exatas.

### Contato e tratamento de falhas

A página contém chamadas de interesse por e-mail já identificando o anúncio. Também foram criados estados próprios para carregamento, identificador ausente, anúncio indisponível, erro de conexão e nova tentativa.

### Validação técnica

A página foi construída de forma responsiva para computadores e celulares. A verificação de tipos, o lint específico e o build estático passaram, incluindo a nova rota de detalhes.

A próxima etapa deverá substituir o contato por e-mail por um formulário de interesse integrado ao backend e vinculado ao imóvel.

## 27. Etapa 11 — Formulário de interesse

Status: concluída.

A página individual recebeu um formulário integrado ao Django com nome, telefone, e-mail, mensagem e autorização de contato. Cada envio fica vinculado ao imóvel e entra no painel administrativo com a situação inicial “Novo”.

### Validação e consentimento

O backend valida tamanhos, formato do e-mail, telefone com DDD, mensagem e consentimento obrigatório. A data e a versão do texto de consentimento são registradas junto ao contato para apoiar o tratamento posterior conforme a LGPD.

### Proteção contra abuso

O endpoint aceita solicitações somente para anúncios publicados e fora da lixeira. Foi incluído um campo-armadilha invisível para robôs e um limite específico de cinco envios por hora para cada origem.

### Experiência do visitante

Durante o envio, o botão indica o processamento e impede cliques repetidos. O formulário apresenta erros retornados pelo backend e, após o sucesso, confirma que a equipe recebeu o contato, permitindo ainda iniciar uma nova mensagem.

### Validação técnica

Quatorze testes do conjunto de interessados e API passaram, incluindo criação, vínculo, consentimento, telefone inválido, anúncio em rascunho e descarte de robôs. A verificação de tipos e o lint da área de imóveis passaram sem erros.

A próxima etapa deverá notificar a equipe quando um novo interessado for recebido e definir o canal de envio usado em produção.

## 28. Etapa 12 — Notificações

Status: adiada para a implantação, conforme decisão do projeto.

O envio de alertas para a equipe será configurado quando o provedor de e-mail e o endereço destinatário de produção forem definidos. O cadastro e a consulta dos interessados pelo painel continuam funcionando independentemente dessa integração.

## 29. Etapa 13 — Segurança e LGPD

Status: concluída.

Foi publicada uma Política de Privacidade acessível no formulário e nos rodapés. O documento apresenta dados coletados, finalidade, compartilhamento, segurança, retenção, direitos do titular e canal de contato, tomando como referência a Lei nº 13.709/2018.

### Consentimento e minimização

O formulário exige autorização destacada e registra a versão configurável da política e a data da concordância. A API limita o tamanho da requisição, não aceita contatos para anúncios indisponíveis e mantém os controles contra robôs e excesso de envios.

### Retenção e anonimização

Foi criado um serviço irreversível de anonimização que remove nome, telefone, e-mail, mensagem e responsável depois do prazo. O título do imóvel e dados operacionais mínimos são preservados para histórico, sem permitir a identificação da pessoa.

### Execução automática e manual

O comando `anonymize_expired_leads` processa contatos cujo último atendimento ocorreu há mais de 730 dias, e `--dry-run` permite auditar o volume antes da execução. O comando deverá ser agendado diariamente na hospedagem; administradores também possuem uma ação manual no painel, indisponível para Editores.

### Segurança de produção

Foram confirmados HTTPS obrigatório, cookies seguros, HSTS, bloqueio de incorporação em frames, proteção contra interpretação incorreta de conteúdo, política restrita de referência e CORS sem credenciais. A auditoria `check --deploy` do Django foi aprovada com uma configuração temporária válida.

### Validação técnica

Vinte e cinco testes de interessados, API, painel e privacidade passaram. Eles abrangem anonimização, repetição segura da operação, prazo vencido, renovação do prazo pelo último atendimento e modo de simulação.

A próxima etapa deverá realizar testes completos do fluxo de cadastro, publicação, consulta, interesse e anonimização. As notificações permanecerão pendentes até a implantação.

## 30. Etapa 14 — Testes completos

Status: concluída.

Foi criada uma jornada automatizada de ponta a ponta que cadastra um imóvel, processa uma imagem principal, publica o anúncio, pesquisa e consulta os detalhes pela API, registra um interessado e verifica sua anonimização após o prazo de retenção.

### Backend e banco de dados

Quarenta e nove testes passaram diretamente no PostgreSQL local. O Django não encontrou alterações de modelos sem migração nem migrações pendentes, e a auditoria de produção `check --deploy` foi aprovada.

### Frontend

A verificação de tipos passou e o ESLint não encontrou erros. Permanecem apenas dezesseis avisos conhecidos sobre o uso intencional de imagens HTML externas; o build de produção pré-renderizou as oito rotas estáticas com sucesso.

### Integração local

As rotas de saúde e imóveis responderam com HTTP 200, e o backend autorizou corretamente a origem do frontend local. A página real de um imóvel publicado foi inspecionada no navegador sem erros de console.

### Responsividade

Em uma largura de 375 pixels, o menu móvel permaneceu disponível, o formulário de interesse foi reorganizado em uma coluna e não houve rolagem horizontal. A página de detalhes apresentou galeria, dados, contato, consentimento e acesso à política de privacidade.

A próxima etapa deverá preparar a hospedagem do Django e do PostgreSQL. As notificações da Etapa 12 serão retomadas quando o provedor de e-mail e o destinatário forem definidos.

## 31. Etapa 15 — Hospedagem do backend

Status: infraestrutura preparada; aplicação externa pendente.

O Render foi selecionado como plataforma inicial por oferecer serviço Python, PostgreSQL, tarefas agendadas, integração com GitHub e infraestrutura declarativa. O arquivo `render.yaml` descreve o ambiente completo sem armazenar credenciais.

### Recursos preparados

O Blueprint cria um serviço Django no plano Starter, um PostgreSQL persistente no plano Basic 256 MB e uma tarefa diária de anonimização. Os recursos utilizam a região Virginia, mais próxima do público brasileiro entre as regiões disponíveis na configuração adotada.

### Processo de publicação

O build instala as dependências e coleta arquivos estáticos. Antes de cada publicação, o Render aplica as migrações; em seguida o Gunicorn inicia dois processos, e `/health/` serve como verificação automática de disponibilidade.

### Configuração protegida

A chave Django é gerada pelo Render, a conexão PostgreSQL é injetada diretamente pelo banco e a credencial Cloudinary deve ser informada manualmente. O domínio `.onrender.com` é reconhecido automaticamente, enquanto CORS e CSRF já autorizam a origem pública `https://thomas022.github.io`.

### Segurança operacional

O deploy automático foi desabilitado para impedir novas implantações sem revisão. A rotina de anonimização foi programada para 03:00 UTC, correspondente à meia-noite no horário padrão de Brasília, e utiliza o mesmo banco de produção.

### Validação

O Blueprint foi analisado como YAML válido, o script de build passou na validação do shell, 173 arquivos estáticos foram coletados e 827 versões comprimidas ou manifestadas foram geradas. A auditoria de produção do Django e a configuração do Gunicorn passaram sem erros.

### Pendência externa

Nenhum recurso pago foi criado automaticamente. Para concluir a etapa, o responsável deve conectar o repositório ao Render, revisar os valores dos planos, fornecer `CLOUDINARY_URL` e aplicar o Blueprint conforme `DEPLOY_RENDER.md`.
