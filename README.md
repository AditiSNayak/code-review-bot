# code_review.bot

An AI-powered code review tool. Paste code or a GitHub pull request URL, and receive a structured, severity-ranked review in seconds.

**Live demo:** https://code-review-bot-aditisnayak.streamlit.app

---

## What It Does

- Reviews pasted code in any language, with any focus the user specifies
- Fetches and reviews public GitHub pull requests by URL (with diff preview)
- Returns a structured review: verdict, severity-ranked findings, before/after code, strengths, and follow-up questions
- Streams a live narrative while the review is being computed
- Falls back across multiple models if the primary is unavailable

---

## Why It Is More Than "Calling the LLM"

| Decision | Reasoning |
|----------|-----------|
| Structured output enforced via Pydantic schema | Eliminates JSON parsing failures and missing fields. The API guarantees the shape. |
| Fixed schema, dynamic content | Any review focus (security, thread safety, GDPR, style) works without hardcoded presets or per-focus templates. |
| Free-text language and focus inputs | No dropdown of presets. Supports 100+ languages and arbitrary review instructions. |
| Two-call streaming pattern | First call streams a short narrative for perceived latency. Second call returns structured JSON for rendering. |
| Model fallback chain | Five models tried in order. Per-model retry. Survives individual model outages. |
| Streaming prelude with graceful degradation | If the prelude fails mid-stream, the review still completes normally. |
| Cloud secrets only | API key is stored in Streamlit Cloud secrets, never in the repository. |

---

## Architecture

```
Browser (Streamlit Cloud)
    |
    v
app.py  ->  UI, wizard state, streaming render, findings display
    |
    v
review.py  ->  Prompt construction, Pydantic schema, model fallback,
               streaming prelude, GitHub PR diff fetcher
    |
    v
Gemini API  ->  Streaming narrative + structured JSON review
```

Two LLM calls per review:

1. Prelude (streaming) - 2-3 sentence plain-text preview, token-by-token
2. Structured review - Pydantic-validated JSON with findings

The prelude keeps the user engaged during the 4-10 second structured call. If it fails, the structured call continues unaffected.

---

## Features

### Input Modes
- Paste code: any language, any snippet
- GitHub PR URL: fetches the unified diff of a public PR, includes context lines, previews before running the review

### Review Output
- Verdict banner: ship-ready or not, with a one-line summary
- Findings: severity-ranked cards with what, why it matters, suggestion, and before/after code blocks
- Meta strip: model used, confidence level, lines reviewed, overall severity
- Strengths: what the code does well
- Improved code: full refactored snippet with syntax highlighting
- Follow-up questions: what a senior reviewer would ask before approving
- Raw JSON: full structured output for power users

### Reliability
- 5-model fallback chain across Gemini models
- Per-model retry on transient errors
- Graceful error surfaces (no raw tracebacks in the UI)
- Streaming prelude failure does not block the review

---

## Tech Stack

- Google Gemini API via the google-genai SDK
- Pydantic for enforced structured output
- Streamlit for the UI
- Streamlit Community Cloud for hosting
- GitHub Codespaces for cloud-native development (zero local installs)

---

## Running Locally

Requirements: Python 3.11+, a Gemini API key from https://aistudio.google.com/app/apikey

```bash
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key_here" > .env
streamlit run app.py
```

The app reads GEMINI_API_KEY from .env locally, or from Streamlit secrets when deployed.

---

## Deployment

The app is deployed on Streamlit Community Cloud:

1. Push to the main branch of the GitHub repository
2. Streamlit Cloud detects the push and rebuilds automatically
3. API key is configured in the Streamlit Cloud dashboard under Advanced Settings

No manual redeploy step is required.

---

## What I Learned Building This

- Enforcing LLM output shape with Pydantic is more reliable than instructing the model to "return valid JSON." The schema guarantee eliminates a whole class of bugs.
- Fixed schema plus dynamic content is the right abstraction. The shape stays stable while the review focus changes.
- Production LLM apps need fallback chains. Free-tier APIs go down under load, and a single hardcoded model name is a single point of failure.
- Streaming is a UX pattern, not a technical flex. Users tolerate long waits when they can see progress. Two-call streaming works well for schema-constrained outputs.
- Cloud-native development eliminates friction. Codespaces plus Streamlit Cloud meant zero local setup throughout the build.
- Simple beats clever in UI decisions. A wizard felt heavier than a sectioned single-page flow for this use case.

---

## Roadmap

- [ ] Review entire files instead of just diffs
- [ ] Private repository support via GitHub token
- [ ] Export review as Markdown
- [ ] Save review history per session
- [ ] Severity filtering in the results view

---

## License

MIT