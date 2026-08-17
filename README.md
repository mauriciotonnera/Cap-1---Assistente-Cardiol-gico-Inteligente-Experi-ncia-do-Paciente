# 🫀 CardioIA — Assistente Cardiológico Conversacional

Protótipo de chatbot de triagem inicial em saúde cardiovascular, desenvolvido para a
**Fase 5** do projeto **CardioIA**. Combina um assistente modelado no **IBM Watson
Assistant** (intents, entities e dialog nodes) com um backend **Flask** que expõe a
conversa em uma interface web simples.

> ⚠️ **Aviso**: este é um projeto acadêmico/educacional. O assistente não realiza
> diagnósticos e não substitui atendimento médico profissional.

---

## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como executar](#como-executar)
- [Configuração do Watson Assistant](#configuração-do-watson-assistant)
- [API](#api)
- [Modo simulado vs. modo Watson](#modo-simulado-vs-modo-watson)

---

## Visão geral

O usuário conversa em linguagem natural com o assistente para:

- Relatar sintomas cardiovasculares e receber orientação (com priorização automática
  de casos de possível emergência).
- Informar fatores de risco (hipertensão, diabetes, tabagismo, etc.).
- Tirar dúvidas sobre condições cardíacas (arritmia, cardiomegalia, insuficiência
  cardíaca, infarto) e exames (ECG, raio-X de tórax, ecocardiograma).
- Agendar uma consulta, com captura de nome e período preferido em turnos sucessivos
  (slot filling).
- Solicitar atendimento humano a qualquer momento.

## Funcionalidades

- 💬 Interface de chat responsiva (HTML/CSS/JS puro, sem frameworks).
- 🔁 Indicador de "digitando...", envio por Enter ou clique, bloqueio de entrada
  durante a espera da resposta.
- 🔍 Painel opcional de depuração exibindo a intent e as entidades detectadas em
  cada mensagem — útil para fins didáticos.
- 🤖 Backend com dois motores de resposta intercambiáveis: API real do Watson
  Assistant ou um simulador local baseado em palavras-chave (mesma árvore de
  diálogo), escolhido automaticamente conforme a presença de credenciais.

## Arquitetura

```
┌─────────────┐      HTTP (JSON)      ┌──────────────┐      AssistantV2 API      ┌───────────────────┐
│  Interface   │ ───────────────────▶ │  Flask app   │ ────────────────────────▶ │ IBM Watson         │
│  (HTML/JS)   │ ◀─────────────────── │  (app.py)    │ ◀──────────────────────── │ Assistant          │
└─────────────┘                       └──────┬───────┘                          └───────────────────┘
                                              │ (sem credenciais)
                                              ▼
                                       ┌──────────────┐
                                       │  Simulador   │
                                       │  local       │
                                       └──────────────┘
```

O backend abstrai a origem das respostas atrás de uma interface comum
(`create_session`, `send_welcome`, `send_message`, `delete_session`), de modo que a
interface web não precisa saber qual motor está respondendo.

## Estrutura do projeto

```
cardioia_fase5_parte1_chatbot/
├── app.py                        # Aplicação Flask e rotas da API
├── services/
│   ├── watson_service.py         # Integração real com IBM Watson Assistant (SDK oficial)
│   └── simulator_service.py      # Motor de simulação local (fallback sem credenciais)
├── templates/
│   └── index.html                # Interface de chat
├── static/
│   ├── style.css
│   └── chat.js
├── watson_assistant_skill.json   # Exportação da skill: intents, entities, dialog nodes
├── requirements.txt
├── .env.example                  # Modelo de variáveis de ambiente (credenciais Watson)
└── .gitignore
```

## Como executar

Pré-requisitos: Python 3.9+.

```bash
git clone <url-deste-repositorio>
cd cardioia_fase5_parte1_chatbot

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # opcional — veja a seção abaixo

python3 app.py
```

Acesse **http://127.0.0.1:5001**. Sem um arquivo `.env` preenchido, o servidor
inicia automaticamente em **modo simulado**, suficiente para testar todo o fluxo
de conversa sem depender de uma instância paga/ativa do Watson.

## Configuração do Watson Assistant

1. Crie um serviço **Watson Assistant** no [IBM Cloud](https://cloud.ibm.com).
2. Em **Assistants > Skills > Import skill**, importe o arquivo
   [`watson_assistant_skill.json`](./watson_assistant_skill.json) deste repositório.
3. Vincule a skill importada a um assistant e publique.
4. Em **Manage > API details**, copie a API Key e a Service URL.
5. Preencha o arquivo `.env` (a partir de `.env.example`):

   ```env
   WATSON_ASSISTANT_APIKEY=sua_api_key_aqui
   WATSON_ASSISTANT_URL=https://api.<região>.assistant.watson.cloud.ibm.com/instances/<instance_id>
   WATSON_ASSISTANT_ID=seu_assistant_id_aqui
   ```

6. Reinicie `python3 app.py` — o backend passa a usar a API real automaticamente,
   sem qualquer alteração de código.

## API

| Rota | Método | Descrição |
|---|---|---|
| `/` | GET | Renderiza a interface de chat |
| `/api/session` | POST | Cria uma sessão e retorna a mensagem de boas-vindas |
| `/api/message` | POST | Envia `{session_id, message}`, retorna resposta + intent + entidades |
| `/api/session/<id>` | DELETE | Encerra a sessão |

Exemplo de resposta de `/api/message`:

```json
{
  "respostas": ["Cardiomegalia é o aumento do tamanho do coração..."],
  "intent_detectada": "ask_condition_info",
  "confianca": 0.88,
  "entidades": [{"entidade": "condition", "valor": "cardiomegalia"}]
}
```

## Modo simulado vs. modo Watson

| | Modo simulado | Modo Watson |
|---|---|---|
| Requer credenciais | Não | Sim |
| Motor de NLU | Correspondência de palavras-chave (Python) | NLU real do Watson Assistant |
| Fluxo de diálogo | Idêntico (mesma árvore) | Idêntico (mesma árvore) |
| Uso recomendado | Desenvolvimento e demonstração | Avaliação de qualidade de NLU / produção |

---

Projeto acadêmico — CardioIA, Fase 5, Parte 1 e 2.
