"""Write the SVG figures for accounts-install/. Run from the repo root: python3 accounts-install/make-figs.py accounts-install"""
import sys, os
from xml.sax.saxutils import escape as esc

OUT = sys.argv[1]
TEAL, PURPLE, CRIMSON, OCHRE = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12"
DARK, MID, LIGHT, PALE, BG = "#1b2a3a", "#5a6670", "#c9d3dd", "#f4f7fa", "#ffffff"
TEAL_L, PURPLE_L, CRIMSON_L, OCHRE_L = "#e3f1f3", "#eee9f6", "#f7e6ea", "#f5efdf"
TERM_BG, TERM_FG = "#1e2630", "#e8edf2"
FONT = "Helvetica, Arial, sans-serif"
MONO = "Menlo, Consolas, 'DejaVu Sans Mono', monospace"


def svg(name, w, h, body):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
         f'font-family="{FONT}">\n'
         '  <defs>\n'
         f'    <marker id="arw" markerWidth="10" markerHeight="10" refX="7" refY="3.4" orient="auto">'
         f'<path d="M0,0 L7.5,3.4 L0,6.8 Z" fill="{DARK}"/></marker>\n'
         f'    <marker id="arwt" markerWidth="10" markerHeight="10" refX="7" refY="3.4" orient="auto">'
         f'<path d="M0,0 L7.5,3.4 L0,6.8 Z" fill="{TEAL}"/></marker>\n'
         f'    <marker id="arwc" markerWidth="10" markerHeight="10" refX="7" refY="3.4" orient="auto">'
         f'<path d="M0,0 L7.5,3.4 L0,6.8 Z" fill="{CRIMSON}"/></marker>\n'
         f'    <marker id="arwo" markerWidth="10" markerHeight="10" refX="7" refY="3.4" orient="auto">'
         f'<path d="M0,0 L7.5,3.4 L0,6.8 Z" fill="#e6b84f"/></marker>\n'
         '  </defs>\n'
         f'  <rect x="0" y="0" width="{w}" height="{h}" fill="{BG}"/>\n'
         + body + '</svg>\n')
    with open(os.path.join(OUT, name), "w") as f:
        f.write(s)


