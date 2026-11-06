#!/usr/bin/env python3
"""Screenshot every animation frame of a lesson page (needs a server on :8765 serving the site root) and
stitch the frames of each animation into one sheet.   usage: shots.py PAGE_PATH_FROM_ROOT OUT_DIR [theme]"""
import sys, os, io
from playwright.sync_api import sync_playwright
from PIL import Image

page_path, out = sys.argv[1], sys.argv[2]
theme = sys.argv[3] if len(sys.argv) > 3 else 'light'
os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1200, 'height': 900}, color_scheme=theme)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/' + page_path, wait_until='load')
    pg.wait_for_timeout(600)
    anims = pg.query_selector_all('.anim')
    for ai, an in enumerate(anims):
        an.scroll_into_view_if_needed()
        n = int(an.get_attribute('data-frames'))
        pg.evaluate("el => { const b = el.querySelector('[data-a=play]'); if (b && b.textContent.includes('Pause')) b.click(); }", an)
        imgs = []
        for i in range(n):
            pg.evaluate("([el,i]) => el.querySelectorAll('.frame-dots button')[i].click()", [an, i])
            pg.wait_for_timeout(700)
            v = an.query_selector('.anim__views')
            imgs.append(Image.open(io.BytesIO(v.screenshot())))
        w, h = imgs[0].size
        cols = 2 if w < 700 else 1
        rows = (n + cols - 1) // cols
        sheet = Image.new('RGB', (w * cols, h * rows), 'white')
        for k, im in enumerate(imgs):
            sheet.paste(im, ((k % cols) * w, (k // cols) * h))
        sheet.save(os.path.join(out, f'anim{ai + 1}.png'))
        print('anim', ai + 1, n, 'frames', sheet.size)
    print('JS errors:', errs)
    b.close()
