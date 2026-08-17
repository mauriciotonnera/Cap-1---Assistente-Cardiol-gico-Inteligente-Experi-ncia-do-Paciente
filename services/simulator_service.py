"""
Motor de simulação local do fluxo de diálogo.

Replica em Python a mesma árvore de intents/entities/dialog nodes descrita em
watson_assistant_skill.json, permitindo executar e demonstrar o protótipo sem
depender de credenciais do IBM Watson Assistant.
"""

import uuid
from typing import Optional

TXT_WELCOME = ("Olá! \U0001F44B Eu sou o assistente virtual do CardioIA. Posso te ajudar a entender "
               "sintomas, fatores de risco, exames cardiológicos e agendar consultas. Importante: "
               "não realizo diagnósticos — em caso de emergência, ligue imediatamente para o SAMU (192). "
               "Como posso te ajudar hoje?")

TXT_EMERGENCY = ("\U0001F6A8 Os sintomas que você descreveu podem indicar uma emergência cardíaca. "
                  "Por favor, ligue AGORA para o SAMU (192) ou vá ao pronto-socorro mais próximo. "
                  "Não continue este atendimento — busque ajuda médica imediata.")

TXT_GREETING = ("Olá! Como posso te ajudar hoje? Posso falar sobre sintomas, fatores de risco, "
                 "exames ou agendar uma consulta.")

TXT_ESCALATE = ("Claro, vou te direcionar para um de nossos atendentes humanos. Você pode falar "
                 "conosco pelo telefone (11) 4000-0000 ou pelo WhatsApp (11) 90000-0000, das 8h às "
                 "20h em dias úteis.")

TXT_THANKS = "Por nada! Fico à disposição sempre que precisar. \U0001F499"

TXT_GOODBYE = ("Até logo! Cuide bem do seu coração. Lembre-se: este assistente é um apoio informativo "
                "e não substitui uma consulta médica presencial. \U0001FAC0")

TXT_ANYTHING_ELSE = [
    "Desculpe, não entendi. Posso ajudar com sintomas, fatores de risco, condições, exames ou "
    "agendamento. Pode reformular?",
    "Ainda não consegui entender. Que tal falar com um de nossos atendentes humanos? Digite "
    "'falar com atendente' para isso.",
]

TXT_CONDITION_DEFAULT = ("Posso te explicar sobre: arritmia, cardiomegalia, insuficiência cardíaca ou "
                          "infarto. Sobre qual dessas condições você gostaria de saber mais?")
TXT_EXAM_DEFAULT = ("Posso explicar sobre: eletrocardiograma, raio-X de tórax ou ecocardiograma. "
                     "Qual desses exames você gostaria de entender melhor?")

CONDICOES = {
    "arritmia": ("Arritmia é uma alteração no ritmo dos batimentos cardíacos — o coração pode bater "
                 "rápido demais (taquicardia), devagar demais (bradicardia) ou de forma irregular. "
                 "Pode ser benigna ou exigir tratamento, dependendo da causa."),
    "cardiomegalia": ("Cardiomegalia é o aumento do tamanho do coração, identificável em radiografias "
                       "de tórax. Pode ser consequência de hipertensão, doença valvar ou insuficiência "
                       "cardíaca, entre outras causas."),
    "insuficiencia_cardiaca": ("Insuficiência cardíaca ocorre quando o coração não consegue bombear "
                                "sangue de forma eficiente para atender às necessidades do corpo. "
                                "Sintomas comuns incluem falta de ar e inchaço nas pernas."),
    "infarto": ("O infarto (ataque cardíaco) acontece quando o fluxo de sangue para uma parte do "
                "coração é bloqueado, geralmente por um coágulo. É uma emergência médica — se você "
                "está com esse sintoma agora, procure ajuda imediatamente (SAMU 192)."),
}

