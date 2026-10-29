"""Draws the creature gear's textures (original pixel art): item icons into textures/item and the Gnashback Carapace
armour layers into textures/models/armor. Colours come from the creatures' own palettes (tools/models/*.py), so the
gear looks cut from the animals. Run from the project folder: python3 tools/gen_creature_textures.py [--sheet out.png]"""
import random
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "src/main/resources/assets/unstable_frontiers/textures"

# Gnashback shell, Shrikewing ash and membrane, Matriarch teal and sac green
SHELL = {"d": (40, 24, 20, 255), "s": (98, 58, 38, 255), "m": (134, 86, 56, 255), "l": (184, 132, 90, 255),
         "b": (214, 200, 168, 255), "o": (24, 14, 12, 255), "r": (170, 92, 46, 255)}


def draw(name, rows, palette, folder="item"):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        assert len(row) == 16 and len(rows) == 16, (name, y, len(row))
        for x, ch in enumerate(row):
            if ch != ".":
                img.putpixel((x, y), palette[ch])
    out = ROOT / folder
    out.mkdir(parents=True, exist_ok=True)
    img.save(out / f"{name}.png")
    return img


ICONS = {}

# A curved plate of beetle shell: dark rim, lit ridge, a bone rib set into it.
ICONS["gnashback_plate"] = draw("gnashback_plate", [
    "................",
    "................",
    "....oooooo......",
    "...osmmllmoo....",
    "..osmmlllmmso...",
    "..osmbbbbbmmso..",
    ".osmmlllllmmsso.",
    ".osmmmlllmmmsso.",
    ".ossmbbbbbbmsso.",
    ".ossmmmmmmmssso.",
    "..ossrssssssso..",
    "..odssssrsssdo..",
    "...oddssssddo...",
    "....oodddddo....",
    "......oooo......",
    "................",
], SHELL)

# A hooked raptor talon: ash-pale base, a dark curved claw.
ICONS["shrike_talon"] = draw("shrike_talon", [
    "................",
    "........ooo.....",
    ".......okkko....",
    "......okkdko....",
    "......okdo.o....",
    ".....okkdo......",
    ".....okddo......",
    "....okkddo......",
    "....okdddo......",
    "...oaaaaaao.....",
    "..oaAAAAaaao....",
    "..oaAppAAaao....",
    "..oaaAAaaapo....",
    "...oaaaaaao.....",
    "....oooooo......",
    "................",
], {"o": (22, 20, 26, 255), "k": (96, 90, 108, 255), "d": (58, 54, 66, 255), "a": (150, 142, 130, 255),
    "A": (210, 204, 190, 255), "p": (118, 74, 128, 255)})

ICONS["carapace_helmet"] = draw("carapace_helmet", [
    "................",
    "................",
    "....oooooooo....",
    "...olllmmmmso...",
    "..olmbbbbbbmso..",
    "..olmmmmmmmmso..",
    "..osdssssssdso..",
    "..osooooooooso..",
    "..oso......oso..",
    "..oso......oso..",
    "..odo......odo..",
    "...o........o...",
    "................",
    "................",
    "................",
    "................",
], SHELL)

ICONS["carapace_chestplate"] = draw("carapace_chestplate", [
    "................",
    "..ooo......ooo..",
    ".olmso....olmso.",
    ".olmsoooooolmso.",
    ".osmmllllllmmso.",
    "..osmbbbbbbmso..",
    "..osmmlllmmmso..",
    "..osmbbbbbbmso..",
    "..ossmmmmmmsso..",
    "..osmbbbbbbmso..",
    "..ossmmmmmmsso..",
    "..odssssssssdo..",
    "..odddrdddrddo..",
    "..oooooooooooo..",
    "................",
    "................",
], SHELL)

ICONS["carapace_leggings"] = draw("carapace_leggings", [
    "................",
    "...oooooooooo...",
    "...ommllllmmo...",
    "...osbbbbbbso...",
    "...osmmoommso...",
    "...osmo..omso...",
    "...olmo..omlo...",
    "...olmo..omlo...",
    "...osbo..obso...",
    "...osmo..omso...",
    "...osmo..omso...",
    "...odso..osdo...",
    "...oooo..oooo...",
    "................",
    "................",
    "................",
], SHELL)

ICONS["carapace_boots"] = draw("carapace_boots", [
    "................",
    "................",
    "................",
    "................",
    "................",
    "..oooo....oooo..",
    "..olmo....omlo..",
    "..obbo....obbo..",
    "..osmo....omso..",
    ".oolmo....omloo.",
    "olmmso....osmmlo",
    "osssdo....odssso",
    "oooooo....oooooo",
    "................",
    "................",
    "................",
], SHELL)

