let sessionId = null;

const janela = document.getElementById('chat-janela');
const form = document.getElementById('form-mensagem');
const campo = document.getElementById('campo-mensagem');
const botaoEnviar = document.getElementById('botao-enviar');
const badge = document.getElementById('modo-badge');
const chkDebug = document.getElementById('chk-debug');

function travarEntrada(travar) {
  campo.disabled = travar;
  botaoEnviar.disabled = travar;
  if (!travar) campo.focus();
}

function mostrarDigitando() {
  const div = document.createElement('div');
  div.className = 'mensagem bot digitando';
  div.id = 'indicador-digitando';
  div.innerHTML = '<span></span><span></span><span></span>';
  janela.appendChild(div);
  janela.scrollTop = janela.scrollHeight;
}

function removerDigitando() {
  document.getElementById('indicador-digitando')?.remove();
}

function adicionarMensagem(tipo, texto) {
  const div = document.createElement('div');
  div.className = 'mensagem ' + tipo;
  div.textContent = texto;
  janela.appendChild(div);
  janela.scrollTop = janela.scrollHeight;
}

function adicionarDebug(intent, confianca, entidades) {
  if (!chkDebug.checked) return;
  const partes = [];
  if (intent) {
    partes.push('intent: ' + intent + (confianca != null ? ' (' + confianca + ')' : ''));
  } else {
    partes.push('intent: nenhuma detectada (fallback)');
  }
  if (entidades && entidades.length) {
    partes.push('entidades: ' + entidades.map(e => e.entidade + '=' + e.valor).join(', '));
  }
  const div = document.createElement('div');
  div.className = 'debug-linha';
  div.textContent = partes.join(' · ');
  janela.appendChild(div);
  janela.scrollTop = janela.scrollHeight;
}

async function iniciarSessao() {
  try {
    const res = await fetch('/api/session', { method: 'POST' });
    const data = await res.json();

    if (data.error) {
      adicionarMensagem('erro', data.error);
      return;
    }

    sessionId = data.session_id;
    badge.textContent = data.modo_simulado ? 'Modo: Simulado' : 'Modo: Watson Assistant';
    (data.respostas || []).forEach(texto => adicionarMensagem('bot', texto));
  } catch (err) {
    adicionarMensagem('erro', 'Não foi possível conectar ao servidor.');
  } finally {
    travarEntrada(false);
  }
}

async function enviarMensagem(texto) {
  if (!sessionId) {
    adicionarMensagem('erro', 'Sessão não iniciada. Recarregue a página.');
    return;
  }

  travarEntrada(true);
  mostrarDigitando();

  try {
    const res = await fetch('/api/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: texto }),
    });
    const data = await res.json();

    removerDigitando();

    if (data.error) {
      adicionarMensagem('erro', data.error);
      return;
    }

    (data.respostas || []).forEach(t => adicionarMensagem('bot', t));
    adicionarDebug(data.intent_detectada, data.confianca, data.entidades);
  } catch (err) {
    removerDigitando();
    adicionarMensagem('erro', 'Falha de comunicação com o servidor.');
  } finally {
    travarEntrada(false);
  }
}

function submeterMensagemAtual() {
  const texto = campo.value.trim();
  if (!texto || campo.disabled) return;
  adicionarMensagem('user', texto);
  campo.value = '';
  enviarMensagem(texto);
}

form.addEventListener('submit', (evento) => {
  evento.preventDefault();
  submeterMensagemAtual();
});

// Reforço explícito: alguns navegadores/webviews não disparam o submit
// nativo do form ao pressionar Enter dentro do input.
campo.addEventListener('keydown', (evento) => {
  if (evento.key === 'Enter' && !evento.shiftKey) {
    evento.preventDefault();
    submeterMensagemAtual();
  }
});

travarEntrada(true);
iniciarSessao();