def text(x, y, s, size=20, fill=DARK, anchor="start", weight="normal", family=None, style=""):
    fam = f' font-family="{family}"' if family else ""
    st = f' font-style="{style}"' if style else ""
    return (f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{fam}{st} xml:space="preserve">{esc(s)}</text>\n')


def lines(x, y, rows, size=20, fill=DARK, anchor="start", weight="normal", dy=None, family=None):
    dy = dy or size * 1.3
    return "".join(text(x, y + i * dy, r, size, fill, anchor, weight, family) for i, r in enumerate(rows))


def rect(x, y, w, h, fill=PALE, stroke=LIGHT, rx=8, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n'


def arrow(x1, y1, x2, y2, color=DARK, sw=2.5, marker="arw", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" marker-end="url(#{marker})"{d}/>\n'


def illustrative(w, h):
    return text(w - 10, h - 10, "illustrative", 14, "#9aa4ad", "end", style="italic")


def terminal(x, y, w, h, title, rows, size=18, dy=None):
    """rows: list of (text, color) or str."""
    dy = dy or size * 1.45
    b = rect(x, y, w, h, TERM_BG, "#3a4654", rx=10, sw=1.5)
    b += f'  <rect x="{x}" y="{y}" width="{w}" height="34" rx="10" fill="#2d3743"/>\n'
    b += f'  <rect x="{x}" y="{y+24}" width="{w}" height="10" fill="#2d3743"/>\n'
    for i, c in enumerate(["#e0605a", "#e6b84f", "#5fbf6a"]):
        b += f'  <circle cx="{x+20+i*22}" cy="{y+17}" r="6.5" fill="{c}"/>\n'
    b += text(x + w / 2, y + 23, title, 15, "#b8c2cc", "middle")
    for i, r in enumerate(rows):
        if isinstance(r, str):
            r = (r, TERM_FG)
        b += text(x + 18, y + 34 + 28 + i * dy, r[0], size, r[1], family=MONO)
    return b


# ---------------------------------------------------------------- fig01
def fig01():
    W, H = 1000, 230
    steps = [("1", "Account", "a plan that\nincludes the agent", TEAL, TEAL_L),
             ("2", "Install", "one line pasted\ninto a terminal", PURPLE, PURPLE_L),
             ("3", "Sign in", "once, through\nthe browser", OCHRE, OCHRE_L),
             ("4", "Hello", "first test in an\nempty folder", CRIMSON, CRIMSON_L)]
    b = ""
    bw, gap = 205, 40
    x0 = (W - (4 * bw + 3 * gap)) / 2
    for i, (n, t, sub, c, cl) in enumerate(steps):
        x = x0 + i * (bw + gap)
        b += rect(x, 40, bw, 150, cl, c, rx=12, sw=2.5)
        b += f'  <circle cx="{x+30}" cy="{72}" r="18" fill="{c}"/>\n'
        b += text(x + 30, 79, n, 20, "#ffffff", "middle", "bold")
        b += text(x + 60, 80, t, 26, c, "start", "bold")
        b += lines(x + bw / 2, 128, sub.split("\n"), 19, DARK, "middle")
        if i < 3:
            b += arrow(x + bw + 4, 115, x + bw + gap - 6, 115)
    b += text(W / 2, 222, "Each step takes minutes. A failure in any one of them stops everything after it.", 18, MID, "middle")
    svg("fig01-path-to-hello.svg", W, H, b)


# ---------------------------------------------------------------- fig02
def fig02():
    W, H = 640, 520
    b = ""
    # laptop
    b += rect(30, 150, 340, 300, PALE, LIGHT, rx=14, sw=2)
    b += text(200, 182, "Your computer", 22, DARK, "middle", "bold")
    b += rect(60, 205, 280, 95, PURPLE_L, PURPLE, rx=10, sw=2.5)
    b += text(200, 240, "2. Agent program", 22, PURPLE, "middle", "bold")
    b += text(200, 270, "claude  /  codex", 19, DARK, "middle", family=MONO)
    b += rect(60, 325, 280, 95, OCHRE_L, OCHRE, rx=10, sw=2.5)
    b += text(200, 360, "3. Terminal", 22, OCHRE, "middle", "bold")
    b += text(200, 390, "where you type", 19, DARK, "middle")
    b += arrow(200, 323, 200, 305)
    # cloud
    b += ('  <path d="M455,120 C430,120 420,95 440,80 C440,50 480,40 500,58 C515,30 570,30 580,62 '
          f'C610,55 630,80 615,100 C635,115 620,140 595,138 L470,138 C455,138 445,130 455,120 Z" '
          f'fill="{TEAL_L}" stroke="{TEAL}" stroke-width="2.5"/>\n')
    b += text(528, 100, "AI model", 20, TEAL, "middle", "bold")
    b += text(528, 124, "(company servers)", 15, DARK, "middle")
    b += rect(420, 190, 200, 110, TEAL_L, TEAL, rx=10, sw=2.5)
    b += text(520, 225, "1. Account", 22, TEAL, "middle", "bold")
    b += lines(520, 255, ["plan + usage", "limits"], 18, DARK, "middle")
    b += arrow(520, 188, 525, 145)
    b += f'  <path d="M340,250 C380,250 380,165 440,140" fill="none" stroke="{DARK}" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#arw)"/>\n'
    b += text(410, 330, "internet", 17, MID, "middle", style="italic")
    b += text(320, 495, "Claude Code and Codex each need their own account and program.", 17, MID, "middle")
    svg("fig02-three-pieces.svg", W, H, b)


# ---------------------------------------------------------------- fig03
def fig03():
    W, H = 640, 520
    b = ""
    b += text(170, 40, "Claude", 24, PURPLE, "middle", "bold")
    b += text(470, 40, "ChatGPT", 24, TEAL, "middle", "bold")
    cl = [("Max / Team / Enterprise", True), ("Pro", True), ("Free", False)]
    co = [("Pro / Business / Edu / Ent.", True), ("Plus", True), ("Go", None), ("Free", None)]
    def ladder(cx, items, c, cl_):
        out = ""
        n = len(items)
        top = 70
        hstep = 330 / n
        for i, (name, ok) in enumerate(items):
            y = top + i * hstep
            if ok is True:
                f, s = cl_, c
            elif ok is None:
                f, s = "#f7f7f7", "#b9c2ca"
            else:
                f, s = "#ffffff", "#b9c2ca"
            out += rect(cx - 135, y, 270, hstep - 14, f, s, rx=8, sw=2, dash=None if ok else "6 4")
            out += text(cx, y + (hstep - 14) / 2 + 7, name, 19, DARK if ok is not False else MID, "middle", "bold" if ok else "normal")
        return out
    b += ladder(170, cl, PURPLE, PURPLE_L)
    b += ladder(470, co, TEAL, TEAL_L)
    # annotations
    b += text(170, 435, "Free: no Claude Code", 18, CRIMSON, "middle", "bold")
    b += text(470, 435, "Free / Go: some Codex,", 18, OCHRE, "middle", "bold")
    b += text(470, 457, "low limits", 18, OCHRE, "middle", "bold")
    b += f'  <line x1="20" y1="478" x2="620" y2="478" stroke="{LIGHT}" stroke-width="1.5"/>\n'
    b += rect(40, 488, 22, 18, PURPLE_L, PURPLE, rx=3, sw=2)
    b += text(70, 503, "includes the agent; enough for the course", 16, DARK)
    b += text(620, 503, "or: API billing", 16, MID, "end", style="italic")
    svg("fig03-plan-ladders.svg", W, H, b)


# ---------------------------------------------------------------- fig04
def fig04():
    W, H = 640, 460
    b = ""
    # e-mail mock
    b += rect(30, 30, 580, 300, "#ffffff", "#aab5bf", rx=10, sw=2)
    b += f'  <rect x="30" y="30" width="580" height="44" rx="10" fill="{PALE}"/>\n'
    b += f'  <rect x="30" y="62" width="580" height="12" fill="{PALE}"/>\n'
    b += text(50, 58, "New message", 18, MID, weight="bold")
    b += text(50, 105, "To:  IT service desk", 18, DARK)
    b += text(50, 135, "Subject:  AI coding agents", 18, DARK)
    b += f'  <line x1="50" y1="150" x2="590" y2="150" stroke="{LIGHT}" stroke-width="1.5"/>\n'
    b += lines(50, 185, ["Hello,",
                         "do we have a Claude or ChatGPT plan, and",
                         "does it include Claude Code or Codex?",
                         "If so, how do I get access?"], 19, DARK, dy=28)
    b += text(50, 312, "Thanks!", 19, DARK)
    # outcomes
    b += rect(30, 360, 280, 80, TEAL_L, TEAL, rx=10, sw=2)
    b += lines(170, 392, ["Yes: use the institutional", "account (often better data terms)"], 17, DARK, "middle")
    b += rect(330, 360, 280, 80, OCHRE_L, OCHRE, rx=10, sw=2)
    b += lines(470, 392, ["No: get Claude Pro or", "ChatGPT Plus yourself"], 17, DARK, "middle")
    b += illustrative(W, H)
    svg("fig04-ask-it.svg", W, H, b)


# ---------------------------------------------------------------- fig05
def fig05():
    W, H = 640, 440
    b = ""
    # subscription: bar with cap
    b += text(160, 40, "Subscription", 24, PURPLE, "middle", "bold")
    b += text(480, 40, "API key", 24, TEAL, "middle", "bold")
    # sub chart
    b += f'  <line x1="50" y1="320" x2="290" y2="320" stroke="{DARK}" stroke-width="2"/>\n'
    b += f'  <line x1="50" y1="320" x2="50" y2="80" stroke="{DARK}" stroke-width="2"/>\n'
    hs = [90, 160, 180, 180, 60, 180, 120]
    for i, h in enumerate(hs):
        col = CRIMSON if h == 180 else PURPLE
        b += f'  <rect x="{62+i*32}" y="{320-h}" width="22" height="{h}" fill="{col}" opacity="0.85"/>\n'
    b += f'  <line x1="50" y1="140" x2="290" y2="140" stroke="{CRIMSON}" stroke-width="2.5" stroke-dasharray="8 5"/>\n'
    b += text(290, 130, "limit: wait for reset", 16, CRIMSON, "end", "bold")
    b += text(170, 345, "use per day", 16, MID, "middle")
    b += lines(170, 380, ["Fixed monthly cost.", "No surprise bills."], 18, DARK, "middle")
    # API meter
    b += f'  <line x1="370" y1="320" x2="610" y2="320" stroke="{DARK}" stroke-width="2"/>\n'
    b += f'  <line x1="370" y1="320" x2="370" y2="80" stroke="{DARK}" stroke-width="2"/>\n'
    pts = [(370, 318), (402, 300), (434, 270), (466, 240), (498, 232), (530, 180), (562, 120), (600, 85)]
    b += '  <polyline points="' + " ".join(f"{x},{y}" for x, y in pts) + f'" fill="none" stroke="{TEAL}" stroke-width="3.5"/>\n'
    b += text(380, 105, "cost so far", 16, TEAL, "start", "bold")
    b += text(490, 345, "days in the month", 16, MID, "middle")
    b += lines(490, 380, ["Pay per use.", "No waiting, no cap."], 18, DARK, "middle")
    svg("fig05-subscription-vs-api.svg", W, H, b)


# ---------------------------------------------------------------- fig06
def fig06():
    W, H = 1000, 330
    b = ""
    # chat
    b += rect(20, 20, 440, 290, PALE, LIGHT, rx=12, sw=2)
    b += text(240, 55, "Chat in the browser", 22, DARK, "middle", "bold")
    b += rect(50, 75, 380, 150, "#ffffff", "#aab5bf", rx=8)
    b += rect(70, 95, 230, 34, "#e9edf1", "#e9edf1", rx=14)
    b += text(85, 118, "[pasted text]", 17, MID)
    b += rect(180, 145, 230, 60, PURPLE_L, PURPLE_L, rx=14)
    b += lines(195, 170, ["Here is a summary", "of your text..."], 16, DARK)
    b += lines(240, 262, ["Sees only what you paste.", "Your files stay where they are."], 18, DARK, "middle")
    # agent
    b += rect(540, 20, 440, 290, TEAL_L, TEAL, rx=12, sw=2)
    b += text(760, 55, "Agent on your computer", 22, TEAL, "middle", "bold")
    b += terminal(565, 75, 190, 150, "agent", [("> make a plot", TERM_FG), ("reading data.csv", "#8fd0dc"), ("running R...", "#8fd0dc")], 14, 24)
    # folder
    b += f'  <path d="M800,95 L840,95 L852,107 L950,107 L950,215 L800,215 Z" fill="#ffffff" stroke="{OCHRE}" stroke-width="2.5"/>\n'
    b += text(875, 135, "project", 16, OCHRE, "middle", "bold")
    b += lines(815, 160, ["data.csv", "plot.R", "figure.png"], 15, DARK, dy=20)
    b += arrow(757, 150, 795, 150, TEAL, 2.5, "arwt")
    b += lines(760, 262, ["Reads, writes and runs things", "in the folder you start it in."], 18, DARK, "middle")
    svg("fig06-chat-vs-local.svg", W, H, b)


# ---------------------------------------------------------------- fig07
def fig07():
    W, H = 640, 470
    b = ""
    b += rect(220, 300, 200, 110, PURPLE_L, PURPLE, rx=12, sw=2.5)
    b += lines(320, 345, ["same agent", "engine"], 21, PURPLE, "middle", "bold")
    items = [(110, "Terminal", "used in this course", TEAL, TEAL_L, True),
             (320, "Desktop app", "fallback", MID, PALE, False),
             (530, "Editor extension", "e.g. VS Code", MID, PALE, False)]
    for cx, t, s, c, cl, main in items:
        b += rect(cx - 100, 60, 200, 130, cl, c, rx=12, sw=3 if main else 2)
        b += text(cx, 115, t, 21, c if main else DARK, "middle", "bold")
        b += text(cx, 145, s, 17, DARK, "middle", style="italic" if not main else "")
        b += arrow(cx, 195, 320 + (cx - 320) * 0.35, 295, MID, 2)
    b += rect(2, 50, 216, 150, "none", TEAL, rx=16, sw=2, dash="6 4")
    b += text(320, 445, "Same instructions on Windows, macOS and Linux.", 18, MID, "middle")
    svg("fig07-surfaces.svg", W, H, b)


# ---------------------------------------------------------------- fig08
def fig08():
    W, H = 1000, 300
    b = ""
    data = [("macOS", "Cmd + Space", "type Terminal, Enter", "you@mac ~ %"),
            ("Windows", "Win + X", "choose Terminal / PowerShell", "PS C:\\Users\\you>"),
            ("Linux", "Ctrl + Alt + T", "or search Terminal", "you@pc:~$")]
    for i, (os_, keys, sub, prompt) in enumerate(data):
        x = 20 + i * 330
        b += text(x + 145, 34, os_, 24, DARK, "middle", "bold")
        # key caps
        parts = keys.split(" + ")
        kw = [max(60, 16 * len(p) + 20) for p in parts]
        total = sum(kw) + 30 * (len(parts) - 1)
        kx = x + 145 - total / 2
        for j, p in enumerate(parts):
            b += rect(kx, 52, kw[j], 44, "#ffffff", DARK, rx=7, sw=2)
            b += text(kx + kw[j] / 2, 81, p, 19, DARK, "middle", "bold")
            kx += kw[j]
            if j < len(parts) - 1:
                b += text(kx + 15, 81, "+", 20, MID, "middle")
                kx += 30
        b += text(x + 145, 124, sub, 17, MID, "middle")
        b += terminal(x, 145, 290, 125, os_, [(prompt + " _", TERM_FG)], 17)
    b += illustrative(W, H)
    svg("fig08-open-terminal.svg", W, H, b)


# ---------------------------------------------------------------- fig09
def fig09():
    W, H = 600, 470
    b = ""
    b += terminal(20, 20, 560, 170, "Windows PowerShell", [("Windows PowerShell", "#b8c2cc"), ("", TERM_FG), ("PS C:\\Users\\you> _", TERM_FG)], 18)
    b += f'  <rect x="32" y="113" width="36" height="30" rx="4" fill="none" stroke="#5fd0a0" stroke-width="2.5"/>\n'
    b += text(590, 222, "PowerShell: starts with PS. Use this one.", 18, TEAL, "end", "bold")
    b += terminal(20, 250, 560, 150, "Command Prompt", [("Microsoft Windows", "#b8c2cc"), ("", TERM_FG), ("C:\\Users\\you> _", TERM_FG)], 18)
    b += text(590, 432, "CMD: no PS. Needs a different install line.", 18, CRIMSON, "end", "bold")
    b += illustrative(W, H)
    svg("fig09-powershell-vs-cmd.svg", W, H, b)


# ---------------------------------------------------------------- fig10
def fig10():
    W, H = 1000, 380
    b = ""
    rows = [("you@mac ~ % curl -fsSL https://claude.ai/install.sh | bash", TERM_FG),
            ("Setting up Claude Code...", "#8fd0dc"),
            ("", TERM_FG),
            ("✔ Claude Code successfully installed!", "#7fdc9a"),
            ("  Location: ~/.local/bin/claude", "#b8c2cc"),
            ("  Next: Run claude --help to get started", "#b8c2cc"),
            ("", TERM_FG),
            ("you@mac ~ % _", TERM_FG)]
    b += terminal(20, 20, 960, 330, "Terminal", rows, 19, 32)
    b += text(980, 372, "illustrative: your wording and version will differ", 14, "#9aa4ad", "end", style="italic")
    b += arrow(420, 175, 695, 175, "#e6b84f", 3, "arwo")
    b += rect(705, 150, 255, 52, "#fff6dc", "#e6b84f", rx=8, sw=2)
    b += text(832, 182, "the line you look for", 18, DARK, "middle", "bold")
    svg("fig10-install-session.svg", W, H, b)


# ---------------------------------------------------------------- fig11
def fig11():
    W, H = 1000, 300
    b = ""
    boxes = [(20, "1. Download", "installer script", "from claude.ai or", "chatgpt.com", TEAL, TEAL_L),
             (270, "2. Put program", "in a folder in your", "home directory", "~/.local/bin", PURPLE, PURPLE_L),
             (520, "3. Add to PATH", "the list of folders", "the terminal searches", "", OCHRE, OCHRE_L),
             (770, "4. Type the name", "claude  /  codex", "starts the program", "", CRIMSON, CRIMSON_L)]
    for x, t, a, c, d, col, cl in boxes:
        b += rect(x, 40, 210, 160, cl, col, rx=12, sw=2.5)
        b += text(x + 105, 78, t, 22, col, "middle", "bold")
        b += text(x + 105, 115, a, 17, DARK, "middle", family=MONO if "claude" in a else None)
        b += text(x + 105, 140, c, 17, DARK, "middle")
        if d:
            b += text(x + 105, 165, d, 17, DARK, "middle", family=MONO if d.startswith("~") else None)
        if x < 770:
            b += arrow(x + 213, 120, x + 255, 120)
    b += rect(520, 225, 460, 55, "#ffffff", OCHRE, rx=8, sw=1.5, dash="5 4")
    b += text(535, 248, "PATH:", 16, OCHRE, weight="bold")
    b += text(595, 248, "/usr/bin   /bin   ~/.local/bin   ...", 16, DARK, family=MONO)
    b += text(535, 270, "folder not on the list → \"command not found\"", 16, CRIMSON)
    svg("fig11-what-install-does.svg", W, H, b)


# ---------------------------------------------------------------- fig12
def fig12():
    W, H = 640, 470
    b = ""
    b += terminal(20, 20, 600, 150, "Window opened BEFORE install", [("$ claude --version", TERM_FG), ("command not found: claude", "#f08a8a")], 18)
    b += text(320, 200, "still has the old PATH list", 18, CRIMSON, "middle", "bold")
    b += arrow(320, 215, 320, 255)
    b += text(340, 245, "close it, open a new one", 17, DARK)
    b += terminal(20, 270, 600, 150, "NEW window", [("$ claude --version", TERM_FG), ("2.1.330 (Claude Code)", "#7fdc9a")], 18)
    b += text(320, 450, "reads the updated PATH when it opens", 18, TEAL, "middle", "bold")
    b += illustrative(W, H - 0)
    svg("fig12-reopen-terminal.svg", W, H, b)


# ---------------------------------------------------------------- fig13
def fig13():
    W, H = 1000, 340
    b = ""
    b += terminal(20, 30, 360, 230, "Terminal", [("$ claude", TERM_FG), ("Select login method:", "#b8c2cc"), ("❯ 1. Claude account", "#8fd0dc"), ("     with subscription", "#8fd0dc"), ("  2. Console account", "#b8c2cc"), ("     (API billing)", "#b8c2cc")], 16, 26)
    # browser
    b += rect(560, 30, 420, 230, "#ffffff", "#aab5bf", rx=10, sw=2)
    b += f'  <rect x="560" y="30" width="420" height="40" rx="10" fill="{PALE}"/>\n'
    b += f'  <rect x="560" y="58" width="420" height="12" fill="{PALE}"/>\n'
    b += rect(580, 40, 380, 22, "#ffffff", LIGHT, rx=11, sw=1)
    b += text(595, 57, "claude.ai / chatgpt.com", 14, MID)
    b += text(770, 110, "Log in", 24, DARK, "middle", "bold")
    b += rect(640, 130, 260, 36, PALE, LIGHT, rx=6)
    b += text(655, 154, "you@university.se", 16, MID)
    b += rect(670, 185, 200, 44, TEAL, TEAL, rx=8)
    b += text(770, 214, "Authorize", 19, "#ffffff", "middle", "bold")
    # arrows
    b += arrow(385, 110, 552, 110, DARK, 2.5)
    b += text(468, 98, "opens", 16, MID, "middle")
    b += f'  <path d="M640,268 C600,320 440,320 400,268" fill="none" stroke="{TEAL}" stroke-width="2.5" marker-end="url(#arwt)"/>\n'
    b += text(520, 330, "signed in: back to the terminal", 17, TEAL, "middle", "bold")
    b += illustrative(W, 25)
    svg("fig13-browser-login.svg", W, H, b)


# ---------------------------------------------------------------- fig14
def fig14():
    W, H = 600, 420
    b = ""
    b += rect(20, 20, 560, 370, "#ffffff", "#aab5bf", rx=10, sw=2)
    b += f'  <rect x="20" y="20" width="560" height="40" rx="10" fill="{PALE}"/>\n'
    b += f'  <rect x="20" y="48" width="560" height="12" fill="{PALE}"/>\n'
    b += text(40, 46, "you (home folder)", 17, MID, weight="bold")
    b += f'  <line x1="180" y1="60" x2="180" y2="390" stroke="{LIGHT}" stroke-width="1.5"/>\n'
    b += lines(35, 95, ["Home", "Desktop", "Documents", "Downloads"], 16, MID, dy=30)
    def folder(x, y, name, hl=False):
        c = TEAL if hl else "#9aa8b5"
        f = TEAL_L if hl else PALE
        o = f'  <path d="M{x},{y} L{x+30},{y} L{x+40},{y+10} L{x+90},{y+10} L{x+90},{y+70} L{x},{y+70} Z" fill="{f}" stroke="{c}" stroke-width="2.5"/>\n'
        o += text(x + 45, y + 95, name, 16, DARK if hl else MID, "middle", "bold" if hl else "normal")
        return o
    b += folder(210, 90, "Teaching")
    b += folder(340, 90, "Grants")
    b += folder(470, 90, "Papers")
    b += folder(210, 230, "agent-hello", True)
    b += rect(195, 215, 120, 135, "none", CRIMSON, rx=10, sw=2.5)
    b += lines(340, 270, ["new and empty:", "start the agent here"], 18, CRIMSON, weight="bold", dy=26)
    b += text(W - 10, H - 8, "illustrative", 14, "#9aa4ad", "end", style="italic")
    svg("fig14-empty-folder.svg", W, H, b)


# ---------------------------------------------------------------- fig15
def fig15():
    W, H = 1000, 420
    b = ""
    rows = [("~/agent-hello $ claude", "#b8c2cc"),
            ("", TERM_FG),
            ("> Which folder are we in, and what files can you see?", "#ffffff"),
            ("", TERM_FG),
            ("● List files in the current folder", "#8fd0dc"),
            ("  (no files)", "#b8c2cc"),
            ("", TERM_FG),
            ("● We are in /Users/you/agent-hello.", TERM_FG),
            ("  The folder is empty: there are no files here yet.", TERM_FG),
            ("  What would you like to create?", TERM_FG)]
    b += terminal(20, 20, 960, 370, "Claude Code (Codex looks similar)", rows, 18, 30)
    b += f'  <rect x="32" y="178" width="470" height="64" rx="6" fill="none" stroke="#e6b84f" stroke-width="2.5"/>\n'
    b += text(970, 230, "it looked before answering", 17, "#e6b84f", "end", "bold")
    b += text(980, 412, "illustrative: wording differs between runs and tools", 14, "#9aa4ad", "end", style="italic")
    svg("fig15-first-hello.svg", W, H, b)


# ---------------------------------------------------------------- fig16
def fig16():
    W, H = 640, 400
    b = ""
    rows = [("Create file hello.txt", "#ffffff"),
            ("", TERM_FG),
            ("Do you want to create hello.txt?", "#e6b84f"),
            ("❯ 1. Yes", "#8fd0dc"),
            ("  2. Yes, and don't ask again", "#b8c2cc"),
            ("  3. No, and tell Claude what to", "#b8c2cc"),
            ("     do differently", "#b8c2cc")]
    b += terminal(20, 20, 600, 290, "permission question", rows, 18, 30)
    b += text(320, 345, "Today: Yes, in your empty folder.", 19, TEAL, "middle", "bold")
    b += text(320, 375, "Next unit: how to read these properly.", 18, MID, "middle")
    b += text(W - 10, H - 6, "illustrative", 14, "#9aa4ad", "end", style="italic")
    svg("fig16-permission-teaser.svg", W, H, b)


# ---------------------------------------------------------------- fig17
def fig17():
    W, H = 600, 440
    b = ""
    cx, cy, r = 300, 210, 140
    b += f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LIGHT}" stroke-width="10"/>\n'
    b += f'  <path d="M{cx+r},{cy} A{r},{r} 0 0,1 {cx+12},{cy+r-1}" fill="none" stroke="{TEAL}" stroke-width="10"/>\n'
    b += f'  <path d="M{cx-r},{cy} A{r},{r} 0 0,1 {cx-12},{cy-r+1}" fill="none" stroke="{TEAL}" stroke-width="10"/>\n'
    b += f'  <path d="M{cx+14},{cy+r-14} L{cx-14},{cy+r} L{cx+14},{cy+r+14} Z" fill="{TEAL}"/>\n'
    b += f'  <path d="M{cx-14},{cy-r-14} L{cx+14},{cy-r} L{cx-14},{cy-r+14} Z" fill="{TEAL}"/>\n'
    b += text(cx, cy - 8, "new version", 22, DARK, "middle", "bold")
    b += text(cx, cy + 22, "every week or so", 18, MID, "middle")
    items = [(cx, 45, "release"), (cx + r + 20, cy + 6, "download"), (cx, cy + r + 42, "used at next start"), (cx - r - 20, cy + 6, "you work")]
    anchors = ["middle", "start", "middle", "end"]
    for (x, y, t), a in zip(items, anchors):
        b += text(x, y, t, 18, DARK, a)
    b += text(cx, 425, "Screen looks different from the course? Update first.", 17, CRIMSON, "middle", "bold")
    svg("fig17-update-cycle.svg", W, H, b)


# ---------------------------------------------------------------- fig18
def fig18():
    W, H = 1000, 280
    b = ""
    b += terminal(20, 20, 380, 120, "Terminal", [("$ claude", TERM_FG), ("command not found: claude", "#f08a8a")], 18)
    b += text(210, 175, "The terminal looks in each", 17, DARK, "middle")
    b += text(210, 198, "PATH folder in turn ...", 17, DARK, "middle")
    folders = [("/usr/bin", False), ("/bin", False), ("/usr/local/bin", False)]
    x = 450
    for i, (f, ok) in enumerate(folders):
        b += rect(x + i * 135, 40, 120, 70, PALE, "#9aa8b5", rx=8, sw=2)
        b += text(x + i * 135 + 60, 82, f, 15, DARK, "middle", family=MONO)
        b += text(x + i * 135 + 60, 135, "✗", 24, CRIMSON, "middle", "bold")
    b += arrow(405, 75, 445, 75)
    b += rect(450, 170, 400, 90, CRIMSON_L, CRIMSON, rx=10, sw=2, dash="7 5")
    b += text(470, 200, "~/.local/bin/claude", 17, DARK, family=MONO)
    b += text(470, 228, "installed, but this folder is not", 17, CRIMSON, weight="bold")
    b += text(470, 250, "on the list (yet)", 17, CRIMSON, weight="bold")
    b += text(870, 210, "fix: new", 17, TEAL, weight="bold")
    b += text(870, 232, "terminal,", 17, TEAL, weight="bold")
    b += text(870, 254, "then PATH", 17, TEAL, weight="bold")
    svg("fig18-command-not-found.svg", W, H, b)


# ---------------------------------------------------------------- fig19
def fig19():
    W, H = 640, 515
    b = ""
    def box(x, y, w, h, t, col, cl, size=18):
        o = rect(x, y, w, h, cl, col, rx=10, sw=2.5)
        rows = t.split("\n")
        y0 = y + h / 2 - (len(rows) - 1) * size * 0.65 + size * 0.35
        o += lines(x + w / 2, y0, rows, size, DARK, "middle", dy=size * 1.3)
        return o
    b += box(170, 20, 300, 70, "Paste the official\ninstall line", DARK, PALE)
    b += arrow(320, 92, 320, 125)
    b += box(170, 130, 300, 60, "Did it work?", DARK, "#ffffff")
    b += arrow(470, 160, 520, 160, TEAL, 2.5, "arwt")
    b += text(495, 150, "yes", 16, TEAL, "middle", "bold")
    b += box(525, 130, 105, 60, "done", TEAL, TEAL_L)
    b += arrow(320, 192, 320, 225, CRIMSON, 2.5, "arwc")
    b += text(335, 215, "error", 16, CRIMSON, "start", "bold")
    b += box(130, 230, 380, 85, "certificate / TLS, 403,\n\"scripts disabled\", blocked site", CRIMSON, CRIMSON_L, 17)
    b += arrow(250, 317, 160, 370)
    b += arrow(390, 317, 480, 370)
    b += box(20, 375, 280, 100, "Send IT the error\n+ official install page", OCHRE, OCHRE_L, 17)
    b += box(340, 375, 280, 100, "Meanwhile: desktop app\n(software centre?)", PURPLE, PURPLE_L, 17)
    b += text(320, 505, "Do not try to work around IT security.", 15, MID, "middle", style="italic")
    svg("fig19-managed-laptop.svg", W, H, b + "")


for f in [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10,
          fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18, fig19]:
    f()
print("ok")
