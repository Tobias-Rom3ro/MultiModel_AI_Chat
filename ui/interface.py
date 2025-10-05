import gradio as gr
from config.providers import get_all_providers, get_available_models
from prompts.tasks import get_all_tasks, AVAILABLE_LANGUAGES
from services.ai_service import ai_service


def update_models(provider):
    models = get_available_models(provider)
    return gr.Dropdown(choices=models, value=models[0] if models else None)


def update_translation_visibility(task):
    is_translation = (task == "Traducción")
    return gr.Dropdown(visible=is_translation), gr.Dropdown(visible=is_translation)


def chat_function(message, history, provider, model, task, source_lang, target_lang):
    response = ai_service.process_task(
        provider=provider,
        model=model,
        task=task,
        input_text=message,
        source_lang=source_lang,
        target_lang=target_lang
    )

    return response


def create_interface():
    initial_provider = "OpenRouter AI"
    initial_models = get_available_models(initial_provider)
    initial_model = initial_models[0] if initial_models else None

    with gr.Blocks(title="Multi-Model AI Chat", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 💬 Multi-Model AI Chat
            Chatea con diferentes modelos de IA para realizar traducciones y resúmenes.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Configuración")

                provider_dropdown = gr.Dropdown(
                    choices=list(get_all_providers()),
                    value=initial_provider,
                    label="Proveedor",
                    info="Selecciona el proveedor de IA"
                )

                model_dropdown = gr.Dropdown(
                    choices=initial_models,
                    value=initial_model,
                    label="Modelo",
                    info="Selecciona el modelo a usar"
                )

                task_dropdown = gr.Dropdown(
                    choices=list(get_all_tasks()),
                    value="Traducción",
                    label="Tarea",
                    info="Selecciona la tarea a realizar"
                )

                source_lang = gr.Dropdown(
                    choices=AVAILABLE_LANGUAGES,
                    value="español",
                    label="Idioma de origen",
                    visible=True
                )

                target_lang = gr.Dropdown(
                    choices=AVAILABLE_LANGUAGES,
                    value="inglés",
                    label="Idioma destino",
                    visible=True
                )

            with gr.Column(scale=2):

                chatbot = gr.ChatInterface(
                    fn=chat_function,
                    textbox=gr.Textbox(
                        placeholder="Escribe tu mensaje aquí...",
                        container=False,
                        scale=7
                    ),
                    type="messages",
                    submit_btn="Enviar",
                    additional_inputs=[
                        provider_dropdown,
                        model_dropdown,
                        task_dropdown,
                        source_lang,
                        target_lang
                    ]
                )

        provider_dropdown.change(
            fn=update_models,
            inputs=[provider_dropdown],
            outputs=[model_dropdown]
        )

        task_dropdown.change(
            fn=update_translation_visibility,
            inputs=[task_dropdown],
            outputs=[source_lang, target_lang]
        )

    return app