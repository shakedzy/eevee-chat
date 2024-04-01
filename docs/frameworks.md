---
title: Supported Frameworks
---

# Frameworks & Models

## Supported Frameworks
The following frameworks are currently supported:

* OpenAI: `OPENAI_API_KEY`
* Anthropic: `ANTHROPIC_API_KEY`
* Mistral: `MISTRAL_API_KEY`
* DeepSeek: `DEEPSEEK_API_KEY`
* Google: `GOOGLE_API_KEY`

To enable them, simply add their API keys under the names above as environment variables. Eevee Chat will detect these on launch.

### Supported Models
Technically, all chat models of the supported frameworks are also supported. Still,a s there are many models, only the most common ones were added
to Eevee. If the model you're looking for is not on the list, simply open the `config.toml` file found under Eevee's installation folder, and add it
to the relevant list under `[models]`.

You can locate the `config.toml` file by running:
```bash
eevee --config-path
```