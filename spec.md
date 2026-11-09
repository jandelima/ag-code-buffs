# Especificação do Projeto — Ambiente Unificado de Desenvolvimento com IA

**Versão:** 1.0  
**Data:** 08/11/2026  
**Tipo:** Documento de requisitos e objetivos

---

## 1. Visão Geral

O projeto tem como objetivo melhorar a experiência de desenvolvimento com agentes de inteligência artificial, especialmente Claude Code e Codex, por meio de três etapas progressivas.

A proposta é preservar as ferramentas oficiais, seus harnesses e suas atualizações, adicionando funcionalidades de transcrição de voz, gerenciamento de contas e integração entre modelos.

O projeto não pretende desenvolver um novo agente de programação nem substituir o Claude Code ou o Codex.

### Princípios fundamentais

- Preservar o Claude Code oficial como ambiente principal.
- Manter compatibilidade com atualizações futuras.
- Evitar modificações invasivas nas ferramentas existentes.
- Priorizar simplicidade, desempenho e facilidade de uso.
- Aproveitar as assinaturas existentes do Claude Code e do Codex.
- Evitar custos recorrentes adicionais quando houver alternativas locais viáveis.
- Desenvolver funcionalidades reutilizáveis entre as etapas.

---

## 2. Etapa 1 — Transcrição de Voz Universal

### 2.1. Objetivo

Desenvolver um aplicativo para Windows que funcione em segundo plano e permita inserir texto transcrito por voz em qualquer campo de texto ativo.

A transcrição deverá ser realizada localmente, utilizando o hardware disponível, sem depender de APIs externas.

### 2.2. Requisitos Funcionais

**RF01 — Execução em segundo plano**
- O aplicativo deverá permanecer disponível em segundo plano.
- Não deverá exigir uma janela aberta durante o uso.

**RF02 — Atalho global**
- O usuário deverá conseguir iniciar a captura de áudio por meio de um atalho global.
- O mesmo atalho, ou outro configurável, deverá permitir interromper a captura.

**RF03 — Transcrição de áudio**
- O aplicativo deverá transcrever a fala em português brasileiro.
- A transcrição deverá preservar fielmente o conteúdo falado.
- O texto deverá apresentar pontuação adequada.
- O sistema deverá evitar alterações desnecessárias no significado da fala.

**RF04 — Inserção universal de texto**
- O texto deverá ser inserido no campo em que o cursor estiver posicionado.
- A funcionalidade deverá operar independentemente do aplicativo utilizado, desde que o campo aceite entrada de texto.

**RF05 — Compatibilidade com aplicativos**
- Terminais Windows.
- Windows Terminal.
- Sessões WSL.
- Claude Code.
- Codex.
- Navegadores.
- WhatsApp.
- Editores de texto.
- Outros aplicativos compatíveis com entrada de texto.

**RF06 — Controle sobre o envio**
- O aplicativo deverá apenas inserir a transcrição.
- Não deverá enviar mensagens automaticamente.
- Não deverá executar comandos automaticamente.
- O usuário deverá poder revisar e editar o texto antes de enviá-lo.

### 2.3. Requisitos Não Funcionais

- Processamento local, sem dependência obrigatória de internet.
- Baixo consumo de CPU e GPU quando inativo.
- Baixa latência de transcrição.
- Boa precisão em português brasileiro.
- Funcionamento estável durante sessões prolongadas.
- Baixa interferência nas demais aplicações em execução.
- Tratamento adequado de falhas de captura e transcrição.

### 2.4. Ambiente de Referência

- Sistema operacional: Windows.
- Processador: AMD Ryzen 7 5700X.
- GPU: NVIDIA RTX 4060.
- Idioma principal: Português brasileiro.
- Processamento: Local, preferencialmente.

### 2.5. Critério de Conclusão

A etapa será considerada concluída quando o usuário conseguir:

1. Abrir qualquer campo de texto compatível.
2. Posicionar o cursor.
3. Acionar o atalho de gravação.
4. Falar naturalmente.
5. Encerrar a gravação.
6. Receber a transcrição diretamente no campo selecionado.
7. Revisar e enviar o texto manualmente.

Tudo isso sem precisar copiar e colar a transcrição.

---

## 3. Etapa 2 — Gerenciamento de Contas do Claude Code

### 3.1. Objetivo

Permitir a alternância rápida entre diferentes contas e assinaturas do Claude Code, eliminando a necessidade de realizar repetidamente logout e login.

A solução deverá preservar o funcionamento oficial do Claude Code e sua capacidade de receber atualizações.

