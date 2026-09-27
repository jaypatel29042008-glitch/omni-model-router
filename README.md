# omni-model-router

> Test, benchmark, and auto-select the best free AI model from [OpenRouter](https://openrouter.ai) — zero dependencies, pure Python.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Compatible-FF6600.svg)](https://openrouter.ai)

## Why?

OpenRouter gives you access to **500+ AI models** through one API, including many **completely free** models. But free models go up and down — rate limits hit, providers go offline, latency varies.

**omni-model-router** solves this by:
- 🔍 **Testing** which free models are actually responding right now
- ⚡ **Benchmarking** latency across all available free models in parallel
- 🎯 **Auto-selecting** the fastest working model for you
- ✅ **Validating** your API key and checking usage/limits

Zero dependencies. Pure Python stdlib. Works everywhere.

## Quick Start

```bash
# Clone
git clone https://github.com/jaypatel29042008-glitch/omni-model-router.git
cd omni-model-router

# Get a free API key from https://openrouter.ai/keys

# Validate your key
python omni_model_router.py --key sk-or-v1-YOUR_KEY check

# List all free models
python omni_model_router.py --key sk-or-v1-YOUR_KEY list

# Benchmark all free models (parallel)
python omni_model_router.py --key sk-or-v1-YOUR_KEY bench

# Auto-select the fastest working model
python omni_model_router.py --key sk-or-v1-YOUR_KEY auto

# Test a specific model
python omni_model_router.py --key sk-or-v1-YOUR_KEY test google/gemini-2.5-flash:free
```

## Example Output

```
$ python omni_model_router.py --key sk-or-v1-xxx bench

Benchmarking 8 models...

Model                                                   Status       Latency    Response
----------------------------------------------------------------------------------------------------
google/gemini-2.5-flash:free                             ✅ ok         812ms      ok
meta-llama/llama-3.3-70b-instruct:free                   ✅ ok         1340ms     ok
qwen/qwen3-coder:free                                    ❌ error-429  230ms      Too Many Requests
deepseek/deepseek-r1-0528:free                           ✅ ok         2100ms     ok

3/8 models responding
Fastest: google/gemini-2.5-flash:free (812ms)
```

## Use with Claude Code

After auto-selecting a model, add it to your `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_AUTH_TOKEN": "sk-or-v1-YOUR_KEY",
    "ANTHROPIC_API_KEY": "",
    "ANTHROPIC_MODEL": "google/gemini-2.5-flash:free"
  },
  "model": "sonnet[1m]"
}
```

## Built-in Free Models Tested

| Model | Provider | Context Window |
|-------|----------|---------------|
| `google/gemini-2.5-flash:free` | Google | 1M tokens |
| `meta-llama/llama-3.3-70b-instruct:free` | Meta | 128K tokens |
| `qwen/qwen3-coder:free` | Alibaba | 128K tokens |
| `deepseek/deepseek-r1-0528:free` | DeepSeek | 128K tokens |
| `nvidia/llama-3.1-nemotron-ultra-253b:free` | NVIDIA | 128K tokens |
| `microsoft/mai-ds-r1:free` | Microsoft | 128K tokens |
| `google/gemma-3-27b-it:free` | Google | 96K tokens |
| `mistralai/mistral-small-3.2-24b:free` | Mistral | 128K tokens |

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## License

MIT License — see [LICENSE](LICENSE) for details.
