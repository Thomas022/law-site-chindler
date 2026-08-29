# To-do — Gestão de Interessados

Este checklist orienta a evolução da área **Interessados** do Balcão de Imóveis para um fluxo completo de atendimento. Os itens marcados com `[x]` já existem; os itens `[ ]` ainda precisam ser implementados e validados.

## Objetivo da primeira versão

Permitir que a equipe receba, distribua e acompanhe cada interessado até a conclusão do atendimento, mantendo histórico, próximas ações, permissões e proteção dos dados pessoais.

## Progresso geral

- [x] Receber interessados pelo formulário público
- [x] Relacionar o interessado ao imóvel anunciado
- [x] Exibir interessados no Django Admin
- [x] Permitir situação e responsável
- [x] Pesquisar, filtrar e exportar contatos
- [x] Registrar consentimento e aplicar retenção LGPD
- [x] Permitir cadastro manual com nome, e-mail e mensagem
- [x] Criar histórico completo de atendimento
- [x] Criar próximas ações e compromissos
- [x] Criar indicadores operacionais
- [x] Aplicar a nova interface ao painel
- [ ] Implantar notificações

## 1. Regras e estrutura dos dados

- [x] Confirmar os estados definitivos: Novo, Em atendimento, Visita agendada, Concluído e Descartado
- [x] Adicionar prioridade do interessado: normal, alta ou urgente
- [x] Adicionar origem: site, telefone, WhatsApp, indicação ou cadastro manual
- [x] Adicionar motivo de descarte
- [x] Adicionar data de conclusão
- [x] Definir se um interessado pode mudar de imóvel durante o atendimento — nesta versão, o imóvel original permanece protegido contra alteração
- [x] Criar e revisar as migrações do banco de dados
- [x] Garantir valores padrão para os registros que já existem

**Concluído quando:** as novas informações forem armazenadas sem quebrar os interessados atuais e todas as migrações puderem ser aplicadas e revertidas com segurança.

## 2. Histórico de atendimento

- [x] Criar uma entidade de interação vinculada ao interessado
- [x] Registrar tipos: observação, ligação, e-mail, WhatsApp, visita e alteração de situação
- [x] Armazenar autor, data, descrição e resultado de cada interação
- [x] Registrar automaticamente mudanças de situação e responsável
- [x] Impedir alteração silenciosa do histórico já registrado
- [x] Exibir uma linha do tempo na página do interessado
- [x] Incluir o histórico no processo de anonimização LGPD

**Concluído quando:** qualquer membro autorizado puder entender todo o atendimento em ordem cronológica e identificar quem realizou cada ação.

## 3. Próximas ações e tarefas

- [x] Criar próxima ação com tipo, data, horário, responsável e observação
- [x] Permitir concluir, cancelar ou reagendar uma ação
- [x] Destacar ações de hoje, futuras e atrasadas
- [x] Evitar que tarefas concluídas continuem aparecendo como pendentes
- [x] Permitir mais de uma tarefa futura por interessado
- [x] Registrar a conclusão da tarefa no histórico
- [x] Criar filtros por prazo e responsável

**Concluído quando:** a equipe conseguir identificar claramente quem deve fazer o quê e até quando.

## 4. Página individual do interessado

- [x] Organizar dados pessoais, imóvel, situação e responsável em seções recolhíveis
- [x] Mostrar telefone e e-mail com ações rápidas
- [x] Exibir a próxima ação em destaque
- [x] Exibir a linha do tempo do atendimento
- [x] Adicionar formulário rápido para observações
- [x] Adicionar comandos para ligação, mensagem, visita, conclusão e descarte
- [x] Solicitar justificativa ao descartar um interessado
- [x] Preservar o layout responsivo em celulares

**Concluído quando:** o atendimento puder ser operado integralmente a partir de uma única tela.

## 5. Lista e indicadores do painel

- [x] Exibir colunas: Nome, Imóvel, Situação, Responsável, Próxima ação e Recebido em
- [x] Aplicar etiquetas visuais às situações
- [x] Criar indicadores: Novos, Em atendimento, Visitas agendadas e Atrasados
- [x] Fazer cada indicador filtrar a listagem correspondente
- [x] Manter pesquisa por nome, telefone, e-mail e imóvel
- [x] Manter filtros laterais compatíveis com o Django Admin
- [x] Adicionar filtro por próxima ação
- [x] Manter exportação CSV conforme as permissões
- [x] Verificar paginação e desempenho com grande quantidade de contatos

