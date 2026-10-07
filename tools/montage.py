"""Contact sheet of structure templates."""
import sys

from PIL import Image, ImageDraw, ImageFont

import render_structure as rs

S = '../src/main/resources/data/aurelia/structures/'


def montage(names, out, cols=4, tile=420, opts=None):
    opts = opts or {}
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tile, rows * (tile + 30)), (14, 14, 20))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    for i, n in enumerate(names):
        im = rs.render(S + n + '.nbt', '/tmp/claude-0/-home-user-ascendra-expansion/48cc1d0c-d4a1-5abb-961a-262088dcdc87/scratchpad/r/_tile.png', size=tile, **opts.get(n, {}))
        im.thumbnail((tile, tile))
        x, y = (i % cols) * tile, (i // cols) * (tile + 30)
        sheet.paste(im, (x + (tile - im.width) // 2, y + 30))
        d.text((x + 8, y + 5), n, fill=(230, 230, 240), font=f)
    sheet.save(out)
    print('wrote', out)


if __name__ == '__main__':
    montage(sys.argv[2:], sys.argv[1])
