import streamlit as st
import json
from review import review_code

st.set_page_config(
    page_title="AI Code Review Bot",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AI Code Review Bot")
st.caption("Paste code. Get a structured senior-level review in seconds.")

# ---------- Input section ----------
col1, col2 = st.columns(2)

with col1:
    language = st.text_input(
        "Language",
        value="python",
        placeholder="e.g. python, javascript, rust, go",
        help="Type any language name. The LLM understands 100+ languages.",
    )

with col2:
    focus = st.text_input(
        "Review focus",
        value="check bugs, security, and style",
        placeholder="e.g. check thread safety, SQL injection, PEP8",
        help="Describe what you want the reviewer to focus on. Free text.",
    )

code = st.text_area(
    "Paste your code",
    height=300,
    placeholder="Paste the code you want reviewed here...",
)

review_clicked = st.button("🔎 Review Code", type="primary")


# ---------- Helper: severity badge ----------
def severity_badge(sev):
    sev = (sev or "").lower()
    if sev == "high":
        return "🔴 HIGH"
    if sev == "medium":
        return "🟠 MEDIUM"
    if sev == "low":
        return "🟡 LOW"
    if sev == "clean":
        return "🟢 CLEAN"
    return f"⚪ {sev.upper()}"


# ---------- Render a single finding ----------
def render_finding(f):
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 6])
        with c1:
            st.markdown(f"**{severity_badge(f.severity)}**")
        with c2:
            st.markdown(f"`{f.category}`")
        with c3:
            line_txt = f"Line {f.line}" if f.line else "Whole file"
            st.markdown(f"*{line_txt}*")

        st.markdown(f"### {f.title}")
        st.markdown(f"**What:** {f.what}")
        st.markdown(f"**Why it matters:** {f.why_it_matters}")
        st.markdown(f"**Suggestion:** {f.suggestion}")

        if f.code_before or f.code_after:
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("**Before**")
                st.code(f.code_before or "", language="python")
            with cc2:
                st.markdown("**After**")
                st.code(f.code_after or "", language="python")

        if f.references:
            st.markdown("**References:** " + " · ".join(f"[link]({r})" for r in f.references))


# ---------- Main handler ----------
if review_clicked:
    if not code.strip():
        st.warning("Please paste some code before clicking Review.")
    else:
        with st.spinner("Reviewing with Gemini..."):
            try:
                result = review_code(code, language, focus)
            except Exception as e:
                st.error(f"Review failed: {type(e).__name__}: {e}")
                st.stop()

        v = result.verdict
        m = result.meta

        # ---- Verdict banner ----
        if v.ship_ready:
            st.success(f"✅ **{v.headline}**\n\n{v.one_liner}")
        else:
            st.error(f"🚫 **{v.headline}**\n\n{v.one_liner}")

        # ---- Meta line ----
        st.caption(
            f"Model: `{m.language_detected}` · "
            f"Confidence: `{m.review_confidence}` · "
            f"Lines reviewed: `{m.lines_reviewed}` · "
            f"Severity: `{v.severity}`"
        )

        st.divider()

        # ---- Findings ----
        if result.findings:
            st.subheader(f"🔍 Findings ({len(result.findings)})")
            for f in result.findings:
                render_finding(f)
        else:
            st.info("No issues found. 🎉")

        st.divider()

        # ---- Strengths ----
        if result.strengths:
            with st.expander(f"✅ Strengths ({len(result.strengths)})", expanded=True):
                for s in result.strengths:
                    st.markdown(f"- {s}")

        # ---- Improved code ----
        if result.improved_code:
            ic = result.improved_code
            with st.expander("💡 Improved Code", expanded=True):
                st.caption(ic.notes)
                st.code(ic.content, language=ic.language)

        # ---- Followup questions ----
        if result.followup_questions:
            with st.expander(f"❓ Followup Questions ({len(result.followup_questions)})"):
                for q in result.followup_questions:
                    st.markdown(f"- {q}")

        # ---- Raw JSON (power users) ----
        with st.expander("📄 Raw JSON (for debugging)"):
            st.json(result.model_dump())
