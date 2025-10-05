from openai import OpenAI
from config.providers import get_provider_config
from prompts.tasks import get_task_prompt


class AIService:

    def __init__(self):
        self.client = None
        self.current_provider = None

    def _get_client(self, provider_name):
        config = get_provider_config(provider_name)

        if not config:
            raise ValueError(f"Proveedor '{provider_name}' no encontrado")

        if not config["api_key"]:
            raise ValueError(
                f"API key no configurada para {provider_name}. "
                "Por favor, agrega la clave en el archivo .env"
            )

        return OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )

    def process_task(self, provider, model, task, input_text, source_lang=None, target_lang=None):
        try:
            if not input_text or not input_text.strip():
                return "Por favor, ingresa un texto para procesar."

            client = self._get_client(provider)

            messages = get_task_prompt(task, input_text, source_lang, target_lang)

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )

            return response.choices[0].message.content

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error al procesar la solicitud: {str(e)}"


ai_service = AIService()