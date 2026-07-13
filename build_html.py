#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render README.md -> index.html with MathJax + figures, for easy browsing.
Math spans are protected from the markdown converter, then rendered by MathJax."""
import re, markdown, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()

# --- protect math so python-markdown doesn't mangle underscores/backslashes ---
store = []
def stash(m):
    store.append(m.group(0))
    return f"\x00MATH{len(store)-1}\x00"
# display math $$...$$ first, then inline $...$
src = re.sub(r"\$\$.*?\$\$", stash, src, flags=re.S)
src = re.sub(r"(?<!\$)\$(?!\$).+?(?<!\$)\$(?!\$)", stash, src, flags=re.S)

body = markdown.markdown(src, extensions=["tables", "fenced_code", "toc", "sane_lists"])

# restore math (escape nothing; MathJax reads raw)
def unstash(m):
    return store[int(m.group(1))]
body = re.sub(r"\x00MATH(\d+)\x00", unstash, body)

tpl = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nuclear Compute: Power, Logic, Memory, and Interconnect in One Radioactive Medium</title>
<script>
  window.MathJax = {{ tex: {{ inlineMath: [['$','$']], displayMath: [['$$','$$']] }},
                      svg: {{ fontCache: 'global' }} }};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" id="MathJax-script" async></script>
<style>
  :root {{ --ink:#16213e; --muted:#5b6b86; --line:#e5e9f0; --bg:#fbfcfe;
           --blue:#2563eb; --red:#dc2626; --green:#16a34a; --code:#f4f6fb; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
  .wrap {{ max-width:860px; margin:0 auto; padding:48px 24px 120px; }}
  h1 {{ font-size:2.3rem; line-height:1.15; margin:.2em 0 .1em; letter-spacing:-.5px; }}
  h3 {{ color:var(--muted); font-weight:500; margin:.2em 0 1.2em; font-size:1.2rem; }}
  h2 {{ font-size:1.5rem; margin:2.4em 0 .6em; padding-top:.5em; border-top:1px solid var(--line); }}
  h2:first-of-type {{ border-top:none; }}
  a {{ color:var(--blue); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
  blockquote {{ margin:1.4em 0; padding:.8em 1.2em; background:#eef4ff;
    border-left:4px solid var(--blue); border-radius:6px; }}
  blockquote strong {{ color:var(--ink); }}
  code {{ background:var(--code); padding:.12em .35em; border-radius:4px; font-size:.9em; }}
  pre {{ background:var(--code); padding:14px 16px; border-radius:8px; overflow-x:auto; }}
  img {{ max-width:100%; display:block; margin:1.5em auto; border:1px solid var(--line);
    border-radius:10px; background:#fff; box-shadow:0 4px 18px rgba(22,33,62,.06); }}
  table {{ border-collapse:collapse; width:100%; margin:1.4em 0; font-size:.93rem; }}
  th,td {{ border:1px solid var(--line); padding:8px 11px; text-align:left; vertical-align:top; }}
  th {{ background:#eef2fa; }}
  tr:nth-child(even) td {{ background:#fafbfe; }}
  hr {{ border:none; border-top:1px solid var(--line); margin:2.5em 0; }}
  mjx-container {{ overflow-x:auto; overflow-y:hidden; max-width:100%; }}
  .wrap > p:first-of-type {{ font-size:1.05rem; }}
</style></head>
<body><div class="wrap">
{body}
<hr><p style="color:var(--muted);font-size:.85rem">© 2026 Max Freedom Pollard
(<a href="https://orcid.org/0009-0007-0059-3319">ORCID 0009-0007-0059-3319</a>).
Text and figures CC BY 4.0; code MIT.</p>
</div></body></html>"""

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(tpl)
print("wrote index.html  (", len(tpl), "bytes )")
