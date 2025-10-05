TASK_PROMPTS = {
    "Traducción": {
        "system": "Eres un traductor profesional. Tu tarea es traducir el texto del usuario del idioma de origen al idioma destino solicitado. Proporciona SOLO la traducción, sin explicaciones adicionales.",
        "user_template": "Traduce el siguiente texto de {source_lang} a {target_lang}:\n\n{text}"
    },
    "Resumen": {
        "system": "Eres un asistente experto en resumir textos. Proporciona resúmenes concisos y precisos que capturen las ideas principales.",
        "user_template": "Resume el siguiente texto de manera concisa:\n\n{text}"
    }
}

AVAILABLE_LANGUAGES = [
    "español",
    "inglés",
    "francés",
    "alemán",
    "italiano",
    "portugués",
    "chino",
    "japonés"
]


def get_task_prompt(task_name, input_text, source_lang=None, target_lang=None):
    if task_name not in TASK_PROMPTS:
        raise ValueError(f"Tarea '{task_name}' no encontrada")

    task_config = TASK_PROMPTS[task_name]

    if task_name == "Traducción":
        if not source_lang:
            source_lang = "inglés"
        if not target_lang:
            target_lang = "español"
        user_message = task_config["user_template"].format(
            source_lang=source_lang,
            target_lang=target_lang,
            text=input_text
        )
    else:
        user_message = task_config["user_template"].format(text=input_text)

    return [
        {"role": "system", "content": task_config["system"]},
        {"role": "user", "content": user_message}
    ]


def get_all_tasks():
    return list(TASK_PROMPTS.keys())