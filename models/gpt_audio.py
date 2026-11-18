import base64
import os

from openai import OpenAI


class GPTAudioAdapter:
    key = "gpt"
    display_name = "GPT-Audio-1.5"

    def __init__(self, model_name="gpt-audio-1.5"):
        self.model_name = model_name

    def is_configured(self):
        return bool(os.getenv("OPENAI_API_KEY"))

    def configuration_help(self):
        return "Set OPENAI_API_KEY in your environment or .env file."

    @staticmethod
    def _encode_audio(audio_path):
        with open(audio_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def run(self, audio_path, prompt):
        if not self.is_configured():
            raise RuntimeError(self.configuration_help())

        client = OpenAI()
        encoded_audio = self._encode_audio(audio_path)

        completion = client.chat.completions.create(
            model=self.model_name,
            modalities=["text"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": encoded_audio,
                                "format": "wav",
                            },
                        },
                    ],
                }
            ],
        )

        return completion.choices[0].message.content or ""