### 3.2. Requisitos Funcionais

**RF01 — Múltiplas contas**
- Permitir manter diferentes contas do Claude Code configuradas.
- Preservar as sessões autenticadas enquanto permanecerem válidas.
- Manter as credenciais e configurações de cada conta separadas.

**RF02 — Alternância simplificada**
- Permitir trocar de conta por meio de um comando simples ou mecanismo equivalente.
- Evitar a necessidade de executar logout e login a cada troca.
- Minimizar a quantidade de ações necessárias para alternar entre contas.

**RF03 — Identificação da conta ativa**
- Permitir identificar facilmente qual conta está sendo utilizada.
- Evitar ambiguidades durante a alternância.

**RF04 — Preservação das sessões**
- Manter as sessões das contas que não estiverem ativas.
- Evitar autenticações repetidas enquanto as sessões permanecerem válidas.

**RF05 — Integração com Claude Code**
- Priorizar uma experiência acessível diretamente pelo terminal.
- Preferencialmente, permitir a troca sem abandonar o ambiente de trabalho.
- Preservar as funcionalidades oficiais do Claude Code.

### 3.3. Requisitos de Compatibilidade

- Compatibilidade com Ubuntu nativo.
- Compatibilidade com Ubuntu executado no WSL.
- Preservação do Claude Code oficial.
- Compatibilidade com futuras atualizações, na medida do possível.
- Evitar dependência de versões específicas.
- Evitar alterações invasivas em arquivos internos do Claude Code.
- Respeitar os mecanismos de autenticação e as condições de uso aplicáveis.

### 3.4. Critério de Conclusão

A etapa será considerada concluída quando o usuário conseguir:

1. Configurar múltiplas contas do Claude Code.
2. Autenticar cada conta inicialmente.
3. Alternar entre contas previamente autenticadas com uma ação simples.
4. Continuar utilizando normalmente o Claude Code.
5. Receber atualizações oficiais sem perder a funcionalidade de alternância.

---

## 4. Etapa 3 — Experiência Unificada no Terminal

### 4.1. Objetivo

Oferecer uma experiência integrada de desenvolvimento com Claude Code e Codex, preferencialmente dentro do próprio Claude Code.

O ambiente deverá permitir:

- Interação contínua por voz.
- Detecção automática do término da fala.
- Seleção simplificada de provedores e modelos.
- Configuração do nível de esforço de raciocínio.
- Integração entre Claude Code e Codex.
- Delegação de tarefas entre agentes.
- Preservação do harness oficial do Claude Code.
- Compatibilidade com futuras atualizações das ferramentas.

### 4.2. Interação por Voz Contínua

**RF01 — Modo de voz**
- Disponibilizar um modo de interação por voz.
- O modo deverá permanecer ativo durante a sessão, quando habilitado.
- Não deverá exigir atalhos para iniciar cada nova fala.

**RF02 — Detecção automática de fala**
- Detectar automaticamente quando o usuário começa a falar.
- Detectar quando o usuário termina de falar.
- Evitar encerrar a transcrição durante pausas naturais.

**RF03 — Transcrição automática**
- Transcrever a fala automaticamente.
- Inserir o texto no campo de entrada do terminal.
- Preservar fidelidade e pontuação.

**RF04 — Controle sobre o envio**
- Não enviar automaticamente o texto transcrito.
- Não executar comandos automaticamente.
- Permitir revisão e edição antes do envio.

**RF05 — Reutilização**
- Reutilizar, quando possível, as funcionalidades desenvolvidas na Etapa 1.

### 4.3. Seleção de Modelos e Provedores

**RF06 — Alternância entre provedores**
- Permitir selecionar modelos Claude.
- Permitir selecionar modelos GPT disponibilizados pelo Codex.
- Facilitar a alternância entre provedores durante o trabalho.

**RF07 — Seleção de modelos**
- Permitir escolher o modelo específico.
- Facilitar o acesso a novos modelos oficialmente disponibilizados.
- Evitar configurações manuais complexas para alternar entre modelos.

**RF08 — Configuração de esforço**
- Permitir selecionar o nível de esforço de raciocínio.
- Respeitar os níveis suportados por cada modelo.
- Permitir alterar a configuração de maneira simples.

**RF09 — Identificação da configuração ativa**
- Exibir ou permitir consultar facilmente:
  - Provedor ativo.
  - Modelo selecionado.
  - Nível de esforço configurado.
  - Conta utilizada, quando aplicável.