EXAMES = {
    "eletrocardiograma": ("O eletrocardiograma (ECG) registra a atividade elétrica do coração e ajuda "
                           "a identificar arritmias, isquemias e outras alterações. É rápido e indolor."),
    "raio_x_torax": ("O raio-X de tórax permite visualizar o tamanho e formato do coração e pulmões, "
                      "auxiliando a identificar cardiomegalia, derrames e infiltrações."),
    "ecocardiograma": ("O ecocardiograma usa ultrassom para avaliar a estrutura e o funcionamento do "
                        "coração em tempo real, incluindo válvulas e câmaras cardíacas."),
}

INTENT_KEYWORDS = [
    # Ordem importa: emergência é checada primeiro, como no dialog tree do Watson.
    ("emergency_symptoms", ["infarto", "não consigo respirar", "nao consigo respirar",
                             "dor muito forte", "dor insuportável", "dor insuportavel",
                             "socorro", "passando muito mal", "emergencia", "emergência"]),
    ("greeting", ["bom dia", "boa tarde", "boa noite", "oi", "olá", "ola", "e aí", "comecar", "começar"]),
    ("goodbye", ["tchau", "até logo", "ate logo", "encerrar", "vou sair", "por hoje é só"]),
    ("thanks", ["obrigad", "valeu", "agradeç", "agradec"]),
    ("risk_factors", ["pressão alta", "pressao alta", "hipertens", "diabet", "fumo", "fumante",
                       "obesidade", "acima do peso", "histórico", "historico", "colesterol", "sedentari"]),
    ("ask_condition_info", ["o que é", "o que e", "me explica", "explique", "significa", "não sei o que"]),
    ("ask_exam_info", ["eletrocardiograma", "ecg", "raio-x", "raio x", "ecocardiograma", "exame"]),
    ("schedule_appointment", ["marcar", "agendar", "agendamento"]),
    ("escalate_human", ["falar com atendente", "atendente", "pessoa de verdade", "humano", "falar com alguém"]),
    ("general_symptoms", ["dor no peito", "palpita", "falta de ar", "tontura", "fadiga", "cansaço",
                           "cansaco", "inchaço", "inchaco", "suor frio", "aperto no peito"]),
]

CONDITION_KEYWORDS = {
    "arritmia": ["arritmia"],
    "cardiomegalia": ["cardiomegalia"],
    "insuficiencia_cardiaca": ["insuficiência cardíaca", "insuficiencia cardiaca", "insuficiencia"],
    "infarto": ["infarto", "ataque cardíaco", "ataque cardiaco"],
}

EXAM_KEYWORDS = {
    "eletrocardiograma": ["eletrocardiograma", "ecg", "eletro"],
    "raio_x_torax": ["raio-x", "raio x", "radiografia", "rx de tórax", "rx de torax"],
    "ecocardiograma": ["ecocardiograma", "eco do coração", "eco do coracao", "ecocardiografia"],
}

SYMPTOM_KEYWORDS = {
    "dor_no_peito": ["dor no peito", "aperto no peito", "peso no peito"],
    "palpitacoes": ["palpita", "coração acelerado", "coracao acelerado", "batedeira"],
    "falta_de_ar": ["falta de ar", "dificuldade para respirar", "respiração curta"],
    "tontura": ["tontura", "vertigem", "cabeça leve"],
    "fadiga": ["fadiga", "cansaço extremo", "cansaco extremo", "fraqueza"],
    "inchaco_pernas": ["inchaço nas pernas", "inchaco nas pernas", "pernas inchadas", "pés inchados"],
    "suor_frio": ["suor frio", "suando frio"],
}

RISK_KEYWORDS = {
    "hipertensao": ["pressão alta", "pressao alta", "hipertens"],
    "diabetes": ["diabet", "açúcar alto", "acucar alto"],
    "tabagismo": ["fumo", "fumante", "cigarro"],
    "obesidade": ["obesidade", "acima do peso", "sobrepeso"],
    "historico_familiar": ["histórico familiar", "historico familiar", "histórico na família", "caso na família"],
    "colesterol_alto": ["colesterol"],
}

