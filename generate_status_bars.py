from pathlib import Path
from math import floor

OUT = Path(__file__).parent / 'assets' / 'status'
OUT.mkdir(parents=True, exist_ok=True)

W,H=2048,682
FONT="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace"

THEMES={
 'light':{
   'bg':'#f8fcfe','panel':'#ffffff','panel2':'#f4fafc','text':'#0b1f2a','muted':'#68879a','grid':'#d8f0f5','line':'#18bfd0','line2':'#59d7e5','border':'#62d8e4','cyan':'#19cad8','teal':'#34d9b5','yellow':'#f2c75b','red':'#ef647b','shadow':'#d7eef4','glow':'#c7f7fa'
 },
 'dark':{
   'bg':'#050d11','panel':'#07171d','panel2':'#0a1d24','text':'#eef9ff','muted':'#87aabd','grid':'#12323c','line':'#69f0f1','line2':'#27d5de','border':'#2b6b7c','cyan':'#6af4f6','teal':'#45e7c6','yellow':'#ffd96c','red':'#ff7388','shadow':'#001015','glow':'#19c4d1'
 }
}

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def svg_open(t, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">
<defs>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="{t['grid']}" stroke-width="1" opacity="0.62"/></pattern>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['cyan']}" stop-opacity="0.30"/><stop offset="1" stop-color="{t['cyan']}" stop-opacity="0.02"/></linearGradient>
  <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="9" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<rect x="0" y="124" width="{W}" height="420" fill="url(#grid)" opacity="0.8"/>
'''

def frame(t, y=126, h=416):
    # Outer frame and cyber corner cuts
    x=2; w=W-4
    return f'''
