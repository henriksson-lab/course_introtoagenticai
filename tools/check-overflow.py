"""Measure rendered reveal.js slide heights with headless Chrome.

Usage: python3 tools/check-overflow.py <unit> [<unit> ...]
  (units = folder names; render first with `quarto render`, decks are read from docs/)
Needs google-chrome. If a deck prints FAILED (timeout), run it again on its own.
Prints, per slide: index, content height (px), slide id. Overflow = height > 720.
"""
import re, subprocess, sys, os, html, concurrent.futures as cf

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import tempfile
SCR = tempfile.mkdtemp(prefix='overflow-')
JS = r"""
<script>
(function(){
  function go(){
    if (!(window.Reveal && Reveal.isReady && Reveal.isReady())) { setTimeout(go, 100); return; }
    var slides = Reveal.getSlides(); var out = []; var i = 0;
    function step(){
      if (i >= slides.length) {
        var pre = document.createElement('pre'); pre.id = 'ovf'; pre.textContent = out.join('\n');
        document.body.appendChild(pre); return;
      }
      var s = slides[i]; var idx = Reveal.getIndices(s); Reveal.slide(idx.h, idx.v);
      setTimeout(function(){
        var h = 0;
        for (var c of s.children) { if (c.tagName === 'ASIDE') continue;
          var r = c.getBoundingClientRect(); var top = s.getBoundingClientRect().top;
          var sc = Reveal.getScale ? Reveal.getScale() : 1;
          h = Math.max(h, (r.bottom - top) / sc); }
        out.push(i + '\t' + Math.round(h) + '\t' + (s.id || ''));
        i++; step();
      }, 120);
    }
    setTimeout(step, 1500);
  }
  go();
})();
</script>
"""

def measure(unit):
    src = f'{REPO}/docs/{unit}/lec.html'
    if not os.path.exists(src):
        return unit, None
    tmp = f'{REPO}/docs/{unit}/_measure.html'
    s = open(src).read().replace('</body>', JS + '</body>')
    open(tmp, 'w').write(s)
    prof = f'{SCR}/prof-{unit}'
    r = subprocess.run(['timeout', '180', 'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox',
                        f'--user-data-dir={prof}', '--window-size=1280,720', '--virtual-time-budget=60000',
                        '--dump-dom', f'file://{tmp}'], capture_output=True, text=True)
    os.remove(tmp)
    m = re.search(r'<pre id="ovf">(.*?)</pre>', r.stdout, re.S)
    if not m:
        return unit, None
    rows = [l.split('\t') for l in html.unescape(m.group(1)).splitlines()]
    return unit, [(int(a), int(b), c) for a, b, c in rows]

if __name__ == '__main__':
    units = sys.argv[1:]
    with cf.ThreadPoolExecutor(3) as ex:
        for unit, rows in ex.map(measure, units):
            if rows is None:
                print(f'{unit}\tFAILED'); continue
            over = [r for r in rows if r[1] > 720]
            print(f'{unit}\t{len(rows)} slides\t{len(over)} overflow')
            for i, h, sid in over:
                print(f'  {unit}\t{i}\t{h}\t{sid}')
