"""CI helper: put fake mod content into a freshly generated vanilla world, so the
cleaner has something to remove before the world is opened in 1.21.1."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from nbt import Tag, BYTE, STRING, LIST, COMPOUND, INT  # noqa: E402

world = sys.argv[1]
reg = os.path.join(world, "region")
done = 0
for fn in sorted(os.listdir(reg)):
    path = os.path.join(reg, fn)
    chunks = {}
    for i, (ts, comp, payload) in nbt.read_region(path).items():
        root = nbt.decode_chunk(comp, payload)
        for sec in root.v["sections"].v[1]:
            pal = sec.v.get("block_states").v["palette"].v[1]
            for e in pal:
                if e.v["Name"].v in ("minecraft:stone", "minecraft:dirt"):
                    e.v["Name"] = Tag(STRING, "aurelia:sunwell")
                    e.v.pop("Properties", None)
            bpal = sec.v["biomes"].v["palette"].v[1]
            bpal[0] = Tag(STRING, "aurelia:gaudy_grove")
        x, z = root.v["xPos"].v * 16, root.v["zPos"].v * 16
        item = lambda i: Tag(COMPOUND, {"id": Tag(STRING, i), "Count": Tag(BYTE, 1), "Slot": Tag(BYTE, 0)})
        root.v["block_entities"].v[1].append(Tag(COMPOUND, {"id": Tag(STRING, "aurelia:altar"),
                                              "x": Tag(INT, x), "y": Tag(INT, 0), "z": Tag(INT, z),
                                              "Items": Tag(LIST, (COMPOUND, [item("aurelia:relic")]))}))
        root.v.setdefault("structures", Tag(COMPOUND, {})).v.setdefault("starts", Tag(COMPOUND, {})).v[
            "aurelia:rootbound_citadel"] = Tag(COMPOUND, {"id": Tag(STRING, "INVALID")})
        chunks[i] = (ts, root)
        done += 1
    nbt.write_region(path, chunks)

(name, lvl), gz = nbt.read_file(os.path.join(world, "level.dat"))
d = lvl.v["Data"].v
d["DataPacks"].v["Enabled"].v[1].append(Tag(STRING, "mod:aurelia"))
d["WorldGenSettings"].v["dimensions"].v["aurelia:grove"] = Tag(COMPOUND, {"type": Tag(STRING, "aurelia:grove")})
lvl.v["fml"] = Tag(COMPOUND, {"LoadingModList": Tag(LIST, (COMPOUND, []))})
nbt.write_file(os.path.join(world, "level.dat"), lvl, name, gz)
print(f"injected mod content into {done} chunks")
