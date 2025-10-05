
from openai import OpenAI
import time
import os
import base64
import mimetypes

from config.providers import get_provider_config, get_available_models
from prompts.tasks import get_task_prompt


class AIService:
    def __init__(self):
        self.client = None
        self.current_provider = None

    def _get_client(self, provider_name: str) -> OpenAI:
        # Reuse client if same provider
        if self.client is not None and self.current_provider == provider_name:
            return self.client

        config = get_provider_config(provider_name)
        base_url = config.get("base_url")
        api_key = config.get("api_key")

        if not api_key:
            raise ValueError(f"Falta API key para el proveedor: {provider_name}")
        if not base_url:
            raise ValueError(f"Falta base_url para el proveedor: {provider_name}")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.current_provider = provider_name
        return self.client

    def _encode_image_as_data_url(self, image_path: str) -> str:
        mime, _ = mimetypes.guess_type(image_path)
        if not mime:
            mime = "image/png"
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def process_task(
        self,
        provider: str,
        model: str,
        task: str,
        input_text: str,
        source_lang: str = None,
        target_lang: str = None,
        image_path: str = None,
        timeout_sec: float = 30.0,
    ) -> str:
        # Validaciones de entrada
        if not task:
            return "Error: no se especificó la tarea."
        if not input_text or not str(input_text).strip():
            return "Por favor, ingresa un texto para procesar."

        # Verificar modelo disponible
        available = get_available_models(provider)
        if model not in available:
            return (
                f"Error: el modelo '{model}' no está disponible para el proveedor {provider}. "
                f"Modelos disponibles: {', '.join(available) if available else 'ninguno'}."
            )

        try:
            client = self._get_client(provider)
            # Construir mensajes base
            messages = get_task_prompt(task, input_text, source_lang, target_lang)

            # VQA: anexar imagen si se proporcionó
            if task == "VQA" and image_path:
                try:
                    data_url = self._encode_image_as_data_url(image_path)
                    last_content = messages[-1]["content"]
                    # Soportar tanto string como lista en el último contenido
                    if isinstance(last_content, list):
                        content_list = last_content
                    else:
                        content_list = [{"type": "text", "text": last_content}]
                    content_list.append({"type": "input_image", "image_url": {"url": data_url}})
                    messages[-1]["content"] = content_list
                except Exception:
                    # Si falla el procesado de imagen, seguimos con solo texto
                    pass

            # Timeout (si el SDK lo soporta)
            try:
                client = client.with_options(timeout=timeout_sec)
            except Exception:
                pass

            start_time = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            elapsed_ms = int((time.time() - start_time) * 1000)

            content = ""
            try:
                content = response.choices[0].message.content
            except Exception:
                content = ""

            suffix = f"\n\n⏱️ Tiempo de inferencia: {elapsed_ms} ms"
            return (content or "(respuesta vacía)") + suffix

        except ValueError as e:
            return f"Error: {str(e)}"
        except TimeoutError:
            return "Error: la solicitud excedió el tiempo máximo de espera."
        except Exception as e:
            msg = str(e)
            if "model_not_found" in msg or "does not exist" in msg:
                return "Error: el modelo solicitado no está disponible ahora mismo."
            if "rate limit" in msg.lower():
                return "Error: límite de peticiones alcanzado. Intenta de nuevo en unos segundos."
            return f"Error al procesar la solicitud: {msg}"


ai_service = AIService()