<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{t['border']}" stroke-width="2"/>
<path d="M2 {y+40} L40 {y+2} M{W-2} {y+40} L{W-40} {y+2} M2 {y+h-40} L40 {y+h-2} M{W-2} {y+h-40} L{W-40} {y+h-2}" stroke="{t['line']}" stroke-width="2" fill="none" opacity="0.9"/>
'''

def txt(x,y,s,size,t,weight=500,anchor='start',fill=None,spacing=0):
    return f'<text x="{x}" y="{y}" fill="{fill or t["text"]}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}">{esc(s)}</text>\n'

def system_metrics(theme):
    t=THEMES[theme]
    s=svg_open(t, f'Sachith GitHub System Metrics {theme}') + frame(t)
    # Header
    s += f'<rect x="49" y="170" width="1950" height="88" fill="{t["panel"]}" fill-opacity="0.88" stroke="{t["border"]}" stroke-width="2"/>'
    s += f'<rect x="49" y="170" width="17" height="88" fill="{t["cyan"]}"/>'
    s += txt(98,224,'GITHUB // SYSTEM METRICS',38,t,800,spacing=5)
    s += txt(1900,222,'PRIMARY:',24,t,500,anchor='end',fill=t['muted'],spacing=1.8)
    s += txt(1988,222,'JAVA',24,t,800,anchor='end',fill=t['teal'],spacing=1.8)
    # Cards
    cards=[('PUBLIC REPOS','31',t['teal']),('TOTAL STARS','48',t['yellow']),('FOLLOWERS','27',t['red']),('365D SIGNALS','1.4K',t['cyan'])]
    xs=[49,532,1019,1505]
    widths=[455,463,458,493]
    bars=[[18,38,58],[18,43,64],[18,41,61],[18,39,59]]
    for i,(label,value,col) in enumerate(cards):
        x=xs[i]; w=widths[i]
        s += f'<rect x="{x}" y="289" width="{w}" height="169" fill="{t["panel"]}" fill-opacity="0.94" stroke="{t["grid"]}" stroke-width="2"/>'
        s += f'<rect x="{x}" y="289" width="{w}" height="9" fill="{col}"/>'
        s += txt(x+32,345,label,23,t,500,fill=t['muted'],spacing=2.2)
        s += txt(x+32,418,value,55,t,800)
        base=x+w-122
        for j,bh in enumerate(bars[i]):
            s += f'<rect x="{base+j*34}" y="{420-bh}" width="17" height="{bh}" fill="{col}" fill-opacity="{0.75+0.08*j}"/>'
    s += txt(52,509,'PUBLIC PROFILE TELEMETRY // CACHED SERVER-SIDE // NO CLIENT TOKEN EXPOSED',19,t,500,fill=t['muted'],spacing=0.8)
    s += '</svg>'
    return s

def contribution(theme):
    t=THEMES[theme]
    s=svg_open(t, f'Sachith Contribution Signal Graph {theme}') + frame(t,72,544)
    # Header
    s += f'<rect x="49" y="106" width="1952" height="74" fill="{t["panel"]}" fill-opacity="0.90" stroke="{t["border"]}" stroke-width="2"/>'
    s += f'<rect x="49" y="106" width="16" height="74" fill="{t["cyan"]}"/>'
    s += txt(98,157,'CONTRIBUTION // SIGNAL GRAPH',37,t,800,spacing=4.6)
    s += f'<line x1="1765" y1="129" x2="1765" y2="158" stroke="{t["line"]}" stroke-width="4" opacity="0.75"/>'
    s += txt(1986,156,'LAST 365 DAYS',23,t,500,anchor='end',fill=t['muted'],spacing=1.5)
    # chart area
    x0,y0=120,226; x1,y1=1998,470
    # horizontal grid labels 0-200
    for val in [0,50,100,150,200]:
        yy=y1-(val/200)*(y1-y0)
        s += f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{t["line"]}" stroke-width="1.4" stroke-dasharray="7 7" opacity="0.42"/>'
        s += txt(91,yy+7,str(val),21,t,500,anchor='end',fill=t['muted'])
    # vertical dashed lines 13 months
    months=['SEP','OCT','NOV','DEC','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP']
    values=[28,94,43,82,115,68,115,87,148,105,74,120,175]
    pts=[]
    for i,m in enumerate(months):
        xx=145+i*(1810/12)
        yy=y1-(values[i]/200)*(y1-y0)
        pts.append((xx,yy))
        s += f'<line x1="{xx:.1f}" y1="198" x2="{xx:.1f}" y2="{y1+16}" stroke="{t["line"]}" stroke-width="1.2" stroke-dasharray="8 8" opacity="0.45"/>'
        s += txt(xx,y1+43,m,20,t,500,anchor='middle',fill=t['muted'])
    # area path
    path='M '+ ' L '.join(f'{x:.1f} {y:.1f}' for x,y in pts) + f' L {pts[-1][0]:.1f} {y1} L {pts[0][0]:.1f} {y1} Z'
    s += f'<path d="{path}" fill="url(#fade)"/>'
    # line path
    lpath='M '+ ' L '.join(f'{x:.1f} {y:.1f}' for x,y in pts)
    s += f'<path d="{lpath}" fill="none" stroke="{t["cyan"]}" stroke-width="4"/>'
    for i,(x,y) in enumerate(pts):
        col=t['red'] if i==len(pts)-1 else t['cyan']
        filt=' filter="url(#softGlow)"' if i==len(pts)-1 and theme=='dark' else ''
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{t["panel"]}" stroke="{col}" stroke-width="4"{filt}/>'
    # axes
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{t["muted"]}" stroke-width="2" opacity="0.75"/>'
    s += f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{t["muted"]}" stroke-width="2" opacity="0.75"/>'
    # footer metrics
    s += f'<rect x="48" y="534" width="1954" height="57" fill="{t["panel"]}" fill-opacity="0.91" stroke="{t["border"]}" stroke-width="2"/>'
    s += txt(79,574,'TOTAL',20,t,500,fill=t['muted'],spacing=1.5)+txt(167,574,'1.4K',28,t,800,fill=t['cyan'],spacing=1.5)
    s += f'<line x1="372" y1="551" x2="372" y2="579" stroke="{t["line"]}" stroke-width="3" opacity="0.65"/>'
    s += txt(432,574,'CURRENT STREAK',20,t,500,fill=t['muted'],spacing=1.5)+txt(643,574,'6D',28,t,800,fill=t['yellow'],spacing=1.5)
    s += f'<line x1="831" y1="551" x2="831" y2="579" stroke="{t["line"]}" stroke-width="3" opacity="0.65"/>'
    s += txt(942,574,'BEST STREAK',20,t,500,fill=t['muted'],spacing=1.5)+txt(1114,574,'7D',28,t,800,fill=t['red'],spacing=1.5)
    s += f'<line x1="1561" y1="551" x2="1561" y2="579" stroke="{t["line"]}" stroke-width="3" opacity="0.65"/>'
    s += txt(1985,574,'SACHITH-GUNARATHNA // GITHUB',19,t,500,anchor='end',fill=t['muted'],spacing=1.0)
    s += '</svg>'
    return s

def dev_signal(theme):
    t=THEMES[theme]
    s=svg_open(t, f'Sachith Dev Signal {theme}') + frame(t,142,398)
    # header
    s += f'<rect x="49" y="184" width="1951" height="97" fill="{t["panel"]}" fill-opacity="0.92" stroke="{t["border"]}" stroke-width="2"/>'
    s += f'<rect x="49" y="184" width="16" height="97" fill="{t["cyan"]}"/>'
    s += txt(97,233,'SACHITH // DEV SIGNAL',34,t,800,spacing=4.5)
    s += txt(98,264,'LOCAL IDE HEARTBEAT • PIXEL HUD v3',20,t,500,fill=t['muted'],spacing=2.4)
    # coding now badge
    bx,by,bw,bh=1404,198,342,68
    s += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{t["panel2"]}" stroke="{t["teal"]}" stroke-width="2"/>'
    s += f'<rect x="{bx+20}" y="{by+21}" width="24" height="24" fill="{t["teal"]}" filter="url(#softGlow)"/>'
    s += txt(bx+65,by+44,'CODING NOW',22,t,700,fill=t['teal'],spacing=1.6)
    # mini signal bars
    heights=[28,55,77,51,71,43]
    cols=[t['yellow'],t['yellow'],t['teal'],t['teal'],t['red'],t['red']]
    for i,(hh,col) in enumerate(zip(heights,cols)):
        s += f'<rect x="{1794+i*29}" y="{274-hh}" width="17" height="{hh}" fill="{col}" fill-opacity="0.88"/>'
    # cards
    cards=[
      ('LANGUAGE','JAVA',t['yellow'],457),
      ('ACTIVE IDE','INTELLIJ IDEA',t['teal'],469),
      ('PROJECT','FULL-STACK WORKSPACE',t['red'],590),
      ('LAST SIGNAL','ACTIVE NOW',t['teal'],343)
    ]
    xs=[49,535,1038,1658]
    widths=[457,469,590,342]
    for i,(label,value,col,_) in enumerate(cards):
        x=xs[i]; w=widths[i]
        s += f'<rect x="{x}" y="312" width="{w}" height="158" fill="{t["panel"]}" fill-opacity="0.93" stroke="{t["border"]}" stroke-width="2"/>'
        s += f'<rect x="{x+22}" y="336" width="16" height="16" fill="{col}" fill-opacity="0.86"/>'
        s += txt(x+57,352,label,20,t,500,fill=t['muted'],spacing=2.0)
        fsize=40 if len(value)<=14 else 31
        s += txt(x+41,417,value,fsize,t,800,spacing=0.8)
        s += f'<rect x="{x+41}" y="436" width="{max(190, int(w*0.52))}" height="8" fill="{col}" fill-opacity="0.78"/>'
    s += txt(72,516,'VS CODE // INTELLIJ IDEA // ANDROID STUDIO // JAVA-FIRST FULL-STACK WORKFLOW',18,t,500,fill=t['muted'],spacing=1.0)
    s += txt(1976,516,'SYS.SACHITH',19,t,500,anchor='end',fill=t['muted'],spacing=1.3)
    s += '</svg>'
    return s

for theme in ('light','dark'):
    (OUT/f'system-metrics-{theme}.svg').write_text(system_metrics(theme),encoding='utf-8')
    (OUT/f'contribution-signal-{theme}.svg').write_text(contribution(theme),encoding='utf-8')
    (OUT/f'dev-signal-{theme}.svg').write_text(dev_signal(theme),encoding='utf-8')

print('Generated', len(list(OUT.glob('*.svg'))), 'SVG files in', OUT)