# A long talon-headed spear: three hooked talons lashed to a dark netherite haft.
ICONS["shrike_impaler"] = draw("shrike_impaler", [
    "...........ooo..",
    "..........okAko.",
    ".........okAkAo.",
    "........okAAko..",
    ".......okAkko.o.",
    "......okkkkookko",
    ".....onnkoo.oko.",
    "....onNno....o..",
    "...onNno........",
    "..onNno.........",
    ".onNno..........",
    "onNno...........",
    "oNno............",
    "ono.............",
    "o...............",
    "................",
], {"o": (20, 18, 24, 255), "k": (96, 90, 108, 255), "A": (214, 208, 194, 255), "n": (58, 50, 54, 255),
    "N": (98, 84, 86, 255)})

# A folded wing of teal membrane, ribbed in bone, clasped by a glowing sac-green brooch.
ICONS["matriarch_mantle"] = draw("matriarch_mantle", [
    "................",
    ".....oooooo.....",
    "....obbbbbbo....",
    "...obmmgGmmbo...",
    "...obmgGGgmbo...",
    "..obmmmggmmmbo..",
    "..obmbmmmmbmbo..",
    ".obmmbmmmmbmmbo.",
    ".obmmbmmmmbmmbo.",
    ".obmbmmmmmmbmbo.",
    "obmmbmmmmmmbmmbo",
    "obmbmmmmmmmmbmbo",
    "obbmmdmmmmdmmbbo",
    "odmdmmdmmdmmdmdo",
    ".oodoodoodoodoo.",
    "................",
], {"o": (14, 22, 24, 255), "b": (222, 214, 190, 255), "m": (70, 96, 84, 255), "d": (34, 50, 44, 255),
    "g": (110, 200, 70, 255), "G": (196, 255, 120, 255)})

# A drop of glowing acid (only seen in flight).
ICONS["acid_glob"] = draw("acid_glob", [
    "................",
    "................",
    "................",
    ".......oo.......",
    "......oggo......",
    ".....oggGgo.....",
    "....ogggGGgo....",
    "....oggggGgo....",
    "...ogggggggdo...",
    "...ogggggggdo...",
    "...odggggggdo...",
    "....oddgggddo...",
    ".....odddddo....",
    "......ooooo.....",
    "................",
    "................",
], {"o": (24, 46, 20, 255), "g": (110, 200, 70, 255), "G": (220, 255, 160, 255), "d": (60, 120, 46, 255)})


# --------------------------------------------------------------------------------------------------- armour layers
def shell_pixel(x, y, rng, seam_every=4):
    """Banded beetle shell: plates with a lit top edge and a dark seam below, a few rivets and rust spots."""
    band = y % seam_every
    base = [(98, 58, 38), (120, 74, 48), (110, 66, 42), (54, 32, 24)][band]
    if band == 0:
        base = (166, 116, 78)
    jitter = rng.randint(-8, 8)
    c = tuple(max(0, min(255, v + jitter)) for v in base)
    if rng.random() < 0.03:
        c = (170, 92, 46)
    return c + (255,)


def fill(img, box, rng, rows=None, rib=False):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        if rows is not None and not (rows[0] <= y < rows[1]):
            continue
        for x in range(x0, x1):
            c = shell_pixel(x, y, rng)
            if rib and (x - x0) % 6 == 2 and (y % 4) != 3:
                c = (214, 200, 168, 255)   # bone ribs grown through the shell
            img.putpixel((x, y), c)


def armour():
    rng = random.Random(61)
    out = ROOT / "models" / "armor"
    out.mkdir(parents=True, exist_ok=True)
    one = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    fill(one, (0, 0, 32, 16), rng)                       # helmet: the head box
    for x in range(8, 16):                               # the visor slit across the face
        one.putpixel((x, 12), (20, 12, 10, 255))
        one.putpixel((x, 11), (24, 14, 12, 255))
    fill(one, (16, 16, 40, 32), rng, rib=True)           # chestplate body
    fill(one, (40, 16, 56, 32), rng)                     # chestplate arms
    fill(one, (0, 16, 16, 20), rng)                      # boots: leg box top/bottom faces
    fill(one, (0, 20, 16, 32), rng, rows=(26, 32))       # boots: the lower legs only
    one.save(out / "carapace_layer_1.png")

    two = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    fill(two, (16, 16, 40, 20), rng)                     # leggings: waist top/bottom
    fill(two, (16, 20, 40, 32), rng, rows=(27, 32))      # leggings: the waist band
    fill(two, (0, 16, 16, 32), rng)                      # leggings: legs
    two.save(out / "carapace_layer_2.png")
    return one, two


def sheet(path, layers):
    icons = list(ICONS.items())
    w = 16 * 8 * len(icons)
    s = Image.new("RGBA", (max(w, 64 * 8), 16 * 8 + 32 * 8 + 8), (36, 36, 44, 255))
    for i, (_, img) in enumerate(icons):
        s.alpha_composite(img.resize((128, 128), Image.NEAREST), (i * 128, 0))
    for i, img in enumerate(layers):
        s.alpha_composite(img.resize((256, 128), Image.NEAREST), (i * 264, 136))
    s.save(path)


if __name__ == "__main__":
    layers = armour()
    if "--sheet" in sys.argv:
        sheet(sys.argv[sys.argv.index("--sheet") + 1], layers)
    print("creature textures written")
