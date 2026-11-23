import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


DEFAULT_MODEL_ID = "nvidia/canary-qwen-2.5b"

# Hard-coded ASR-mode request; the test prompt is only used in LLM mode.
TRANSCRIBE_REQUEST = "Transcribe the following: {audio_tag}"

# Qwen3 soft switch: skip <think> reasoning in LLM mode (faster, no truncation).
NO_THINK_SWITCH = "/no_think"


class CanaryQwenAdapter:
    key = "canary"
    display_name = "Nvidia Canary-Qwen"

    def __init__(self, model_name=DEFAULT_MODEL_ID, device=None):
        self.model_name = model_name
        self.device = device
        # NeMo/torch are imported and the model is loaded on the first run()
        # call, so building the adapter registry never requires NeMo.
        self.model = None

    def is_configured(self):
        # Always attempt to run; a missing NeMo install surfaces as an
        # ImportError on run(), which run_tests.py records as an Error row.
        return True

    def configuration_help(self):
        return (
            "Canary-Qwen requires NeMo with speechlm2 support. "
            "Install dependencies from requirements.txt."
        )

    def _load_model(self):
        if self.model is not None:
            return

        try:
            from nemo.collections.speechlm2.models import SALM
        except ImportError as exc:
            raise ImportError(
                "Canary-Qwen requires NeMo with speechlm2 support. "
                "Install dependencies from requirements.txt."
            ) from exc

        import torch

        self.device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SALM.from_pretrained(self.model_name).eval().to(self.device)

    def _decode(self, token_ids):
        return self.model.tokenizer.ids_to_text(token_ids.cpu()).strip()

    @staticmethod
    @contextmanager
    def _mono_audio(path):
        """Yield a path to mono audio; Canary-Qwen fails on multi-channel input.

        Mono files are passed through unchanged. Multi-channel files are
        averaged down to one channel in a temporary WAV that is deleted after use.
        """
        import soundfile as sf

        if sf.info(str(path)).channels == 1:
            yield path
            return

        data, sample_rate = sf.read(str(path), always_2d=True)
        fd, tmp_name = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            sf.write(tmp_name, data.mean(axis=1), sample_rate)
            yield Path(tmp_name)
        finally:
            os.remove(tmp_name)

    def _transcribe(self, audio_path, max_new_tokens=256):
        """ASR mode: audio + hard-coded transcription request."""
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(f"Audio file not found: {path}")

        with self._mono_audio(path) as mono_path:
            prompts = [[
                {
                    "role": "user",
                    "content": TRANSCRIBE_REQUEST.format(
                        audio_tag=self.model.audio_locator_tag
                    ),
                    "audio": [str(mono_path)],
                }
            ]]
            output = self.model.generate(prompts=prompts, max_new_tokens=max_new_tokens)
        return self._decode(output[0])

    def _ask(self, prompt, max_new_tokens=512):
        """LLM mode: text-only prompt with the speech adapter disabled."""
        if not prompt or not prompt.strip():
            raise ValueError("prompt must not be empty")

        with self.model.llm.disable_adapter():
            output = self.model.generate(
                prompts=[[{"role": "user", "content": prompt}]],
                max_new_tokens=max_new_tokens,
            )
        return self._extract_answer(self._decode(output[0]))

    @staticmethod
    def _extract_answer(text):
        """Keep only the final answer from an LLM-mode generation.

        The decoded output echoes the chat ("user\\n<prompt>\\nassistant\\n")
        and includes Qwen3's <think>...</think> reasoning before the answer.
        """
        if "</think>" in text:
            return text.rsplit("</think>", 1)[1].strip()

        # No closing tag: drop the echoed chat turn if present.
        marker = "\nassistant\n"
        if marker in text:
            text = text.rsplit(marker, 1)[1]

        # Reasoning that never closed (hit max_new_tokens) has no final answer.
        if text.lstrip().startswith("<think>"):
            return ""
        return text.strip()

    def run(self, audio_path, prompt):
        self._load_model()

        import torch

        with torch.inference_mode():
            transcript = self._transcribe(audio_path)
            if not transcript:
                # No speech recognized: skip LLM mode so the grader records a Fail.
                return ""

            return self._ask(self._build_llm_prompt(prompt, transcript))

    @staticmethod
    def _build_llm_prompt(prompt, transcript):
        return f"{prompt}\n\nTranscript: {transcript}\n\n{NO_THINK_SWITCH}"
