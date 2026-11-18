class Qwen2AudioAdapter:
    key = "qwen2"
    display_name = "Qwen2-Audio"

    def is_configured(self):
        return False

    def configuration_help(self):
        return (
            "Qwen2-Audio adapter is scaffolded but not connected yet. "
            "Add this model's API or local inference code inside models/qwen2_audio.py."
        )

    def run(self, audio_path, prompt):
        raise NotImplementedError(self.configuration_help())
