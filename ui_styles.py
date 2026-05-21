"""CSS condiviso."""

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=Inter:wght@300;400;500;600&display=swap');

#MainMenu, footer, header {visibility: hidden;}
[data-testid="stSidebarNav"] {display: none;}
.block-container { padding-top: 2rem; padding-bottom: 2.5rem; }

.eb-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 2.4rem; font-weight: 600; letter-spacing: -0.02em;
    color: #1a2332; margin-bottom: 0.25rem; line-height: 1.2;
}
.eb-subtitle {
    font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #5c6b7a;
    margin-bottom: 1.5rem; line-height: 1.5;
}
.eb-meta {
    font-family: 'Inter', sans-serif; font-size: 0.75rem; color: #8b9aab;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;
}
.eb-question {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.25rem; font-weight: 600; color: #1a2332;
    line-height: 1.45; margin: 1rem 0 0.75rem 0;
}
.eb-divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.25rem 0; }
.eb-result-card {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;
}
.eb-profile-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.5rem; font-weight: 600; color: #1e3a5f;
}
.eb-motto {
    font-family: 'Source Serif 4', Georgia, serif; font-style: italic;
    font-size: 1rem; color: #475569; margin: 0.5rem 0 1rem 0;
    padding-left: 1rem; border-left: 3px solid #3b82f6;
}
.eb-banner {
    background: #1e3a5f; color: #fff; border-radius: 10px;
    padding: 1rem 1.25rem; font-family: 'Inter', sans-serif;
    font-size: 0.95rem; margin: 1rem 0; text-align: center;
}
.stProgress > div > div { background-color: #3b82f6; }
div[data-testid="stRadio"] > label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important; padding: 0.75rem 0 !important;
}
</style>
"""

PRESENTER_CSS = """
<style>
.presenter-wrap { max-width: 1100px; margin: 0 auto; }
.presenter-h1 {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 3rem; font-weight: 600; color: #0f172a; text-align: center;
}
.presenter-h2 {
    font-family: 'Inter', sans-serif; font-size: 1.25rem; color: #475569;
    text-align: center; margin-bottom: 2rem;
}
.presenter-stat {
    font-family: 'Inter', sans-serif; font-size: 4rem; font-weight: 600;
    color: #1e3a5f; text-align: center; line-height: 1;
}
.presenter-stat-label {
    font-family: 'Inter', sans-serif; font-size: 1rem; color: #64748b;
    text-align: center; text-transform: uppercase; letter-spacing: 0.1em;
}
.presenter-instructions {
    font-family: 'Inter', sans-serif; font-size: 1.35rem; color: #1e293b;
    text-align: center; line-height: 1.6; padding: 1rem 2rem;
    background: #f1f5f9; border-radius: 12px; margin: 1rem 0 2rem 0;
}
</style>
"""
