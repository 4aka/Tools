import sys
import os
import markdown
import tempfile
import webbrowser

if len(sys.argv) < 2:
    print("Usage: mdview.py <file.md>")
    sys.exit(1)

md_path = sys.argv[1]

with open(md_path, encoding="utf-8") as f:
    md_content = f.read()

html_body = markdown.markdown(md_content, extensions=["fenced_code", "tables", "toc"])

title = os.path.basename(md_path)

html = f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 16px;
    line-height: 1.7;
    padding: 48px 24px;
  }}
  .content {{
    max-width: 860px;
    margin: 0 auto;
  }}
  h1, h2, h3, h4, h5, h6 {{
    color: #ffffff;
    margin-top: 1.6em;
    margin-bottom: 0.4em;
    font-weight: 600;
  }}
  h1 {{ font-size: 2em; border-bottom: 1px solid #333; padding-bottom: 0.3em; }}
  h2 {{ font-size: 1.5em; border-bottom: 1px solid #2a2a2a; padding-bottom: 0.2em; }}
  h3 {{ font-size: 1.2em; }}
  p {{ margin-bottom: 1em; }}
  ul, ol {{ margin: 0.5em 0 1em 1.8em; }}
  li {{ margin-bottom: 0.3em; }}
  code {{
    background: #2d2d2d;
    color: #ce9178;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
    font-size: 0.9em;
  }}
  pre {{
    background: #2d2d2d;
    border-left: 3px solid #569cd6;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    margin-bottom: 1em;
  }}
  pre code {{
    background: none;
    padding: 0;
    color: #d4d4d4;
  }}
  blockquote {{
    border-left: 4px solid #569cd6;
    padding-left: 1em;
    color: #9e9e9e;
    margin: 1em 0;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1em;
  }}
  th, td {{
    border: 1px solid #3a3a3a;
    padding: 8px 12px;
    text-align: left;
  }}
  th {{ background: #2d2d2d; color: #fff; }}
  tr:nth-child(even) {{ background: #252525; }}
  a {{ color: #569cd6; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  hr {{ border: none; border-top: 1px solid #333; margin: 2em 0; }}
  strong {{ color: #ffffff; }}
</style>
</head>
<body>
<div class="content">
{html_body}
</div>
</body>
</html>"""

tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
tmp.write(html)
tmp.close()

webbrowser.open("file:///" + tmp.name.replace("\\", "/"))
