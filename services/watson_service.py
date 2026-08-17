"""Integração real com a API do IBM Watson Assistant (AssistantV2)."""

from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class WatsonAssistantService:

    def __init__(self, api_key: str, url: str, assistant_id: str, version: str = '2023-06-15'):
        authenticator = IAMAuthenticator(api_key)
        self.assistant = AssistantV2(version=version, authenticator=authenticator)
        self.assistant.set_service_url(url)
        self.assistant_id = assistant_id

    def create_session(self) -> str:
        response = self.assistant.create_session(assistant_id=self.assistant_id).get_result()
        return response['session_id']

    def send_welcome(self, session_id: str) -> dict:
        response = self.assistant.message(
            assistant_id=self.assistant_id,
            session_id=session_id,
            input={'message_type': 'text', 'text': ''},
        ).get_result()
        return self._formatar_resposta(response)

    def send_message(self, session_id: str, text: str) -> dict:
        response = self.assistant.message(
            assistant_id=self.assistant_id,
            session_id=session_id,
            input={
                'message_type': 'text',
                'text': text,
                'options': {'return_context': True},
            },
        ).get_result()
        return self._formatar_resposta(response)

    def delete_session(self, session_id: str) -> None:
        self.assistant.delete_session(assistant_id=self.assistant_id, session_id=session_id)

    @staticmethod
    def _formatar_resposta(response: dict) -> dict:
        mensagens = [
            item.get('text', '')
            for item in response.get('output', {}).get('generic', [])
            if item.get('response_type') == 'text'
        ]
        intents = response.get('output', {}).get('intents', [])
        entities = response.get('output', {}).get('entities', [])

        return {
            'respostas': mensagens,
            'intent_detectada': intents[0]['intent'] if intents else None,
            'confianca': round(intents[0]['confidence'], 3) if intents else None,
            'entidades': [{'entidade': e['entity'], 'valor': e['value']} for e in entities],
        }
