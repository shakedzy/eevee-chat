---
title: Enable Google Search
---

# Enable Google Search
Models which support tool calling are automatically connected to the web. By default, web search is based on DuckDuckGo, as it enables hassle-free web search.

Still, if you'd like to upgrade your web search and use Google Search, you can easily do so by following the following steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/), and create a new project or select an existing one
2. Navigate to the "APIs & Services" dashboard and click on "ENABLE APIS AND SERVICES". Search for the Custom Search JSON API and enable it for your project
3. In the API & Services dashboard, go to Credentials. Click on "Create Credentials" and select "API key". This key is used to authenticate your requests.
4. Save the API key as an environment variable named `GOOGLE_SEARCH_API_KEY`
5. Go to the [Google Custom Search](https://cse.google.com/cse/) Engine page and create a new search engine. Set your search engine to search across all the web
6. Copy the unique identifier for your search engine, referred to as the "cx" parameter.
7. Save the identifier as as an environment variable named `GOOGLE_SEARCH_CSE_ID`

Eevee Chat looks for these two environment variables on launch, and if found, Google Search is used.
