"""OpenAI API key for superconductivity LLM scripts.

Prefer OPENAI_API_KEY in the environment. Optionally use a gitignored module
`openai_key_local.py` in this directory with `OPENAI_KEY = "sk-..."`.
"""

import os

OPENAI_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip() or None

if OPENAI_KEY is None:
    try:
        from utils.openai_key_local import OPENAI_KEY  # type: ignore
    except ImportError:
        pass

if not OPENAI_KEY:
    raise RuntimeError(
        "OpenAI API key not found. Either export OPENAI_API_KEY, or add "
        "superconductivity/utils/openai_key_local.py containing OPENAI_KEY = 'sk-...' "
        "(that file is gitignored)."
    )
