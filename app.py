import streamlit as st
import time
import json
from review import review_code

st.set_page_config(
    page_title="code_review.bot",
    page_icon="🖤",
    layout="wide",
)

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    :root {
        --bg: #0d1117;
        --surface: #161b22;
        --surface-2: #1c2128;
        --border: #30363d;
        --border-bright: #484f58;
        --text: #e6edf3;
        --text-muted: #7d8590;
        --accent: #58a6ff;
        --success: #3fb950;
        --danger: #f85149;
        --warning: #d29922;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }
    code, pre, .stCodeBlock code, textarea, input {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ---------- Background: GitHub dark + abstract contribution graph + glows ---------- */
    .stApp {
        background-color: var(--bg) !important;
        background-image:
            url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='88' viewBox='0 0 120 88'><g fill='%2339d353' fill-opacity='0.05'><rect x='0' y='0' width='9' height='9' rx='2'/><rect x='13' y='0' width='9' height='9' rx='2'/><rect x='39' y='0' width='9' height='9' rx='2'/><rect x='65' y='0' width='9' height='9' rx='2'/><rect x='91' y='0' width='9' height='9' rx='2'/><rect x='26' y='13' width='9' height='9' rx='2'/><rect x='52' y='13' width='9' height='9' rx='2'/><rect x='104' y='13' width='9' height='9' rx='2'/><rect x='0' y='26' width='9' height='9' rx='2'/><rect x='13' y='26' width='9' height='9' rx='2'/><rect x='78' y='26' width='9' height='9' rx='2'/><rect x='91' y='26' width='9' height='9' rx='2'/><rect x='39' y='39' width='9' height='9' rx='2'/><rect x='52' y='39' width='9' height='9' rx='2'/><rect x='65' y='39' width='9' height='9' rx='2'/><rect x='104' y='39' width='9' height='9' rx='2'/><rect x='13' y='52' width='9' height='9' rx='2'/><rect x='26' y='52' width='9' height='9' rx='2'/><rect x='78' y='52' width='9' height='9' rx='2'/><rect x='0' y='65' width='9' height='9' rx='2'/><rect x='52' y='65' width='9' height='9' rx='2'/><rect x='91' y='65' width='9' height='9' rx='2'/><rect x='104' y='65' width='9' height='9' rx='2'/></g></svg>"),
            radial-gradient(circle at 75% 25%, rgba(57,211,83,0.06) 0%, transparent 45%),
            radial-gradient(circle at 15% 85%, rgba(88,166,255,0.05) 0%, transparent 50%);
        background-size: 120px 88px, 100% 100%, 100% 100%;
        background-attachment: fixed, fixed, fixed;
        color: var(--text);
    }

    .stApp > header { background: transparent !important; }

    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 960px !important;
        position: relative;
        z-index: 1;
    }

    h1, h2, h3, h4 {
        color: var(--text) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ---------- Inputs ---------- */
    .stTextInput label, .stTextArea label {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.16em !important;
        font-weight: 500 !important;
        font-family: 'JetBrains Mono', monospace !important;
        margin-bottom: 0.4rem !important;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.95rem !important;
        padding: 0.85rem 1rem !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #4d5560 !important;
    }
    .stTextInput input:hover, .stTextArea textarea:hover {
        border-color: var(--border-bright) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important;
        outline: none !important;
    }

    /* ---------- Button ---------- */
    .stButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: 1px solid rgba(240,246,252,0.1) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        padding: 0.9rem 1.5rem !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #2ea043 !important;
        box-shadow: 0 0 0 3px rgba(46,160,67,0.25) !important;
    }
    .stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(46,160,67,0.35) !important;
        outline: none !important;
    }

    /* ---------- Code blocks ---------- */
    .stCodeBlock, pre, [data-testid="stCodeBlock"] {
        background-color: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    code, [data-testid="stCodeBlock"] code {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.86em !important;
    }
    p code, li code {
        background-color: var(--surface-2) !important;
        color: #e6edf3 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid var(--border) !important;
        font-size: 0.85em !important;
    }

    /* ---------- Expander ---------- */
    [data-testid="stExpander"], details {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        margin-bottom: 0.7rem !important;
    }
    [data-testid="stExpander"] summary, details summary {
        background-color: transparent !important;
        color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.86rem !important;
        padding: 0.9rem 1.1rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stExpander"] summary:hover, details summary:hover {
        background-color: var(--surface-2) !important;
    }

    [data-testid="stAlert"] {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
    }

    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 2rem 0 !important;
    }
    a { color: var(--accent) !important; text-decoration: none !important; }
    a:hover { text-decoration: underline !important; }

    #MainMenu, footer { visibility: hidden; height: 0; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stStatusWidget"] { display: none; }

    /* ---------- HERO: brand row ---------- */
    .brand-row {
        display: flex;
        align-items: center;
        gap: 1.35rem;
        margin-bottom: 3rem;
        padding-bottom: 2rem;
        border-bottom: 1px solid var(--border);
    }
    .brand-row svg {
        flex-shrink: 0;
        opacity: 0.9;
        transition: opacity 0.15s ease, transform 0.15s ease;
    }
    .brand-row svg:hover {
        opacity: 1;
        transform: scale(1.05);
    }
    .brand-wordmark {
        font-family: 'JetBrains Mono', monospace;
        font-size: 3rem;
        font-weight: 600;
        letter-spacing: -0.04em;
        line-height: 1;
        color: #e6edf3;
    }
    .brand-wordmark .dim { color: #7d8590; font-weight: 500; }

    /* ---------- Verdict banner ---------- */
    .verdict {
        position: relative;
        padding: 1.6rem 1.75rem 1.6rem 1.9rem;
        border-radius: 10px;
        background: var(--surface);
        border: 1px solid var(--border);
        margin: 0.75rem 0 1.1rem 0;
        overflow: hidden;
        animation: fadeUp 0.35s ease;
    }
    .verdict::before {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
    }
    .verdict.ready::before   { background: var(--success); box-shadow: 0 0 20px var(--success); }
    .verdict.blocked::before { background: var(--danger);  box-shadow: 0 0 20px var(--danger); }
    .verdict.ready   { background: linear-gradient(90deg, rgba(63,185,80,0.06) 0%, var(--surface) 55%); }
    .verdict.blocked { background: linear-gradient(90deg, rgba(248,81,73,0.06) 0%, var(--surface) 55%); }

    .verdict-status {
        display: inline-flex; align-items: center; gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; letter-spacing: 0.18em;
        text-transform: uppercase; margin-bottom: 0.65rem; font-weight: 600;
    }
    .verdict.ready .verdict-status   { color: var(--success); }
    .verdict.blocked .verdict-status { color: var(--danger); }

    .verdict-headline {
        font-size: 1.25rem; font-weight: 600; color: var(--text);
        letter-spacing: -0.02em; margin-bottom: 0.5rem; line-height: 1.35;
    }
    .verdict-oneliner { font-size: 0.95rem; color: #a3a3a3; line-height: 1.6; }

    /* ---------- Meta strip ---------- */
    .meta-strip {
        display: flex; gap: 2.25rem; flex-wrap: wrap;
        padding: 1rem 0; margin-bottom: 1.5rem;
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    }
    .meta-item { color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.12em; }
    .meta-item strong { color: var(--text); font-weight: 500; margin-left: 0.45rem;
                        text-transform: none; letter-spacing: 0; }

    /* ---------- Findings ---------- */
    .finding {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.5rem 1.65rem;
        margin-bottom: 0.9rem;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.35s ease;
    }
    .finding:hover {
        border-color: var(--border-bright);
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0,0,0,0.5), 0 0 0 1px var(--border-bright);
    }
    .finding::before {
        content: "";
        position: absolute; left: 0; top: 0; bottom: 0; width: 2px;
    }
    .finding.high::before   { background: var(--danger);  box-shadow: 0 0 14px var(--danger); }
    .finding.medium::before { background: var(--warning); box-shadow: 0 0 14px var(--warning); }
    .finding.low::before    { background: var(--text-muted); }

    .finding-top { display: flex; align-items: center; gap: 0.75rem;
                   margin-bottom: 0.9rem; flex-wrap: wrap; }

    .chip {
        display: inline-flex; align-items: center; gap: 0.35rem;
        padding: 3px 11px; border-radius: 999px;
        font-size: 0.68rem; font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.1em; text-transform: uppercase;
        border: 1px solid;
    }
    .chip.high   { background: rgba(248,81,73,0.10); color: #ff7b72; border-color: rgba(248,81,73,0.4); }
    .chip.medium { background: rgba(210,153,34,0.10); color: #d29922; border-color: rgba(210,153,34,0.4); }
    .chip.low    { background: rgba(230,237,243,0.05); color: #7d8590; border-color: rgba(125,133,144,0.3); }
    .chip.clean  { background: rgba(63,185,80,0.10); color: #56d364; border-color: rgba(63,185,80,0.4); }

    .finding-cat {
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        color: var(--text-muted); padding: 3px 9px;
        background: #0d1117; border-radius: 4px;
        border: 1px solid var(--border); letter-spacing: 0.02em;
    }
    .finding-line {
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        color: var(--text-muted); margin-left: auto;
    }
    .finding-title {
        font-size: 1.05rem; font-weight: 600; color: var(--text);
        margin: 0.35rem 0 1rem 0; letter-spacing: -0.01em; line-height: 1.4;
    }
    .field { margin-bottom: 0.8rem; font-size: 0.9rem; line-height: 1.65; color: #c9d1d9; }
    .field-label {
        display: block; font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.16em;
        margin-bottom: 0.25rem; font-weight: 500;
    }
    .refs {
        margin-top: 0.95rem; padding-top: 0.85rem;
        border-top: 1px solid var(--border);
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    }
    .refs a { color: #7d8590; margin-right: 1rem; text-decoration: none;
              border-bottom: 1px dotted #30363d; }
    .refs a:hover { color: var(--text); border-bottom-color: var(--text); }

    /* ---------- Stages ---------- */
    .stages {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 10px; padding: 1.1rem 1.4rem; margin: 0.75rem 0;
    }
    .stage {
        display: flex; align-items: center; gap: 0.75rem;
        padding: 0.35rem 0; font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem; color: #4d5560; transition: color 0.25s ease;
    }
    .stage.active { color: var(--text); }
    .stage.done   { color: #a3a3a3; }
    .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #2a2a2a; flex-shrink: 0; transition: all 0.25s ease;
    }
    .stage.active .dot { background: var(--accent); animation: pulse 1.2s ease-out infinite; }
    .stage.done .dot   { background: var(--success); box-shadow: 0 0 8px rgba(63,185,80,0.5); }

    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(88,166,255,0.55); }
        70%  { box-shadow: 0 0 0 10px rgba(88,166,255,0); }
        100% { box-shadow: 0 0 0 0 rgba(88,166,255,0); }
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .top-progress {
        position: fixed; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #39d353, transparent);
        background-size: 40% 100%; background-repeat: no-repeat;
        animation: slideBar 1.6s linear infinite;
        z-index: 9999;
    }
    @keyframes slideBar {
        0%   { background-position: -50% 0; }
        100% { background-position: 150% 0; }
    }
</style>
""", unsafe_allow_html=True)


OCTOCAT_SVG = '''
<svg width="44" height="44" viewBox="0 0 16 16" fill="#e6edf3" xmlns="http://www.w3.org/2000/svg" aria-label="GitHub">
  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
</svg>
'''


def esc(t):
    if t is None: return ""
    return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def severity_chip(sev):
    s = (sev or "").lower()
    return f'<span class="chip {esc(s)}">{esc(s or "unknown")}</span>'

def render_stages(stages, current_index, done=False):
    html = '<div class="stages">'
    for i, s in enumerate(stages):
        if done or i < current_index:
            cls = "stage done"
        elif i == current_index:
            cls = "stage active"
        else:
            cls = "stage"
        html += f'<div class="{cls}"><span class="dot"></span>{esc(s)}</div>'
    html += '</div>'
    return html

def render_finding(f):
    sev = (f.severity or "").lower()
    line_txt = f"line {f.line}" if f.line else "whole file"
    refs_html = ""
    if f.references:
        links = "".join(f'<a href="{esc(r)}" target="_blank">↗ {esc(r)}</a>' for r in f.references)
        refs_html = f'<div class="refs">{links}</div>'
    return f'''
    <div class="finding {esc(sev)}">
        <div class="finding-top">
            {severity_chip(f.severity)}
            <span class="finding-cat">{esc(f.category)}</span>
            <span class="finding-line">{esc(line_txt)}</span>
        </div>
        <div class="finding-title">{esc(f.title)}</div>
        <div class="field"><span class="field-label">what</span>{esc(f.what)}</div>
        <div class="field"><span class="field-label">why it matters</span>{esc(f.why_it_matters)}</div>
        <div class="field"><span class="field-label">suggestion</span>{esc(f.suggestion)}</div>
        {refs_html}
    </div>
    '''


# HERO — no tagline
st.markdown(
    f'''
    <div class="brand-row">
        <a href="https://github.com/AditiSNayak/code-review-bot" target="_blank">{OCTOCAT_SVG}</a>
        <div class="brand-wordmark">code_review<span class="dim">.bot</span></div>
    </div>
    ''',
    unsafe_allow_html=True,
)


col1, col2 = st.columns(2)
with col1:
    language = st.text_input("LANGUAGE", value="python",
        placeholder="python, rust, go, javascript...")
with col2:
    focus = st.text_input("REVIEW FOCUS", value="check bugs, security, and style",
        placeholder="e.g. thread safety, SQL injection, PEP8")

code = st.text_area("CODE", height=320, placeholder="// paste your code here")

review_clicked = st.button("RUN REVIEW")


if review_clicked:
    if not code.strip():
        st.warning("Please paste some code before running the review.")
    else:
        stages = ["analyzing code structure", "identifying issues",
                  "ranking by severity", "writing suggestions"]

        top_bar = st.empty()
        top_bar.markdown('<div class="top-progress"></div>', unsafe_allow_html=True)

        progress_placeholder = st.empty()
        progress_placeholder.markdown(render_stages(stages, 0), unsafe_allow_html=True)
        time.sleep(0.3)

        try:
            result = review_code(code, language, focus)
        except Exception as e:
            top_bar.empty()
            progress_placeholder.empty()
            st.error(f"Review failed: {type(e).__name__}: {e}")
            st.stop()

        for i in range(1, len(stages)):
            progress_placeholder.markdown(render_stages(stages, i), unsafe_allow_html=True)
            time.sleep(0.15)

        progress_placeholder.markdown(render_stages(stages, len(stages), done=True), unsafe_allow_html=True)
        time.sleep(0.4)
        progress_placeholder.empty()
        top_bar.empty()

        v = result.verdict
        m = result.meta
        state_class = "ready" if v.ship_ready else "blocked"
        status_text = "ship ready" if v.ship_ready else "not ready"

        st.markdown(
            f'''
            <div class="verdict {state_class}">
                <div class="verdict-status"><span>{status_text}</span></div>
                <div class="verdict-headline">{esc(v.headline)}</div>
                <div class="verdict-oneliner">{esc(v.one_liner)}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'''
            <div class="meta-strip">
                <span class="meta-item">model<strong>{esc(m.language_detected)}</strong></span>
                <span class="meta-item">confidence<strong>{esc(m.review_confidence)}</strong></span>
                <span class="meta-item">lines<strong>{esc(m.lines_reviewed)}</strong></span>
                <span class="meta-item">severity<strong>{esc(v.severity)}</strong></span>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        if result.findings:
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace;font-size:0.72rem;'
                f'color:#7d8590;text-transform:uppercase;letter-spacing:0.16em;margin-bottom:1rem">'
                f'findings · {len(result.findings)}</div>',
                unsafe_allow_html=True,
            )
            for f in result.findings:
                st.markdown(render_finding(f), unsafe_allow_html=True)
                if f.code_before or f.code_after:
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        st.markdown(
                            '<div style="font-family:JetBrains Mono,monospace;font-size:0.62rem;'
                            'color:#7d8590;text-transform:uppercase;letter-spacing:0.16em;'
                            'margin-bottom:0.35rem">before</div>',
                            unsafe_allow_html=True,
                        )
                        st.code(f.code_before or "# (none)", language=language or "python")
                    with bc2:
                        st.markdown(
                            '<div style="font-family:JetBrains Mono,monospace;font-size:0.62rem;'
                            'color:#7d8590;text-transform:uppercase;letter-spacing:0.16em;'
                            'margin-bottom:0.35rem">after</div>',
                            unsafe_allow_html=True,
                        )
                        st.code(f.code_after or "# (none)", language=language or "python")
                    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        else:
            st.success("No issues found. Clean bill of health.")

        st.markdown("---")

        if result.strengths:
            with st.expander(f"strengths · {len(result.strengths)}", expanded=True):
                for s in result.strengths:
                    st.markdown(f"- {s}")

        if result.improved_code:
            ic = result.improved_code
            with st.expander("improved code", expanded=True):
                st.caption(ic.notes)
                st.code(ic.content, language=ic.language or "python")

        if result.followup_questions:
            with st.expander(f"followup questions · {len(result.followup_questions)}"):
                for q in result.followup_questions:
                    st.markdown(f"- {q}")

        with st.expander("raw json · for debugging"):
            st.json(result.model_dump())