**Concluído quando:** o painel reproduzir funcionalmente o protótipo aprovado e os números refletirem os dados reais.

## 6. Permissões e auditoria

- [ ] Administrador visualiza e redistribui todos os interessados
- [ ] Editor visualiza os contatos permitidos pela regra definida
- [ ] Editor registra interações, tarefas e mudanças de situação
- [ ] Restringir exportação, exclusão e anonimização conforme o perfil
- [ ] Registrar usuário, data e conteúdo das alterações relevantes
- [ ] Impedir acesso a interessados por usuários sem permissão
- [ ] Testar tentativas de acesso direto por URL

**Concluído quando:** cada perfil executar somente as ações autorizadas e toda mudança importante tiver autoria rastreável.

## 7. Notificações

- [ ] Definir o endereço geral da Chindler
- [ ] Configurar o provedor de e-mail em produção
- [ ] Notificar a equipe ao receber um novo interessado
- [ ] Criar alertas internos para ações próximas e atrasadas
- [ ] Evitar notificações duplicadas
- [ ] Registrar quando uma notificação foi enviada ou falhou
- [ ] Deixar WhatsApp e outras automações para uma expansão posterior

**Concluído quando:** novos contatos e tarefas importantes gerarem alertas confiáveis sem excesso de mensagens.

## 8. Privacidade e LGPD

- [ ] Confirmar quais dados do histórico serão anonimizados
- [ ] Remover dados pessoais de observações e tarefas durante a anonimização
- [ ] Manter somente métricas não identificáveis após o prazo de retenção
- [ ] Bloquear exportação para usuários não autorizados
- [ ] Registrar operações administrativas sensíveis
- [ ] Validar o texto e a versão do consentimento utilizados no site

**Concluído quando:** interessado, histórico e tarefas seguirem a mesma política de retenção e anonimização.

## 9. Testes e qualidade

- [ ] Testar criação pelo formulário público
- [ ] Testar atribuição e troca de responsável
- [ ] Testar todas as mudanças de situação
- [ ] Testar criação, conclusão e atraso de tarefas
- [ ] Testar linha do tempo e auditoria
- [ ] Testar indicadores e filtros
- [ ] Testar permissões de Administrador e Editor
- [ ] Testar anonimização dos novos dados
- [ ] Testar responsividade do painel
- [ ] Executar a suíte completa do backend
- [ ] Realizar teste manual do fluxo completo no ambiente de homologação

**Concluído quando:** os testes automatizados passarem e um atendimento completo puder ser realizado sem erros no ambiente de teste.

## 10. Implantação

- [ ] Fazer backup do banco antes da migração
- [ ] Aplicar migrações primeiro em homologação
- [ ] Validar interessados existentes após a migração
- [ ] Configurar variáveis de notificação
- [ ] Publicar o backend no Render
- [ ] Executar verificações de saúde e logs
- [ ] Validar o fluxo entre website, API e painel publicado
- [ ] Orientar a equipe sobre o novo processo de atendimento
- [ ] Monitorar erros e uso durante os primeiros dias

**Concluído quando:** o fluxo estiver disponível em produção, integrado ao site e validado pela equipe da Chindler.

## Ordem recomendada de implementação

1. Estrutura dos dados e migrações
2. Histórico de atendimento
3. Próximas ações e tarefas
4. Página individual do interessado
5. Lista, filtros e indicadores
6. Permissões, auditoria e LGPD
7. Notificações
8. Testes completos
9. Implantação e treinamento

## Registro de andamento

Ao terminar uma entrega, marcar o item correspondente com `[x]` e registrar abaixo a data, um resumo e os testes executados.

| Data | Entrega | Resultado | Testes |
|---|---|---|---|
| — | Checklist criado | Planejamento da evolução do módulo de interessados | Não se aplica |
| 29/08/2026 | Etapas 1 a 5 | Dados, histórico, tarefas, página individual, lista, filtros e indicadores implementados | 57 testes automatizados e inspeção visual local |
| 29/08/2026 | Cadastro manual | Canal manual com telefone e imóvel opcionais, origem automática e consentimento não informado | Teste automatizado e cadastro pela interface local |