### 4.4. Integração entre Claude Code e Codex

**RF10 — Ambiente principal**
- Preservar o Claude Code como ambiente principal de interação.
- Manter o acesso às funcionalidades de seu harness oficial.

**RF11 — Utilização do Codex**
- Permitir utilizar o Codex em tarefas de raciocínio, análise ou programação.
- Evitar a necessidade de alternar manualmente entre terminais independentes.

**RF12 — Delegação de tarefas**
- Permitir solicitar ao Claude Code que delegue tarefas ao Codex.
- Possibilitar a utilização do Codex como agente auxiliar.
- Permitir que os resultados sejam aproveitados no fluxo principal.

**RF13 — Compartilhamento de contexto**
- Preservar, sempre que tecnicamente possível, o contexto relevante durante a delegação.
- Evitar a necessidade de repetir manualmente informações já disponíveis.
- Reduzir a perda de contexto durante a alternância entre agentes.

### 4.5. Preservação das Ferramentas Oficiais

Este é um requisito central e prioritário.

**RF14 — Preservação do harness**
- Manter o harness oficial do Claude Code como preferência principal.
- Não recriar desnecessariamente funcionalidades existentes.
- Preservar o comportamento das ferramentas originais.

**RF15 — Atualizações**
- Continuar recebendo atualizações oficiais do Claude Code.
- Continuar recebendo atualizações oficiais do Codex.
- Manter acesso às novas funcionalidades disponibilizadas.
- Manter acesso aos novos modelos disponibilizados.
- Evitar modificações que precisem ser refeitas a cada atualização.

**RF16 — Compatibilidade**
- Evitar alterações invasivas nas ferramentas.
- Priorizar mecanismos de extensão e integração compatíveis com as ferramentas oficiais.
- Minimizar a dependência de comportamentos internos não documentados.

### 4.6. Restrições e Considerações

A utilização direta de modelos GPT dentro do harness do Claude Code constitui um objetivo sujeito à avaliação de viabilidade técnica.

Caso a substituição direta do modelo não seja compatível com o funcionamento oficial da ferramenta, a integração por delegação ao Codex poderá constituir uma alternativa.

A implementação deverá priorizar a preservação das funcionalidades oficiais em vez de forçar uma integração que comprometa a estabilidade ou as atualizações.

### 4.7. Critério de Conclusão

A etapa será considerada concluída quando o usuário conseguir:

1. Utilizar uma experiência de terminal unificada.
2. Trabalhar preferencialmente dentro do Claude Code.
3. Habilitar um modo de interação contínua por voz.
4. Falar naturalmente e receber a transcrição sem acionar atalhos repetidamente.
5. Revisar o texto antes de enviá-lo.
6. Alternar facilmente entre modelos Claude e GPT/Codex.
7. Configurar os níveis de esforço disponíveis.
8. Delegar tarefas do Claude Code ao Codex.
9. Continuar utilizando as funcionalidades oficiais.
10. Receber atualizações futuras sem comprometer a integração.

---

## 5. Sequência das Entregas

### Etapa 1 — Transcrição Universal

**Entrega:** aplicativo de transcrição local por atalho global.

**Dependências:** nenhuma das demais etapas.

### Etapa 2 — Gerenciamento de Contas

**Entrega:** mecanismo de alternância simplificada entre contas do Claude Code.

**Dependências:** nenhuma das demais etapas.

### Etapa 3 — Experiência Unificada

**Entrega:** ambiente integrado com voz contínua, seleção de modelos, configuração de esforço e delegação entre Claude Code e Codex.

**Dependências:** poderá reutilizar funcionalidades desenvolvidas nas Etapas 1 e 2.

---

## 6. Escopo e Decisões Futuras

Este documento estabelece os objetivos, requisitos e critérios de conclusão do projeto.

Não determina antecipadamente:

- Linguagens de programação.
- Frameworks.
- Bibliotecas.
- Modelos específicos de transcrição.
- Mecanismos de autenticação.
- Arquitetura de integração.
- Protocolos de comunicação entre agentes.
- Formas específicas de extensão do Claude Code.

Essas decisões deverão ser tomadas durante o planejamento técnico de cada etapa, considerando:

1. Viabilidade técnica.
2. Compatibilidade com ferramentas oficiais.
3. Facilidade de manutenção.
4. Desempenho.
5. Simplicidade de utilização.
6. Custos operacionais.
7. Preservação de atualizações futuras.

O objetivo principal é ampliar as capacidades das ferramentas existentes, sem substituí-las ou comprometer sua evolução.
