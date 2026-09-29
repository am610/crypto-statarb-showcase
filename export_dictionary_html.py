import re

md_path = "/Users/ayan/Programs/Quant/WSQ/To_Do/Crypto_StatArb_Project/QUANT_DICTIONARY.md"
html_path = "/Users/ayan/Programs/Quant/WSQ/To_Do/Crypto_StatArb_Project/QUANT_DICTIONARY.html"

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Convert basic markdown elements to HTML
html_content = ""
lines = text.split("\n")

in_code = False
in_table = False

html_lines = []
for line in lines:
    if line.startswith("```"):
        if in_code:
            html_lines.append("</code></pre>")
            in_code = False
        else:
            html_lines.append("<pre><code>")
            in_code = True
        continue
    
    if in_code:
        html_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        continue

    # Headings
    if line.startswith("# "):
        html_lines.append(f"<h1>{line[2:]}</h1>")
    elif line.startswith("## "):
        html_lines.append(f"<h2>{line[3:]}</h2>")
    elif line.startswith("### "):
        title = line[4:]
        anchor = re.sub(r'[^a-zA-Z0-9_-]', '', title.lower().replace(' ', '-'))
        html_lines.append(f"<h3 id='{anchor}'>{title}</h3>")
    elif line.startswith("> "):
        html_lines.append(f"<blockquote class='callout'>{line[2:]}</blockquote>")
    elif line.startswith("* **") or line.startswith("- **"):
        # Bold bullets
        formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line[2:])
        formatted = re.sub(r'`(.*?)`', r'<code>\1</code>', formatted)
        formatted = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted)
        html_lines.append(f"<li class='bullet'>{formatted}</li>")
    elif line.startswith("---"):
        html_lines.append("<hr/>")
    elif line.strip():
        formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        formatted = re.sub(r'`(.*?)`', r'<code>\1</code>', formatted)
        formatted = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted)
        html_lines.append(f"<p>{formatted}</p>")
    else:
        html_lines.append("<br/>")

body_html = "\n".join(html_lines)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>The Quant & Trading Dictionary</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<style>
  :root {{
    --bg: #ffffff;
    --text: #1f2328;
    --primary: #0969da;
    --card-bg: #f6f8fa;
    --border: #d0d7de;
    --code-bg: #f6f8fa;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: var(--text);
    background-color: #fdfdfd;
    margin: 0;
    padding: 0;
  }}
  .container {{
    max-width: 900px;
    margin: 40px auto;
    padding: 30px 40px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  }}
  h1 {{ color: #1f2328; border-bottom: 2px solid var(--border); padding-bottom: 12px; font-size: 28px; }}
  h2 {{ color: #24292f; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-top: 32px; font-size: 22px; }}
  h3 {{ color: #0969da; margin-top: 28px; font-size: 18px; }}
  .callout {{
    background: #e7f5ff;
    border-left: 4px solid #339af0;
    padding: 12px 16px;
    border-radius: 4px;
    color: #1971c2;
    margin: 16px 0;
    font-size: 14.5px;
  }}
  code {{
    background-color: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 13.5px;
    color: #b0183e;
    border: 1px solid #e1e4e8;
  }}
  pre {{
    background: #24292f;
    color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 13.5px;
  }}
  pre code {{
    background: none;
    color: #f6f8fa;
    border: none;
    padding: 0;
  }}
  li.bullet {{
    margin-bottom: 6px;
  }}
  hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 30px 0;
  }}
  .search-box {{
    width: 100%;
    padding: 12px 16px;
    font-size: 16px;
    border: 2px solid #0969da;
    border-radius: 6px;
    margin-bottom: 24px;
    box-sizing: border-box;
    outline: none;
  }}
</style>
</head>
<body>
<div class="container">
  <input type="text" id="searchInput" class="search-box" placeholder="🔍 Search any term (e.g. leverage, liquidation, beta, liquidity)...">
  <div id="content">
    {body_html}
  </div>
</div>
<script>
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', function() {{
    const query = this.value.toLowerCase().trim();
    const headings = document.querySelectorAll('h3');
    headings.forEach(h => {{
      let section = [];
      let el = h;
      while (el && el.nextElementSibling && el.nextElementSibling.tagName !== 'H3' && el.nextElementSibling.tagName !== 'H2') {{
        section.push(el);
        el = el.nextElementSibling;
      }}
      section.push(el);
      const text = section.map(e => e.innerText).join(' ').toLowerCase();
      const match = text.includes(query);
      section.forEach(e => e.style.display = match ? '' : 'none');
    }});
  }});
</script>
</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Generated QUANT_DICTIONARY.html successfully!")
