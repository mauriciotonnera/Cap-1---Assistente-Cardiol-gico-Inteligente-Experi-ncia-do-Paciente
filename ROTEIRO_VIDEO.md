# Roteiro — Vídeo de Demonstração (≤ 3 min)

Antes de gravar: rode `python3 app.py` e abra `http://127.0.0.1:5001` no navegador.
Use o **Cmd+Shift+5** (macOS) para gravar a tela, ou o QuickTime Player
(Arquivo > Nova Gravação de Tela).

Marque o checkbox **"Mostrar detalhes técnicos"** antes de começar — assim o
painel de intent/entidade aparece em todas as respostas, o que ajuda a mostrar
o NLP funcionando sem precisar narrar cada detecção.

---

### 00:00–00:15 — Abertura
**Fala sugerida:**
> "Este é o CardioIA, um assistente cardiológico conversacional. Ele foi modelado
> no IBM Watson Assistant — com intents, entities e dialog nodes — e está
> integrado a um backend em Flask com uma interface de chat."

**Tela:** página inicial carregada, mensagem de boas-vindas visível.

---

### 00:15–00:40 — Sintoma + fator de risco
**Digitar:** `tenho sentido palpitações e também fumo bastante`

**Fala sugerida:**
> "Ele reconhece fatores de risco relatados em linguagem natural — aqui,
> tabagismo — e recomenda acompanhamento médico. Reparem no painel de baixo:
> mostra a intent e a entidade que o motor de NLP identificou."

---

### 00:40–01:00 — Emergência (o ponto mais importante do fluxo)
**Digitar:** `acho que estou tendo um infarto`

**Fala sugerida:**
> "Sintomas agudos são priorizados automaticamente. O fluxo interrompe
> qualquer assunto em andamento e orienta buscar ajuda de emergência
> imediatamente — isso está configurado no dialog node com prioridade máxima
> no Watson Assistant."

---

### 01:00–01:20 — Pergunta sobre uma condição
**Digitar:** `o que é cardiomegalia`

**Fala sugerida:**
> "Também respondo dúvidas sobre condições e exames cardiológicos — cada uma
> mapeada para uma entidade específica reconhecida pelo assistente."

---

### 01:20–01:55 — Agendamento com slot-filling
**Digitar em sequência:**
1. `quero marcar uma consulta`
2. `Maria Silva` (quando perguntado o nome)
3. `de manhã` (quando perguntado o período)

**Fala sugerida:**
> "O agendamento usa slot-filling: o assistente pede o nome e o período em
> turnos separados, guarda essas informações no contexto da conversa, e só
> confirma quando os dois estão preenchidos."

---

### 01:55–02:25 — Estrutura do projeto (panorâmica rápida do código)
**Tela:** abrir o editor de código e mostrar rapidamente:
- `app.py` (rotas Flask)
- `services/watson_service.py` e `services/simulator_service.py`
- `watson_assistant_skill.json`

**Fala sugerida:**
> "No backend, o Flask escolhe automaticamente entre a API real do Watson
> Assistant ou um simulador local, dependendo de credenciais configuradas em
> variáveis de ambiente. A skill completa — os 10 intents, as 5 entities e os
> 21 dialog nodes — está exportada em JSON no repositório, pronta para
> importar no Watson Assistant."

*(Se você tiver uma instância do Watson Assistant configurada, esse é o
melhor momento para trocar de tela e mostrar rapidamente o canvas de dialog
nodes lá dentro.)*

---

### 02:25–02:50 — Encerramento
**Digitar:** `obrigado`

**Fala sugerida:**
> "Esse é o protótipo do CardioIA: um exemplo de como IA conversacional pode
> apoiar — sem nunca substituir — o atendimento médico. Código completo no
> repositório do GitHub, no link da descrição."

---

**Dica:** grave em duas ou três tomadas curtas (ex: abertura+sintomas,
emergência+condição, agendamento+encerramento) e corte no QuickTime/iMovie se
errar alguma fala — é mais fácil que tentar acertar tudo em uma tomada só.
