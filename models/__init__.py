from .gpt_audio import GPTAudioAdapter
from .gemini import GeminiAdapter
from .qwen2_audio import Qwen2AudioAdapter
from .canary_qwen import CanaryQwenAdapter


def get_model_adapters():
    return {
        "gpt": GPTAudioAdapter(),
        "gemini": GeminiAdapter(),
        "qwen2": Qwen2AudioAdapter(),
        "canary": CanaryQwenAdapter(),
    }
