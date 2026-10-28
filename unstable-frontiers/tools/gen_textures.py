"""Draws the item textures (original pixel art) into src/main/resources/assets/unstable_frontiers/textures/item.
Run from the project folder: python3 tools/gen_textures.py"""
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "src/main/resources/assets/unstable_frontiers/textures/item"

def draw(name, rows, palette):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                img.putpixel((x, y), palette[ch])
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png")

# A jagged violet crystal with a red rift glowing down its middle.
draw("rift_shard", [
    "................",
    ".........d......",
    "........dLd.....",
    ".......dLmd.....",
    ".......dLrmd....",
    "......dLmrmd....",
    "......dLrRmd....",
    ".....dLmrRmd....",
    ".....dLrRrmd....",
    "....dLmrRmd.....",
    "....dLmRrmd.....",
    "....dLrRmd......",
    ".....dLrmd......",
    "......dmd.......",
    ".......d........",
    "................",
], {"d": (40, 18, 58, 255), "L": (196, 150, 235, 255), "m": (124, 66, 170, 255), "r": (196, 40, 60, 255), "R": (255, 110, 90, 255)})

# A tiny iron cage with a gold idol inside.
draw("cage_trophy", [
    "................",
    "......kkkk......",
    ".....k....k.....",
    "....kkkkkkkk....",
    "....i.i..i.i....",
    "....i.iggi.i....",
    "....i.gGGg.i....",
    "....i.gGGg.i....",
    "....i.iggi.i....",
    "....i.igg..i....",
    "....i.i..i.i....",
    "....kkkkkkkk....",
    "...bbbbbbbbbb...",
    "...bBBBBBBBBb...",
    "...bbbbbbbbbb...",
    "................",
], {"k": (52, 52, 60, 255), "i": (170, 174, 182, 255), "g": (196, 140, 30, 255), "G": (255, 214, 80, 255),
    "b": (34, 28, 34, 255), "B": (78, 64, 74, 255)})

# A glaive: a hooked chitin blade on a long dark haft.
draw("swarmbreaker", [
    "..........ggg...",
    ".........gGGgg..",
    "........gGCCcg..",
    ".......gGCCccg..",
    "......gGCCccg...",
    ".....gGCcccg....",
    "......gcccgg....",
    ".....h.ggg......",
    "....h.h.........",
    "...h.h..........",
    "..hHh...........",
    ".hHh............",
    "hHh.............",
    "Hh..............",
    "h...............",
    "................",
], {"g": (30, 46, 30, 255), "G": (150, 220, 120, 255), "C": (92, 168, 80, 255), "c": (52, 110, 52, 255),
    "h": (46, 30, 22, 255), "H": (120, 84, 54, 255)})
print("wrote", sorted(p.name for p in OUT.glob("*.png")))
