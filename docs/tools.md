---
title: Tools and Power-ups
---

# Tools & Power-ups
Eevee Chat comes built-in with several tools and power-ups, which provide a native-like experience, as well as some additional power-ups available usually only to developers.

## Tools
Some models were trained to use external tools, such as web search. Models which support tool calling are automatically attached to the following tools:

* **Web connection:** 
    * **Web Search:** Using Google Search (if [enabled](google_search.md)), or DuckDuckGo as default
    * **Web Surf:** Visiting websites, extracting text only

## Power-ups
Power-ups are usually available only to developers as part of the API functionality. Eevee Chat exposes these to everyone.

* **JSON Forcing:** Activating this option forces the model to output a valid JSON. Note that when enabled, streaming is off.
* **Adjustable System Prompt:** Eevee Chat allows you to modify and control the system prompt of the chat. The system prompt can be overwritten and modified during conversation too.


## Known Limitations
Not all models were trained the same. The table below summarizes some known limitations of the supported frameworks:

Framework | Tool Calling | JSON Forcing
-|-|-
OpenAI | ✅ | ✅
Anthropic| ❌ | ❌
Mistral | ✅ | ✅ (Tool calling is not supported when forcing JSON)


