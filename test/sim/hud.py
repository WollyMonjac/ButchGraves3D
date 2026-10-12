"""Add the game's HUD (same layout as G.drawHud at 240x320) under a rendered 240x278 frame."""
import sys
from PIL import Image, ImageDraw, ImageFont
RES = '/home/claude/bg/res/'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 10)


def outline(d, xy, s, col, anchor='mt'):
    x, y = xy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        d.text((x + dx, y + dy), s, font=FONT, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), s, font=FONT, fill=col, anchor=anchor)


def compose(view, out, health=100, ammo_kind=1, ammo=24, face='face0', boss=None, bossfrac=0.62):
    W, H, hudH = 240, 320, 42
    im = Image.new('RGB', (W, H))
    im.paste(Image.open(view).convert('RGB'), (0, 0))
    d = ImageDraw.Draw(im)
    y0 = H - hudH
    for i in range(hudH):
        t = i * 255 // hudH
        d.line((0, y0 + i, W, y0 + i), fill=(40 - t * 28 // 255, 28 - t * 20 // 255, 24 - t * 18 // 255))
    d.line((0, y0, W, y0), fill=(0xff, 0x70, 0x10)); d.line((0, y0 + 1, W, y0 + 1), fill=(0x60, 0x1c, 0x04))
    for x in range(6, W, W // 6):
        d.rectangle((x, y0 + hudH - 4, x + 1, y0 + hudH - 3), fill=(0x80, 0x60, 0x50))
    fs = 36
    fimg = Image.open(RES + '%s_36.png' % face).convert('RGBA')
    fx, fy = W // 2 - fs // 2, y0 + (hudH - fs) // 2 + 1
    d.rectangle((fx - 2, fy - 1, fx + fs + 1, fy + fs), fill=(0x14, 0x08, 0x06), outline=(0x80, 0x40, 0x10))
    im.paste(fimg, (fx, fy), fimg)
    dig = Image.open(RES + 'dig16.png').convert('RGBA')
    cw, ch = dig.width // 12, dig.height
    icons = Image.open(RES + 'icons.png').convert('RGBA')

    def digits(v, x, y):
        for k, c in enumerate(str(v)):
            g = dig.crop((int(c) * cw, 0, int(c) * cw + cw, ch))
            im.paste(g, (x + k * (cw * 3 // 4), y), g)

    def icon(i, x, y):
        g = icons.crop((i * 16, 0, i * 16 + 16, 16))
        im.paste(g, (x, y), g)
    dy = y0 + (hudH - ch) // 2 + 1
    iy = y0 + (hudH - 16) // 2 + 1
    icon(0, 3, iy); digits(health, 21, dy)
    rx = fx + fs + 6
    icon(2 + ammo_kind, rx, iy); digits(ammo, rx + 18, dy)
    cx, cy = W // 2, (H - hudH) // 2
    for (a, b) in (((cx - 4, cy), (cx - 2, cy)), ((cx + 2, cy), (cx + 4, cy)), ((cx, cy - 4), (cx, cy - 2)), ((cx, cy + 2), (cx, cy + 4))):
        d.line((a, b), fill=(0xff, 0xd0, 0x40))
    if boss:
        bw, bx, by = W - 16, 8, 3
        d.rectangle((bx - 1, by - 1, bx + bw, by + 5), fill=(0, 0, 0))
        d.rectangle((bx, by, bx + bw - 1, by + 4), fill=(0x40, 0x10, 0x10), outline=(0xff, 0x80, 0x40))
        d.rectangle((bx + 1, by + 1, bx + int((bw - 2) * bossfrac), by + 3), fill=(0xd0, 0x20, 0x10))
        outline(d, (W // 2, by + 8), boss, (0xff, 0xb0, 0x80))
    im.save(out)


if __name__ == '__main__':
    # hud.py view.png out.png health ammo_kind(0 bullets, 1 shells, 2 pumpkins) ammo face [BOSS NAME]
    a = sys.argv[1:]
    compose(a[0], a[1], int(a[2]), int(a[3]), int(a[4]), a[5], a[6] if len(a) > 6 else None)
