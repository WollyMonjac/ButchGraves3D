"""MANUAL.md -> docs/MANUAL.pdf: python-markdown (tables, heading ids) with a print stylesheet, printed by headless
Chromium. Image paths are made absolute so the page can be printed from anywhere.
Usage: python3 tools/manual_pdf.py [chrome] [out.html]"""
import os, subprocess, sys
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = sys.argv[1] if len(sys.argv) > 1 else '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
HTML = sys.argv[2] if len(sys.argv) > 2 else '/tmp/man_print.html'

CSS = '''@page{size:A4;margin:16mm 14mm}
body{font-family:"DejaVu Sans",Helvetica,Arial,sans-serif;color:#1f2328;font-size:10.5pt;line-height:1.45}
h1{font-size:22pt;border-bottom:2px solid #c8501a;padding-bottom:4px;color:#3a1408}
h2{font-size:16pt;border-bottom:1px solid #d1d9e0;padding-bottom:3px;margin-top:22px;color:#3a1408;page-break-after:avoid}
h3{font-size:13pt;color:#7a2a0c;page-break-after:avoid} h4{font-size:11.5pt;margin-bottom:2px;page-break-after:avoid}
code{background:#eff1f3;padding:1px 4px;border-radius:4px;font-size:90%}
table{border-collapse:collapse;width:100%;margin:6px 0;font-size:9.5pt} td,th{border:1px solid #d1d9e0;padding:4px 7px;vertical-align:top}
th{background:#f6f2ee} tr{page-break-inside:avoid}
p[align=center]{text-align:center;page-break-inside:avoid} img{page-break-inside:avoid}
a{color:#a8400f;text-decoration:none} hr{border:0;border-top:1px solid #ddd}
'''

md = open(os.path.join(ROOT, 'MANUAL.md'), encoding='utf-8').read()
body = markdown.markdown(md, extensions=['tables', 'toc'])
for d in ('docs/', 'screenshots/'):
    body = body.replace('src="' + d, 'src="' + ROOT + '/' + d)
page = ('<html><head><meta charset="utf-8"><title>Butch Graves 3D - Game Manual</title><style>\n' + CSS
        + '</style></head><body>' + body + '</body></html>')
open(HTML, 'w', encoding='utf-8').write(page)
out = os.path.join(ROOT, 'docs', 'MANUAL.pdf')
subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                '--print-to-pdf=' + out, 'file://' + HTML], check=True, stderr=subprocess.DEVNULL)
print('wrote', out)
