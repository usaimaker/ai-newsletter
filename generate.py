import os, glob, re, html

QRIFY_BLOCK = '<!-- QRIFY_TRAFFIC_START -->\n<section class="qrify-tool" style="margin:32px 0;padding:18px 20px;border:1px solid #d8dee9;border-radius:12px;background:#f8fafc;color:#0f172a;font-family:system-ui,Arial,sans-serif;line-height:1.6">\n  <div style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#64748b;margin-bottom:8px">Free tool for readers</div>\n  <p style="margin:0 0 10px"><strong>Make a QR code in seconds &mdash; no signup, no watermark.</strong> QRify is a free browser-based QR generator with custom colours, a logo overlay and SVG export. Everything runs locally in your browser, so your links and data never leave your device.</p>\n  <p style="margin:0;font-size:14px">\n    <a href="https://qrify.dynv6.net/" rel="noopener" style="color:#0369a1">Free QR code generator</a> &nbsp;&middot;&nbsp;\n    <a href="https://qrify.dynv6.net/wifi-qr-code" rel="noopener" style="color:#0369a1">WiFi QR code</a> &nbsp;&middot;&nbsp;\n    <a href="https://qrify.dynv6.net/vcard-qr-code" rel="noopener" style="color:#0369a1">vCard QR code</a> &nbsp;&middot;&nbsp;\n    <a href="https://qrify.dynv6.net/qr-code-with-logo" rel="noopener" style="color:#0369a1">QR code with logo</a> &nbsp;&middot;&nbsp;\n    <a href="https://qrify.dynv6.net/restaurant-menu-qr-code" rel="noopener" style="color:#0369a1">Restaurant menu QR</a> &nbsp;&middot;&nbsp;\n    <a href="https://usaimaker.github.io/free-qr-code-generator.html" rel="noopener" style="color:#0369a1">Full how-to guide</a>\n  </p>\n</section>\n<!-- QRIFY_TRAFFIC_END -->'

ISSUES = "issues"
SITE = "https://ai-newsletter-mu.vercel.app"
ADSENSE_CLIENT = "ca-pub-9959815194191047"

ADSENSE = (
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
    f'?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'
)

# Sponsor / self-promo slot + affiliate + support — injected into every page.
SPONSOR_BLOCK = f'''
<div class="nl-promo" style="margin:28px 0;padding:18px 20px;border:1px solid #2a2a40;border-radius:12px;background:#0f1020;color:#e5e7eb;font-family:system-ui,Arial">
  <div style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#a78bfa;margin-bottom:6px">Sponsor &middot; AI Automation Daily</div>
  <p style="margin:0 0 10px;line-height:1.6"><strong>Need this built for you?</strong> We design done-for-you AI automation &mdash; WhatsApp outreach, faceless video pipelines, content &amp; SEO engines, custom agents &mdash; that runs 24/7 at $0. <a href="mailto:felovery@gmail.com?subject=AI%20Automation%20project" style="color:#34d399">Email us &rarr;</a></p>
  <p style="margin:0;font-size:14px"><a href="https://ai-gumroad-products.vercel.app/" target="_blank" rel="noopener" style="color:#fbbf24">&#128722; Free AI Kits</a> &nbsp;&middot;&nbsp; <a href="https://ko-fi.com/aidaily" target="_blank" rel="noopener" style="color:#fff">&#9749; Support on Ko-fi</a> &nbsp;&middot;&nbsp; <a href="https://buymeacoffee.com/felovery" target="_blank" rel="noopener" style="color:#ffd700">&#9749; Buy Me a Coffee</a></p>
</div>
'''

AFFILIATE_NOTE = (
    '<p style="font-size:12px;color:#9aa0aa;margin-top:8px">'
    'Some links are affiliate links; they cost you nothing and help keep this newsletter free.</p>'
)