PERIODOS = {
    "manha": ["manhã", "manha", "de manhã", "de manha"],
    "tarde": ["tarde"],
    "noite": ["noite"],
}

PERIODOS_EXIBICAO = {
    "manha": "manhã",
    "tarde": "tarde",
    "noite": "noite",
}


def _detectar_por_dicionario(texto_norm: str, dicionario: dict) -> Optional[str]:
    for valor, chaves in dicionario.items():
        if any(chave in texto_norm for chave in chaves):
            return valor
    return None


class SimulatedAssistant:
    """Motor de diálogo local baseado em correspondência de palavras-chave."""

    def __init__(self):
        self.sessions: dict[str, dict] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'count_fallback': 0,
            'aguardando': None,
            'appointment_name': None,
            'appointment_period': None,
        }
        return session_id

    def send_welcome(self, session_id: str) -> dict:
        return self._resultado([TXT_WELCOME], 'welcome', 1.0, [])

    def send_message(self, session_id: str, text: str) -> dict:
        if session_id not in self.sessions:
            raise KeyError('Sessão inválida ou expirada.')

        estado = self.sessions[session_id]
        texto_norm = text.lower().strip()

        if estado['aguardando'] == 'nome':
            return self._preencher_nome(estado, text)
        if estado['aguardando'] == 'periodo':
            return self._preencher_periodo(estado, texto_norm)

        intent = self._detectar_intent(texto_norm)

        despachantes = {
            'emergency_symptoms': self._h_emergencia,
            'greeting': self._h_saudacao,
            'goodbye': self._h_despedida,
            'thanks': self._h_agradecimento,
            'general_symptoms': self._h_sintomas,
            'risk_factors': self._h_fatores_risco,
            'ask_condition_info': self._h_condicao,
            'ask_exam_info': self._h_exame,
            'schedule_appointment': self._h_agendar,
            'escalate_human': self._h_escalar,
        }

        if intent is None:
            return self._h_fallback(estado)

        estado['count_fallback'] = 0
        return despachantes[intent](estado, texto_norm)

    def delete_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)

    # ── Detecção ─────────────────────────────────────────────────────────────
    @staticmethod
    def _detectar_intent(texto_norm: str) -> Optional[str]:
        for intent, chaves in INTENT_KEYWORDS:
            if any(chave in texto_norm for chave in chaves):
                return intent
        return None

    @staticmethod
    def _resultado(respostas, intent, confianca, entidades):
        return {
            'respostas': respostas,
            'intent_detectada': intent,
            'confianca': confianca,
            'entidades': entidades,
        }

    # ── Handlers ─────────────────────────────────────────────────────────────
    def _h_emergencia(self, estado, texto_norm):
        return self._resultado([TXT_EMERGENCY], 'emergency_symptoms', 0.95, [])

    def _h_saudacao(self, estado, texto_norm):
        return self._resultado([TXT_GREETING], 'greeting', 0.9, [])

    def _h_despedida(self, estado, texto_norm):
        return self._resultado([TXT_GOODBYE], 'goodbye', 0.9, [])

    def _h_agradecimento(self, estado, texto_norm):
        return self._resultado([TXT_THANKS], 'thanks', 0.9, [])

    def _h_sintomas(self, estado, texto_norm):
        sintoma = _detectar_por_dicionario(texto_norm, SYMPTOM_KEYWORDS) or 'sintoma_nao_especificado'
        resposta = (
            f"Entendo que você está sentindo {sintoma.replace('_', ' ')}. É importante não ignorar "
            "esse tipo de sinal. Se o sintoma for intenso, súbito ou vier acompanhado de falta de ar, "
            "dor irradiando para o braço ou suor frio, procure atendimento de emergência imediatamente. "
            "Caso contrário, recomendo agendar uma consulta para avaliação. Deseja agendar agora?"
        )
        entidades = [{'entidade': 'symptom', 'valor': sintoma}] if sintoma != 'sintoma_nao_especificado' else []
        return self._resultado([resposta], 'general_symptoms', 0.82, entidades)

    def _h_fatores_risco(self, estado, texto_norm):
        fator = _detectar_por_dicionario(texto_norm, RISK_KEYWORDS) or 'fator_nao_especificado'
        resposta = (
            f"Obrigado por compartilhar essa informação sobre {fator.replace('_', ' ')}. Fatores de "
            "risco cardiovascular merecem atenção contínua e acompanhamento médico regular. Recomendo "
            "conversar com um cardiologista para uma avaliação personalizada. Posso te ajudar a agendar "
            "uma consulta?"
        )
        entidades = [{'entidade': 'risk_factor', 'valor': fator}] if fator != 'fator_nao_especificado' else []
        return self._resultado([resposta], 'risk_factors', 0.82, entidades)

    def _h_condicao(self, estado, texto_norm):
        condicao = _detectar_por_dicionario(texto_norm, CONDITION_KEYWORDS)
        if condicao:
            return self._resultado(
                [CONDICOES[condicao]], 'ask_condition_info', 0.88,
                [{'entidade': 'condition', 'valor': condicao}]
            )
        return self._resultado([TXT_CONDITION_DEFAULT], 'ask_condition_info', 0.75, [])

    def _h_exame(self, estado, texto_norm):
        exame = _detectar_por_dicionario(texto_norm, EXAM_KEYWORDS)
        if exame:
            return self._resultado(
                [EXAMES[exame]], 'ask_exam_info', 0.88,
                [{'entidade': 'exam', 'valor': exame}]
            )
        return self._resultado([TXT_EXAM_DEFAULT], 'ask_exam_info', 0.75, [])

    def _h_agendar(self, estado, texto_norm):
        estado['aguardando'] = 'nome'
        return self._resultado(
            ['Para começar o agendamento, qual é o seu nome completo?'],
            'schedule_appointment', 0.85, []
        )

    def _preencher_nome(self, estado, texto_original):
        nome = texto_original.strip().title()
        estado['appointment_name'] = nome
        estado['aguardando'] = 'periodo'
        return self._resultado(
            [f'Obrigado, {nome}! Você prefere o período da manhã, tarde ou noite?'],
            'schedule_appointment', 0.9,
            [{'entidade': 'sys-person', 'valor': nome}]
        )

    def _preencher_periodo(self, estado, texto_norm):
        periodo = _detectar_por_dicionario(texto_norm, PERIODOS)
        if not periodo:
            return self._resultado(
                ['Não entendi o período. Você prefere manhã, tarde ou noite?'],
                'schedule_appointment', 0.6, []
            )
        estado['appointment_period'] = periodo
        nome = estado['appointment_name']
        resposta = (
            f"Perfeito, {nome}! Pré-agendei sua consulta para o período da "
            f"{PERIODOS_EXIBICAO[periodo]}. Nossa equipe entrará em contato em breve para confirmar "
            "data e horário exatos. \U0001F4C5"
        )
        estado['aguardando'] = None
        estado['appointment_name'] = None
        estado['appointment_period'] = None
        return self._resultado(
            [resposta], 'schedule_appointment', 0.9,
            [{'entidade': 'period', 'valor': periodo}]
        )

    def _h_escalar(self, estado, texto_norm):
        return self._resultado([TXT_ESCALATE], 'escalate_human', 0.9, [])

    def _h_fallback(self, estado):
        estado['count_fallback'] += 1
        indice = min(estado['count_fallback'] - 1, len(TXT_ANYTHING_ELSE) - 1)
        return self._resultado([TXT_ANYTHING_ELSE[indice]], None, None, [])
