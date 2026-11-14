"""Render the four LinkedIn preview images (1200x628) and their share pages.

Each card is drawn as SVG in a 300x157 design space and scaled 4x by headless Chrome.
Share pages carry their own Open Graph tags (so LinkedIn shows the right image)
and send human visitors straight to the matching section of the portfolio.

Run from site/:  python3 tools/make_thumbnails.py
"""
import subprocess
import tempfile
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
IMG = SITE / "img" / "share"
SHARE = SITE / "share"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"

def T(x, y, s, size=12, fill="#ffffff", weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" font-family="{FONT}">{s}</text>')

FLAG_MALTA = '''<g transform="translate(234,12)">
<rect width="27" height="36" fill="#ffffff"/><rect x="27" width="27" height="36" fill="#cf142b"/>
<rect x="3.5" y="3.5" width="9" height="9" fill="#9a9a9a" stroke="#cf142b" stroke-width="0.6"/>
<path d="M8,5 v6 M5,8 h6" stroke="#ffffff" stroke-width="1.4"/>
</g>'''
FLAG_CYPRUS = '''<g transform="translate(234,12)">
<rect width="54" height="36" fill="#ffffff" stroke="#d9d9d9" stroke-width="0.4"/>
<path d="M12,17 q4,-3 10,-3 q8,-1 13,-3 q4,-2 7,-4 q1,1 -1,3 q-3,3 -8,4 q-9,3 -21,3z" fill="#d57800"/>
<path d="M17,25 q10,7 20,0" fill="none" stroke="#4e5b31" stroke-width="1.6"/>
<g fill="#4e5b31"><ellipse cx="20" cy="27.5" rx="1.6" ry="0.9"/><ellipse cx="24" cy="29.2" rx="1.6" ry="0.9"/>
<ellipse cx="30" cy="29.2" rx="1.6" ry="0.9"/><ellipse cx="34" cy="27.5" rx="1.6" ry="0.9"/></g>
</g>'''
FLAG_ALBANIA = '''<g transform="translate(234,12)">
<rect width="54" height="36" fill="#e41e20"/>
<g fill="#111111">
<path d="M25.5,15 L13,8.5 L15.5,12 L10.5,12.5 L15,15.5 L10,17 L15.5,19 L11.5,21.5 L17,22 L25.5,21z"/>
<path d="M28.5,15 L41,8.5 L38.5,12 L43.5,12.5 L39,15.5 L44,17 L38.5,19 L42.5,21.5 L37,22 L28.5,21z"/>
<ellipse cx="27" cy="20" rx="3.2" ry="6"/>
<path d="M25.5,15 L23.5,11 M28.5,15 L30.5,11" stroke="#111111" stroke-width="1.8"/>
<circle cx="23" cy="10" r="2.1"/><circle cx="31" cy="10" r="2.1"/>
<path d="M21.2,9.2 L18.6,10.4 L21.2,11z M32.8,9.2 L35.4,10.4 L32.8,11z"/>
<path d="M24.8,25 L22.5,31 L27,28.5 L31.5,31 L29.2,25z"/>
</g>
</g>'''

def chip(x, w, label, filled=False):
    if filled:
        return (f'<rect x="{x}" y="66" width="{w}" height="18" rx="3" fill="#4fb8a9"/>'
                + T(x + w / 2, 79, label, 11, "#12201e", 500, "middle"))
    return (f'<rect x="{x}" y="66" width="{w}" height="18" rx="3" fill="none" stroke="#4fb8a9" stroke-width="0.8"/>'
            + T(x + w / 2, 79, label, 11, "#4fb8a9", 400, "middle"))

CARDS = {
    "portfolio": dict(
        bg="#12201e",
        body="".join([
            T(16, 34, "H. Michael Bar Bourenane", 16, "#ffffff", 500),
            T(16, 52, "Financial crime and sanctions portfolio", 12, "#9fc9c2"),
            chip(16, 38, "OFAC"), chip(60, 34, "AML"), chip(100, 34, "SAR"),
            chip(140, 44, "OSINT"), chip(190, 34, "EDD"), chip(230, 54, "عربي", True),
            T(16, 112, "6 projects · hmichael-bar.github.io", 11, "#c9d6d3"),
            '<polyline points="16,150 50,144 84,147 118,136 152,139 186,128 220,131 254,118 284,121" fill="none" stroke="#e09a63" stroke-width="2" stroke-linejoin="round"/>',
            '<circle cx="254" cy="118" r="3.5" fill="#e09a63"/>',
        ]),
        title="H. Michael Bar Bourenane · Financial Crime & Sanctions Portfolio",
        desc="Six working projects: OFAC screening with Arabic-name matching, transaction monitoring, SARs, Cyprus shell-network map, sanctions-evasion typologies, English/Arabic adverse media.",
        target="./",
    ),
    "malta": dict(
        bg="#0c2737",
        body="".join([
            '<g stroke="#1d4256" stroke-width="0.5"><line x1="0" y1="40" x2="300" y2="40"/><line x1="0" y1="80" x2="300" y2="80"/><line x1="0" y1="120" x2="300" y2="120"/><line x1="75" y1="0" x2="75" y2="157"/><line x1="150" y1="0" x2="150" y2="157"/><line x1="225" y1="0" x2="225" y2="157"/></g>',
            '<path d="M150,46 q8,-6 16,-2 q6,4 2,9 q-8,5 -16,1 q-5,-3 -2,-8z" fill="#c8b98a"/>',
            '<path d="M143,42 q3,-2 5,0 q1,2 -2,3 q-3,0 -3,-3z" fill="#c8b98a"/>',
            T(172, 40, "Malta", 11, "#c8b98a"),
            '<polyline points="8,58 60,66 112,80" fill="none" stroke="#f0c36b" stroke-width="2"/>',
            '<polyline points="112,80 160,100 196,112" fill="none" stroke="#f0c36b" stroke-width="2" stroke-dasharray="4 4"/>',
            '<polyline points="216,120 250,128 292,138" fill="none" stroke="#f0c36b" stroke-width="2"/>',
            T(122, 76, "AIS gap", 11, "#f0c36b"),
            '<polygon points="194,108 205,112 194,116" fill="#ffffff"/><polygon points="218,114 207,118 218,122" fill="#ffffff"/>',
            '<circle cx="206" cy="115" r="12" fill="none" stroke="#e05a4f" stroke-width="1.2"/>',
            T(222, 104, "STS transfer", 11, "#e05a4f"),
            FLAG_MALTA,
            T(12, 134, "Shadow fleet off Malta", 15, "#ffffff", 500),
            T(12, 149, "AIS gaps · STS transfers · flag-hopping", 11, "#9fc0d0"),
        ]),
        title="Shadow fleet off Malta · Sanctions-evasion typology reports",
        desc="AIS gaps, ship-to-ship transfers and flag-hopping, plus Gulf free-zone TBML and crypto off-ramps, with red flags and detection controls. By H. Michael Bar Bourenane.",
        target="./#typologies",
    ),
    "cyprus": dict(
        bg="#18202c",
        body="".join([
            '<g stroke="#4fb8a9" stroke-width="1" fill="none"><line x1="140" y1="72" x2="52" y2="34"/><line x1="140" y1="72" x2="50" y2="104"/><line x1="140" y1="72" x2="214" y2="40"/><line x1="140" y1="72" x2="222" y2="100"/><line x1="52" y1="34" x2="50" y2="104" stroke-dasharray="3 3"/></g>',
            '<g stroke="#3a4d5e" stroke-width="0.6"><line x1="52" y1="34" x2="30" y2="22"/><line x1="52" y1="34" x2="72" y2="20"/><line x1="50" y1="104" x2="28" y2="116"/><line x1="50" y1="104" x2="70" y2="120"/><line x1="222" y1="100" x2="244" y2="112"/></g>',
            '<g fill="#4fb8a9"><circle cx="52" cy="34" r="5"/><circle cx="50" cy="104" r="5"/><circle cx="214" cy="40" r="5"/><circle cx="222" cy="100" r="5"/></g>',
            '<g fill="#7e93a6"><circle cx="30" cy="22" r="2.5"/><circle cx="72" cy="20" r="2.5"/><circle cx="28" cy="116" r="2.5"/><circle cx="70" cy="120" r="2.5"/><circle cx="244" cy="112" r="2.5"/></g>',
            '<circle cx="140" cy="72" r="11" fill="#d57800"/>',
            T(62, 30, "BVI", 11, "#c9d6d3"), T(60, 100, "Seychelles", 11, "#c9d6d3"),
            T(174, 36, "Russia", 11, "#c9d6d3"), T(232, 98, "UAE", 11, "#c9d6d3"),
            FLAG_CYPRUS,
            T(12, 134, "The Cyprus corridor", 15, "#ffffff", 500),
            T(12, 149, "18,297 companies mapped from ICIJ leaks", 11, "#9fb0c0"),
        ]),
        title="The Cyprus corridor · Shell-company network map",
        desc="Graph analysis of 18,297 Cyprus-linked companies from the ICIJ Offshore Leaks: hub intermediaries, nominee directors, circular ownership and sanctions/PEP screening. By H. Michael Bar Bourenane.",
        target="./#network",
    ),
    "albania": dict(
        bg="#221a1a",
        body="".join([
            '<path d="M150,108 q20,-8 40,0 t40,0 t40,0 t30,0 V157 H150z" fill="#1f4a63"/>',
            '<g fill="#e8d7c0"><rect x="168" y="78" width="14" height="30"/><rect x="186" y="64" width="14" height="44"/><rect x="204" y="52" width="14" height="56"/><rect x="222" y="70" width="14" height="38"/></g>',
            '<g fill="#221a1a"><rect x="171" y="84" width="3" height="3"/><rect x="176" y="84" width="3" height="3"/><rect x="189" y="70" width="3" height="3"/><rect x="194" y="70" width="3" height="3"/><rect x="207" y="58" width="3" height="3"/><rect x="212" y="58" width="3" height="3"/><rect x="207" y="66" width="3" height="3"/><rect x="225" y="76" width="3" height="3"/><rect x="230" y="76" width="3" height="3"/></g>',
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="#e41e20" stroke-width="1.5"/></marker></defs>',
            '<polyline points="16,60 60,58 100,72 156,74" fill="none" stroke="#e41e20" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#ah)"/>',
            T(16, 50, "Smuggling proceeds", 11, "#e8a09a"),
            FLAG_ALBANIA,
            T(12, 134, "Albania real estate", 15, "#ffffff", 500),
            T(12, 149, "Proceeds into coastal development", 11, "#c9b4ae"),
        ]),
        title="Albania real estate laundering · OSINT case study",
        desc="How smuggling proceeds move into coastal construction, traced with geolocation, property records and local-language sources. Part of a financial crime portfolio by H. Michael Bar Bourenane.",
        target="./",
    ),
}

def svg(card):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="628" viewBox="0 0 300 157">'
            f'<rect width="300" height="157" fill="{card["bg"]}"/>{card["body"]}</svg>')

def main():
    IMG.mkdir(parents=True, exist_ok=True)
    SHARE.mkdir(parents=True, exist_ok=True)
    for name, card in CARDS.items():
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:{card["bg"]}}}</style></head><body>{svg(card)}</body></html>')
            tmp = f.name
        out = IMG / f"{name}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,628",
                        f"--screenshot={out}", f"file://{tmp}"],
                       check=True, capture_output=True)
        url = f"https://hmichael-bar.github.io/share/{name}.html"
        img = f"https://hmichael-bar.github.io/img/share/{name}.png"
        target = "../" + card["target"].lstrip("./") if card["target"] != "./" else "../"
        (SHARE / f"{name}.html").write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{card["title"]}</title>
<meta name="description" content="{card["desc"]}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{card["title"]}">
<meta property="og:description" content="{card["desc"]}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="628">
<meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{url}">
</head><body><p><a href="{target}">Open the portfolio</a></p></body></html>
''', encoding="utf-8")
        print("wrote", out.relative_to(SITE), "and", (SHARE / f"{name}.html").relative_to(SITE))

if __name__ == "__main__":
    main()