def load_issues():
    out = []
    for f in sorted(glob.glob(os.path.join(ISSUES, "*.html"))):
        slug = os.path.splitext(os.path.basename(f))[0]
        with open(f, encoding="utf-8") as fh:
            body = fh.read()
        title = "AI Automation Daily"
        tm = re.search(r"<title>(.*?)</title>", body, re.S)
        if tm:
            title = tm.group(1).strip()
        hm = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        if hm:
            title = re.sub(r"<[^>]+>", "", hm.group(1)).strip()
        out.append({"slug": slug, "title": title, "body": body, "path": f})
    return out


def inject_into_issue(path, body):
    """Add AdSense + sponsor/support footer to an issue page if missing."""
    changed = False
    # Collapse malformed multi-slash hosts first: replacing the bare host below
    # would otherwise recreate "https://host////" on every single rebuild.
    MULTISLASH = re.compile(r'(https?://[a-zA-Z0-9.-]+\.(?:vercel\.app|github\.io))/{2,}')
    collapsed = MULTISLASH.sub(r'\1/', body)
    if collapsed != body:
        body = collapsed
        changed = True
    # Unify cross-links to canonical Vercel URLs (Pages mirror kept as backup)
    for stale in ('https://usaimaker.github.io/ai-gumroad-products', 'https://ai-gumroad-products.vercel.app'):
        if stale in body:
            body = body.replace(stale, 'https://ai-gumroad-products.vercel.app/')
            changed = True
    # Normalize once more after rewriting so the result is idempotent
    collapsed = MULTISLASH.sub(r'\1/', body)
    if collapsed != body:
        body = collapsed
        changed = True
    if ADSENSE_CLIENT not in body:
        body = body.replace("</head>", ADSENSE + "\n</head>", 1)
        changed = True
    if 'class="nl-promo"' not in body:
        block = SPONSOR_BLOCK + AFFILIATE_NOTE
        if "</body>" in body:
            body = body.replace("</body>", block + "\n</body>", 1)
        else:
            body = body + block
        changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
    return body


def build():
    issues = load_issues()
    for it in issues:
        it["body"] = inject_into_issue(it["path"], it["body"])

    items = ""
    for it in issues:
        items += f'<li><a href="issues/{it["slug"]}.html">{html.escape(it["title"])}</a></li>\n'

    index = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>AI Automation Daily — free tools & tactics</title>
<meta name="description" content="A daily newsletter of free AI automation tools and tactics for solo founders.">
{ADSENSE}
</head><body style="font-family:system-ui,Arial;max-width:760px;margin:40px auto;padding:0 20px;line-height:1.7">
<h1>AI Automation Daily</h1>
<p>Free AI automation tools & tactics, curated daily. <a href="feed.xml">RSS</a></p>
{SPONSOR_BLOCK}
{AFFILIATE_NOTE}
<h2>Archive</h2><ul>{items}</ul>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index)

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
    xml += f"<title>AI Automation Daily</title><link>{SITE}</link>"
    xml += "<description>Free AI automation tools & tactics</description>"
    for it in issues:
        xml += f'<item><title>{html.escape(it["title"])}</title>'
        xml += f'<link>{SITE}/issues/{it["slug"]}.html</link>'
        xml += f'<guid>{SITE}/issues/{it["slug"]}.html</guid></item>'
    xml += "</channel></rss>"
    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("built", len(issues), "issues")


if __name__ == "__main__":
    build()

# QRIFY_TRAFFIC_INJECT_START (idempotent, survives the daily rebuild)
if __name__ == "__main__":
    try:
        with open("index.html", encoding="utf-8") as _qf:
            _qh = _qf.read()
        if "QRIFY_TRAFFIC_START" not in _qh:
            if "</body>" in _qh:
                _qh = _qh.replace("</body>", QRIFY_BLOCK + "\n</body>", 1)
            else:
                _qh = _qh + QRIFY_BLOCK
            with open("index.html", "w", encoding="utf-8") as _qf:
                _qf.write(_qh)
    except Exception as _qe:
        print("qrify inject skipped:", _qe)
# QRIFY_TRAFFIC_INJECT_END
