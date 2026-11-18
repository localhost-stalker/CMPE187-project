class CanaryQwenAdapter:
    key = "canary"
    display_name = "Nvidia Canary-Qwen"

    def is_configured(self):
        return False

    def configuration_help(self):
        return (
            "Nvidia Canary-Qwen adapter is scaffolded but not connected yet. "
            "Add this model's API or local inference code inside models/canary_qwen.py."
        )

    def run(self, audio_path, prompt):
        raise NotImplementedError(self.configuration_help())
