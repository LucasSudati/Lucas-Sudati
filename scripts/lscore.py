import json, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "lscore-state.json"
SVG = ROOT / "assets" / "lscore.svg"
RESULT = ROOT / "lscore-result.txt"

W, H = 13, 7
NODES = {"A": (4, 1), "B": (7, 5), "C": (10, 2)}
CORE = (11, 3)
START = (1, 3)
BLOCKED = {(3,0),(3,2),(3,4),(3,6),(6,1),(6,3),(6,6),(9,0),(9,4),(9,6)}

def load():
    return json.loads(STATE.read_text(encoding="utf-8"))

def save(s):
    STATE.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def render(s):
    cell, ox, oy = 34, 39, 72
    width, height = 520, 350
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" rx="18" fill="#0d1117"/>',
             '<style>text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.pulse{animation:p 1.5s ease-in-out infinite}@keyframes p{50%{opacity:.35}}@media(prefers-reduced-motion:reduce){.pulse{animation:none}}</style>',
             '<text x="28" y="34" fill="#58a6ff" font-size="17" font-weight="700">LS//CORE</text>',
             f'<text x="492" y="34" text-anchor="end" fill="#8b949e" font-size="12">MOV {s["moves"]:04d} · CORE {s["wins"]:02d}</text>',
             '<text x="28" y="54" fill="#8b949e" font-size="11">COLLABORATIVE LOGIC FIELD · ACTIVATE A B C → CORE</text>']
    for y in range(H):
        for x in range(W):
            px, py = ox+x*cell, oy+y*cell
            fill = "#161b22" if (x,y) not in BLOCKED else "#21262d"
            stroke = "#30363d"
            parts.append(f'<rect x="{px}" y="{py}" width="28" height="28" rx="5" fill="{fill}" stroke="{stroke}"/>')
    for name,(x,y) in NODES.items():
        px,py=ox+x*cell+14,oy+y*cell+18
        on=name in s["activated"]
        parts.append(f'<circle cx="{px}" cy="{py-4}" r="10" fill="{"#1f6feb" if on else "#21262d"}" stroke="#58a6ff"/>')
        parts.append(f'<text x="{px}" y="{py}" text-anchor="middle" fill="{"#fff" if on else "#8b949e"}" font-size="11" font-weight="700">{name}</text>')
    x,y=CORE; px,py=ox+x*cell+14,oy+y*cell+14
    unlocked=len(s["activated"])==3
    parts.append(f'<rect x="{px-11}" y="{py-11}" width="22" height="22" rx="4" fill="{"#1f6feb" if unlocked else "#21262d"}" stroke="#58a6ff" class="{"pulse" if unlocked else ""}"/>')
    parts.append(f'<text x="{px}" y="{py+4}" text-anchor="middle" fill="#fff" font-size="9">LS</text>')
    x,y=s["x"],s["y"]; px,py=ox+x*cell+14,oy+y*cell+14
    parts.append(f'<circle cx="{px}" cy="{py}" r="7" fill="#58a6ff" class="pulse"/>')
    active=" ".join("●" if n in s["activated"] else "○" for n in "ABC")
    player=html.escape(s.get("last_player") or "waiting")
    parts.append(f'<text x="28" y="326" fill="#8b949e" font-size="11">NODES {active} · LAST SIGNAL: {player}</text>')
    parts.append('</svg>')
    SVG.parent.mkdir(exist_ok=True)
    SVG.write_text("\n".join(parts), encoding="utf-8")

def main():
    s=load()
    title=sys.argv[1] if len(sys.argv)>1 else ""
    player=sys.argv[2] if len(sys.argv)>2 else "unknown"
    cmd=title.split(":",1)[1].strip().upper() if ":" in title else ""
    delta={"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}
    if cmd not in delta:
        RESULT.write_text("Unknown LS//CORE command.",encoding="utf-8"); render(s); return
    dx,dy=delta[cmd]; nx,ny=s["x"]+dx,s["y"]+dy
    if 0<=nx<W and 0<=ny<H and (nx,ny) not in BLOCKED:
        s["x"],s["y"]=nx,ny
    s["moves"]+=1; s["last_player"]=player
    pos=(s["x"],s["y"])
    for name,p in NODES.items():
        if pos==p and name not in s["activated"]:
            s["activated"].append(name)
    won=pos==CORE and len(s["activated"])==3
    if won:
        s["wins"]+=1; s["x"],s["y"]=START; s["activated"]=[]
    save(s); render(s)
    msg="CORE synchronized! New cycle started." if won else f"Signal moved {cmd}. Active nodes: {len(s['activated'])}/3."
    RESULT.write_text(msg,encoding="utf-8")

if __name__=="__main__":
    main()
