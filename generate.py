import os, glob, re, html

ISSUES = "issues"
SITE = "https://ai-newsletter.vercel.app"
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
  <p style="margin:0;font-size:14px"><a href="https://ai-gumroad-products.vercel.app" target="_blank" rel="noopener" style="color:#fbbf24">&#128722; Free AI Kits</a> &nbsp;&middot;&nbsp; <a href="https://ko-fi.com/aidaily" target="_blank" rel="noopener" style="color:#fff">&#9749; Support on Ko-fi</a> &nbsp;&middot;&nbsp; <a href="https://buymeacoffee.com/felovery" target="_blank" rel="noopener" style="color:#ffd700">&#9749; Buy Me a Coffee</a></p>
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
