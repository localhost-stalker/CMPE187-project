class GeminiAdapter:
    key = "gemini"
    display_name = "Google Gemini"

    def is_configured(self):
        return False

    def configuration_help(self):
        return (
            "Google Gemini adapter is scaffolded but not connected yet. "
            "Add this model's API or local inference code inside models/gemini.py."
        )

    def run(self, audio_path, prompt):
        raise NotImplementedError(self.configuration_help())
