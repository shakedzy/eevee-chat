---
title: Supported Frameworks
---

# Frameworks & Models

## Supported Frameworks
The following frameworks are currently supported:

* OpenAI: `OPENAI_API_KEY`
* Anthropic: `ANTHROPIC_API_KEY`
* Mistral: `MISTRAL_API_KEY`

To enable them, simply add their API keys under the names above as environment variables. Eevee Chat will detect these on launch.

### Supported Models
Technically, all chat models of the supported frameworks are also supported. Still,a s there are many models, only the most common ones were added
to Eevee. If the model you're looking for is not on the list, simply open the `config.toml` file found under Eevee's installation folder, and add it
to the relevant list under `[models]`.


## Known Limitations
Not all models were trained the same. The table below summarizes some known limitations of the supported frameworks:

Framework | Tool Calling | JSON Forcing
-|-|-
OpenAI | ✅ | ✅
Anthropic| ❌ | ❌
Mistral | ✅ | ✅ (Tool calling is not supported when forcing JSON)

* **Tool Calling:** Model's ability to use external tools, such as web search. Models which support tool calling are automatically attached to the provided tools (see below)
* **JSON Forcing:** Activating this option forces the model to output a valid JSON. Note that when enabled, streaming is off.

## Available Tools:
* **Web connection:** 
    * **Web Search:** Using Google Search (if [enabled](google_search.md)), or DuckDuckGo as default
    * **Web Surf:** Visiting websites, extracting text only

