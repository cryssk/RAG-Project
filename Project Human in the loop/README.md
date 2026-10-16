# Project Human in the loop

Agentes com **LangChain** e **LangGraph** que leem o Gmail, resumem os e-mails com o **Claude** e enviam o resultado pelo **Telegram**, com a opção de **Human in the Loop**: você aprova, edita ou rejeita a ação antes de ela ser executada.

O projeto foi construído em etapas. Cada script apresenta um middleware do LangChain, e o último junta todos eles em um agente completo.

## Scripts

| Arquivo | O que faz |
|---|---|
| `01_sumarization.py` | `SummarizationMiddleware`: resume conversas longas (com prompt em português) para economizar tokens. |
| `02_fallback.py` | `ModelFallbackMiddleware`: se o modelo principal falhar, um modelo reserva responde. |
| `03_email_agent.py` | `HumanInTheLoopMiddleware`: o agente lê o último e-mail de um remetente, escreve uma resposta e **pausa** para você aprovar, editar ou rejeitar antes de enviá-la por SMTP. |
| `04_daily_email_agent_wapp.py` | Versão do resumo diário que envia pelo WhatsApp (CallMeBot). |
| `05_daily_email_agent_tlg.py` | **Agente principal.** Resume os e-mails não lidos de cada período do dia (manhã, tarde e noite) e envia o resumo pelo **Telegram**. |

## Como funciona o agente do Telegram (`05`)

1. Lê pelo **IMAP** do Gmail os e-mails não lidos que chegaram no período. A caixa é aberta em modo somente leitura, então nenhum e-mail é marcado como lido.
2. O **Claude Haiku 4.5** escreve uma linha por e-mail (`• resumo — remetente`). Se ele falhar, o **Claude Sonnet 5.5** assume (fallback).
3. O agente chama a ferramenta `enviar_resumo`, que manda o texto para o seu chat pela **API de Bots do Telegram** (`sendMessage`). Mensagens acima de 4.000 caracteres são divididas em partes.
4. Com `APROVAR_ANTES_DE_ENVIAR = True`, o envio pausa e mostra o rascunho no terminal para você aprovar, editar ou rejeitar (Human in the Loop).

Os horários, os cabeçalhos das mensagens e os limites de custo ficam no bloco **CONFIGURAÇÃO** no início do arquivo.

### Por que Telegram?

A API de Bots do Telegram é gratuita, oficial e não exige número de telefone comercial nem serviço intermediário. Basta um token e o ID do chat para enviar mensagens com uma requisição HTTP simples.

## Requisitos

- Python 3.10 ou mais recente
- Uma chave da API da Anthropic: https://platform.claude.com/settings/keys
- Uma conta Gmail com **verificação em duas etapas** e uma **senha de app** (veja abaixo)
- Um bot do Telegram (veja abaixo)

## Instalação

```bash
pip install python-dotenv requests langchain langgraph langchain-anthropic
```

## Passo a passo: senha de app do Gmail

O Google não aceita a sua senha normal em programas que usam IMAP/SMTP. É preciso gerar uma **senha de app**, uma senha de 16 letras que dá acesso só ao e-mail e pode ser revogada a qualquer momento.

1. Acesse https://myaccount.google.com e entre na conta que o agente vai ler.
2. Vá em **Segurança** e ative a **Verificação em duas etapas**. Sem ela, a opção de senha de app não aparece.
3. Abra https://myaccount.google.com/apppasswords (ou pesquise "Senhas de app" na barra de busca da conta).
4. Digite um nome para o app, por exemplo `Agente de e-mails`, e clique em **Criar**.
5. Copie a senha de 16 letras que aparece. Ela só é mostrada uma vez.
6. Coloque a senha no `.env` em `GMAIL_APP_PASSWORD`. Os espaços podem ser removidos.
7. Confira se o IMAP está ativo no Gmail: **Configurações (engrenagem) → Ver todas as configurações → Encaminhamento e POP/IMAP → Ativar IMAP**. Nas contas novas ele já vem ativo.

> Contas de trabalho ou escola (Google Workspace) podem ter a senha de app bloqueada pelo administrador. Nesse caso, use uma conta pessoal ou peça a liberação.

Para revogar o acesso, volte em https://myaccount.google.com/apppasswords e exclua a senha.

## Passo a passo: bot do Telegram

1. No Telegram, abra uma conversa com o **@BotFather**.
2. Envie `/newbot`, escolha um nome e um usuário para o bot (o usuário precisa terminar em `bot`).
3. O BotFather responde com o **token** do bot (formato `123456789:ABC...`). Coloque-o em `TELEGRAM_BOT_TOKEN`.
4. Abra a conversa com o seu bot e envie qualquer mensagem (ex.: `oi`). O bot só consegue escrever para quem falou com ele antes.
5. Acesse no navegador `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates` e procure `"chat":{"id": ...}`. Esse número é o `TELEGRAM_CHAT_ID`.

## Configuração (`.env`)

Crie o arquivo `.env` na raiz do repositório (`RAG - Project/.env`):

```
ANTHROPIC_API_KEY=sk-ant-...

# Gmail
GMAIL_USER=seu-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop

# Só para o 03_email_agent.py: remetente cujo último e-mail será respondido
TARGET_SENDER=alguem@exemplo.com

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=123456789
```

O `.env` está no `.gitignore`. Nunca faça commit do token do bot nem da senha de app: com eles, qualquer pessoa lê seus e-mails ou fala pelo seu bot.

## Como rodar

```bash
cd "Project Human in the loop"

# Testa sem enviar nada: mostra no terminal a mensagem que iria para o Telegram
python 05_daily_email_agent_tlg.py --teste

# Resume e envia o último período encerrado
python 05_daily_email_agent_tlg.py

# Resume um período específico de um dia
python 05_daily_email_agent_tlg.py --periodo manha --data 2026-10-15

# Fica rodando e envia automaticamente ao fim de cada período
python 05_daily_email_agent_tlg.py --agendar
```

No modo `--agendar`, a janela do terminal precisa ficar aberta. O resumo sai 1 minuto depois do fim de cada período, para incluir e-mails que chegaram no último minuto.

## Custo

- Usa o `claude-haiku-4-5`, o Claude mais barato. O Sonnet só entra se o Haiku falhar.
- No máximo 50 e-mails por período e 1.500 caracteres por e-mail são enviados ao modelo (`MAX_EMAILS` e `MAX_CARACTERES_POR_EMAIL`).
- Se não houver e-mails não lidos no período, o modelo não é chamado (custo zero).
- A API de Bots do Telegram é gratuita.

## Segurança

- O agente só **lê** o Gmail (modo somente leitura) e só envia mensagens para o seu chat.
- O prompt manda o modelo ignorar instruções escritas dentro dos e-mails, para reduzir o risco de *prompt injection*.
- Se o envio ao Telegram falhar, a mensagem de erro não mostra a URL, que contém o token do bot.
