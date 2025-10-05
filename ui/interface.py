import gradio as gr
from config.providers import get_all_providers, get_available_models
from prompts.tasks import get_all_tasks, AVAILABLE_LANGUAGES
from services.ai_service import ai_service


def update_models(provider):
    models = get_available_models(provider)
    return gr.Dropdown(choices=models, value=models[0] if models else None)


def update_translation_and_image_visibility(task):
    is_translation = (task == "Traducción")
    show_image = (task == "VQA")
    return (
        gr.Dropdown(visible=is_translation),
        gr.Dropdown(visible=is_translation),
        gr.Image(visible=show_image),
    )


def chat_function(message, history, provider, model, task, source_lang, target_lang, image_path):
    return ai_service.process_task(
        provider=provider,
        model=model,
        task=task,
        input_text=message,
        source_lang=source_lang,
        target_lang=target_lang,
        image_path=image_path,
    )


def create_interface():
    providers = get_all_providers()
    tasks = get_all_tasks()

    with gr.Blocks(title="Multi-Model AI Chat") as app:
        gr.Markdown("# Multi-Model AI Chat")

        with gr.Row():
            provider_dropdown = gr.Dropdown(
                choices=providers,
                value=providers[0] if providers else None,
                label="Proveedor"
            )
            model_dropdown = gr.Dropdown(
                choices=get_available_models(providers[0]) if providers else [],
                value=(get_available_models(providers[0])[0]
                       if providers and get_available_models(providers[0]) else None),
                label="Modelo"
            )
            task_dropdown = gr.Dropdown(
                choices=tasks,
                value=tasks[0] if tasks else None,
                label="Tarea"
            )

        with gr.Row():
            source_lang = gr.Dropdown(
                choices=AVAILABLE_LANGUAGES,
                value="español",
                label="Idioma origen",
                visible=True
            )
            target_lang = gr.Dropdown(
                choices=AVAILABLE_LANGUAGES,
                value="inglés",
                label="Idioma destino",
                visible=True
            )

        # ¡IMPORTANTE! Crear image_input ANTES de usarlo en .change(...)
        image_input = gr.Image(
            label="Imagen para VQA",
            type="filepath",
            visible=False
        )

        gr.ChatInterface(
            fn=chat_function,
            additional_inputs=[
                provider_dropdown,
                model_dropdown,
                task_dropdown,
                source_lang,
                target_lang,
                image_input,
            ],
        )

        provider_dropdown.change(
            fn=update_models,
            inputs=[provider_dropdown],
            outputs=[model_dropdown]
        )

        task_dropdown.change(
            fn=update_translation_and_image_visibility,
            inputs=[task_dropdown],
            outputs=[source_lang, target_lang, image_input]
        )

    return app
