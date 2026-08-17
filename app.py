"""
Backend Flask do Assistente Cardiológico Conversacional (CardioIA - Fase 5, Parte 1).

Encaminha mensagens do usuário para o IBM Watson Assistant (AssistantV2) quando
as credenciais estão configuradas em variáveis de ambiente. Na ausência delas,
recorre automaticamente a um motor de simulação local (services/simulator_service.py)
que replica o mesmo fluxo de diálogo, permitindo demonstrar o protótipo sem
depender de uma instância paga/ativa do Watson.
"""

import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from services.watson_service import WatsonAssistantService
from services.simulator_service import SimulatedAssistant

load_dotenv()

app = Flask(__name__)

WATSON_API_KEY = os.environ.get('WATSON_ASSISTANT_APIKEY')
WATSON_URL = os.environ.get('WATSON_ASSISTANT_URL')
WATSON_ASSISTANT_ID = os.environ.get('WATSON_ASSISTANT_ID')


def _construir_engine():
    if WATSON_API_KEY and WATSON_URL and WATSON_ASSISTANT_ID:
        return WatsonAssistantService(WATSON_API_KEY, WATSON_URL, WATSON_ASSISTANT_ID)
    return SimulatedAssistant()


engine = _construir_engine()
MODO_SIMULADO = isinstance(engine, SimulatedAssistant)


@app.route('/')
def index():
    return render_template('index.html', modo_simulado=MODO_SIMULADO)


@app.route('/api/session', methods=['POST'])
def criar_sessao():
    try:
        session_id = engine.create_session()
        boas_vindas = engine.send_welcome(session_id)
    except Exception as exc:
        return jsonify({'error': f'Falha ao iniciar sessão: {exc}'}), 502

    return jsonify({
        'session_id': session_id,
        'modo_simulado': MODO_SIMULADO,
        'respostas': boas_vindas.get('respostas', []),
    })


@app.route('/api/message', methods=['POST'])
def enviar_mensagem():
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get('session_id')
    texto = (data.get('message') or '').strip()

    if not session_id or not texto:
        return jsonify({'error': 'session_id e message são obrigatórios.'}), 400

    try:
        resultado = engine.send_message(session_id, texto)
    except KeyError:
        return jsonify({'error': 'Sessão inválida ou expirada. Recarregue a página.'}), 404
    except Exception as exc:
        return jsonify({'error': f'Falha ao processar mensagem: {exc}'}), 502

    return jsonify(resultado)


@app.route('/api/session/<session_id>', methods=['DELETE'])
def encerrar_sessao(session_id):
    try:
        engine.delete_session(session_id)
    except Exception:
        pass
    return jsonify({'status': 'encerrado'})


if __name__ == '__main__':
    porta = int(os.environ.get('PORT', 5001))
    modo = 'SIMULADO (sem credenciais Watson)' if MODO_SIMULADO else 'WATSON ASSISTANT (API real)'
    print(f'\nCardioIA Chatbot iniciando em modo: {modo}')
    print(f'Acesse: http://127.0.0.1:{porta}\n')
    app.run(debug=True, port=porta)
