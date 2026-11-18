import base64
import os

from google import genai


class GeminiAdapter:
    key = "gemini"
    display_name = "Google Gemini 3.5 Flash-Lite"

    def __init__(self, model_name=None):
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def is_configured(self):
        return bool(os.getenv("GEMINI_API_KEY"))

    def configuration_help(self):
        return "Set GEMINI_API_KEY in your environment or .env file."

    def run(self, audio_path, prompt):
        if not self.is_configured():
            raise RuntimeError(self.configuration_help())

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        audio_data = base64.b64encode(audio_path.read_bytes()).decode("utf-8")

        interaction = client.interactions.create(
            model=self.model_name,
            input=[
                {"type": "text", "text": prompt},
                {
                    "type": "audio",
                    "data": audio_data,
                    "mime_type": "audio/wav",
                },
            ],
        )

        return interaction.output_text or ""
