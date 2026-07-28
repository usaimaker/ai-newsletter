import os, glob, re, html, json

ISSUES = "issues"

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
        out.append({"slug": slug, "title": title, "body": body})
    return out

def build():
    issues = load_issues()
    items = ""
    for it in issues:
        items += f'<li><a href="issues/{it["slug"]}.html">{html.escape(it["title"])}</a></li>\n'
    index = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>AI Automation Daily — free tools & tactics</title>
<meta name="description" content="A daily newsletter of free AI automation tools and tactics for solo founders.">
</head><body style="font-family:system-ui,Arial;max-width:760px;margin:40px auto;padding:0 20px;line-height:1.7">
<h1>AI Automation Daily</h1>
<p>Free AI automation tools & tactics, curated daily. <a href="feed.xml">RSS</a></p>
<h2>Archive</h2><ul>{items}</ul>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
    xml += "<title>AI Automation Daily</title><link>https://example.com</link>"
    xml += "<description>Free AI automation tools & tactics</description>"
    for it in issues:
        xml += f'<item><title>{html.escape(it["title"])}</title>'
        xml += f'<link>https://example.com/issues/{it["slug"]}.html</link>'
        xml += f'<guid>issues/{it["slug"]}.html</guid></item>'
    xml += "</channel></rss>"
    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("built", len(issues), "issues")

if __name__ == "__main__":
    build()