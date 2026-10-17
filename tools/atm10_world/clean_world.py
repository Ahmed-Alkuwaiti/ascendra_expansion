"""Strip a modded Minecraft world down to vanilla so it opens cleanly elsewhere.

Built to move an Ascendra (Forge 1.20.1) world into All the Mods 10
(NeoForge 1.21.1). It writes a copy of the world in which:

  * every non-vanilla block becomes air, and its block entity is removed
  * non-vanilla biomes become the dimension's default vanilla biome
  * non-vanilla items, entities, enchantments and POIs are removed everywhere
    (chests, players, ender chests, item frames, mobs, ...)
  * modded dimensions are deleted; players standing in one are moved to spawn
  * level.dat loses its Forge mod list, modded datapacks and modded
    world-gen settings, so the world loads without "missing mods" errors

The world keeps its 1.20.1 data version: Minecraft 1.21.1 upgrades the vanilla
parts itself the first time the world is opened. The source world is never
modified.

Usage:
    python3 -I tools/atm10_world/clean_world.py <world folder or .zip> <output folder>
        [--keep NAMESPACE ...] [--reset-end] [--jobs N] [--zip]

--keep keeps a mod's content (e.g. --keep create) if that mod is also in ATM10.
"""
import argparse
import collections
import json
import multiprocessing
import os
import re
import shutil
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt  # noqa: E402
from nbt import Tag, BYTE, INT, DOUBLE, STRING, LIST, COMPOUND, LONG_ARRAY  # noqa: E402

VANILLA_FEATURES = {"vanilla", "bundle", "trade_rebalance", "update_1_21", "minecart_improvements",
                    "redstone_experiments", "winter_drop"}

DEFAULT_BIOME = {"overworld": "minecraft:plains", "nether": "minecraft:nether_wastes", "end": "minecraft:the_end"}

VANILLA_DIMS = {
    "minecraft:overworld": ("minecraft:overworld", "minecraft:overworld",
                            {"type": "minecraft:multi_noise", "preset": "minecraft:overworld"}),
    "minecraft:the_nether": ("minecraft:the_nether", "minecraft:nether",
                             {"type": "minecraft:multi_noise", "preset": "minecraft:nether"}),
    "minecraft:the_end": ("minecraft:the_end", "minecraft:end", {"type": "minecraft:the_end"}),
}

# Lists where every slot has a fixed meaning; a removed item leaves an empty slot.
FIXED_SLOT_LISTS = {"ArmorItems", "HandItems"}

# What a vanilla world folder holds. Anything else at the top level is mod data.
VANILLA_TOP = {"level.dat", "icon.png", "region", "entities", "poi", "DIM-1", "DIM1", "data",
               "playerdata", "advancements", "stats", "datapacks", "dimensions"}
VANILLA_DATA = re.compile(r"^(raids(_end|_nether)?|map_\d+|idcounts|scoreboard|random_sequences|chunks"
                          r"|command_storage_minecraft|villages.*)\.dat$")

NS_RE = re.compile(r"^([a-z0-9_.-]+):[a-z0-9_./-]+$")


class Cleaner:
    def __init__(self, keep, reset_end=False):
        self.keep = {"minecraft"} | set(keep)
        self.reset_end = reset_end
        self.removed = collections.Counter()

    def foreign(self, s):
        """Namespace of s if it is a resource id from a mod that is not kept, else None."""
        m = NS_RE.match(s) if isinstance(s, str) else None
        if m and m.group(1) not in self.keep:
            return m.group(1)
        return None

    def count(self, what, ident):
        self.removed[(what, ident.split(":")[0])] += 1

    # ---- generic tree scrub: items, entities, enchantments ... ----

    def scrub(self, tag):
        """Remove modded objects (compounds whose 'id' is a mod's) anywhere below tag."""
        if tag.t == COMPOUND:
            d = tag.v
            for k in list(d):
                c = d[k]
                if c.t == COMPOUND:
                    cid = c.v.get("id")
                    if cid is not None and cid.t == STRING and self.foreign(cid.v):
                        self.count("object", cid.v)
                        del d[k]
                        continue
                if c.t in (COMPOUND, LIST):
                    self.scrub(c)
        elif tag.t == LIST:
            et, items = tag.v
            if et == COMPOUND:
                keep = []
                fixed = getattr(tag, "_fixed", False)
                for it in items:
                    cid = it.v.get("id")
                    if cid is not None and cid.t == STRING and self.foreign(cid.v):
                        self.count("object", cid.v)
                        if fixed:
                            keep.append(Tag(COMPOUND, {}))
                        continue
                    keep.append(it)
                    self.scrub(it)
                tag.v = (et, keep)
            elif et == LIST:
                for it in items:
                    self.scrub(it)

    def scrub_root(self, tag):
        # Mark fixed-slot lists so removals leave empty slots instead of shifting.
        self._mark_fixed(tag)
        self.scrub(tag)

    def _mark_fixed(self, tag):
        if tag.t == COMPOUND:
            for k, c in tag.v.items():
                if c.t == LIST and k in FIXED_SLOT_LISTS:
                    c.__class__ = FixedList
                self._mark_fixed(c)
        elif tag.t == LIST and tag.v[0] in (COMPOUND, LIST):
            for it in tag.v[1]:
                self._mark_fixed(it)

    # ---- chunks ----

    def clean_chunk(self, root, dim):
        d = root.v
        changed = False
        sections = d.get("sections")
        if sections is not None:
            for sec in sections.v[1]:
                bs = sec.v.get("block_states")
                if bs is not None and self._clean_palette(bs, True, None):
                    changed = True
                bi = sec.v.get("biomes")
                if bi is not None and self._clean_palette(bi, False, DEFAULT_BIOME[dim]):
                    changed = True

        for key in ("block_ticks", "fluid_ticks"):
            ticks = d.get(key)
            if ticks is not None and ticks.v[1]:
                kept = []
                for t in ticks.v[1]:
                    i = t.v.get("i")
                    if i is not None and self.foreign(i.v):
                        changed = True
                        continue
                    kept.append(t)
                ticks.v = (ticks.v[0], kept)

        st = d.get("structures")
        if st is not None:
            for sub in ("starts", "References"):
                s = st.v.get(sub)
                if s is not None:
                    for k in list(s.v):
                        if self.foreign(k):
                            self.count("structure", k)
                            del s.v[k]
                            changed = True

        before = sum(self.removed.values())
        for key in ("block_entities", "entities", "Entities"):
            if key in d:
                self.scrub_root(d[key])
        if sum(self.removed.values()) != before:
            changed = True
        return changed

    def _clean_palette(self, container, blocks, default_biome):
        pal = container.v.get("palette")
        if pal is None or not pal.v[1]:
            return False
        entries = pal.v[1]
        names = [(e.v["Name"].v if blocks else e.v) for e in entries]
        bad = [i for i, n in enumerate(names) if self.foreign(n)]
        if not bad:
            return False
        for i in bad:
            self.count("block" if blocks else "biome", names[i])
            if blocks:
                entries[i] = Tag(COMPOUND, {"Name": Tag(STRING, "minecraft:air")})
            else:
                entries[i] = Tag(STRING, default_biome)

        # Merge duplicate palette entries and repack the index data.
        def key(e):
            return nbt.dumps(e) if blocks else e.v
        new_entries, remap, seen = [], [], {}
        for e in entries:
            k = key(e)
            if k not in seen:
                seen[k] = len(new_entries)
                new_entries.append(e)
            remap.append(seen[k])
        old_n, new_n = len(entries), len(new_entries)
        data = container.v.get("data")
        if old_n > 1 and data is not None:
            idx = unpack(data.v, bits_for(old_n, blocks), 4096 if blocks else 64)
            idx = [remap[i] if i < old_n else 0 for i in idx]
        else:
            idx = None
        pal.v = (pal.v[0], new_entries)
        if new_n == 1:
            container.v.pop("data", None)
        elif idx is not None:
            container.v["data"] = Tag(LONG_ARRAY, pack(idx, bits_for(new_n, blocks)))
        return True

    # ---- POI ----

    def clean_poi(self, root):
        changed = False
        secs = root.v.get("Sections")
        if secs is None:
            return False
        for sec in secs.v.values():
            rec = sec.v.get("Records")
            if rec is None:
                continue
            kept = []
            for r in rec.v[1]:
                t = r.v.get("type")
                if t is not None and self.foreign(t.v):
                    self.count("poi", t.v)
                    changed = True
                    continue
                kept.append(r)
            rec.v = (rec.v[0], kept)
        return changed

    # ---- players ----

    def clean_player(self, p, spawn):
        self.scrub_root(Tag(COMPOUND, {"_": p}))
        d = p.v
        dim = d.get("Dimension")
        if dim is not None and (self.foreign(dim.v) or (self.reset_end and dim.v == "minecraft:the_end")):
            self.count("player moved out of", dim.v)
            d["Dimension"] = Tag(STRING, "minecraft:overworld")
            x, y, z = spawn
            d["Pos"] = Tag(LIST, (DOUBLE, [Tag(DOUBLE, x + 0.5), Tag(DOUBLE, float(y)), Tag(DOUBLE, z + 0.5)]))
            d.pop("RootVehicle", None)
        sd = d.get("SpawnDimension")
        if sd is not None and (self.foreign(sd.v) or (self.reset_end and sd.v == "minecraft:the_end")):
            for k in ("SpawnDimension", "SpawnX", "SpawnY", "SpawnZ", "SpawnForced", "SpawnAngle"):
                d.pop(k, None)
        for k in ("recipeBook",):
            rb = d.get(k)
            if rb is not None:
                for lk in ("recipes", "toBeDisplayed"):
                    lst = rb.v.get(lk)
                    if lst is not None and lst.v[0] == STRING:
                        lst.v = (STRING, [s for s in lst.v[1] if not self.foreign(s.v)])

    # ---- level.dat ----

    def clean_level(self, root):
        for k in list(root.v):
            if k != "Data":
                del root.v[k]  # "fml", "forge": Forge's record of the mod list
        d = root.v["Data"].v
        notes = []
        wgs = d.get("WorldGenSettings")
        if wgs is not None:
            dims = wgs.v["dimensions"].v
            for name in list(dims):
                if self.foreign(name):
                    del dims[name]
                    notes.append(f"removed dimension {name}")
                elif name in VANILLA_DIMS and has_foreign(dims[name], self):
                    dims[name] = vanilla_dimension(name)
                    notes.append(f"reset {name} world generation to vanilla (it used a mod's generator)")
        dp = d.get("DataPacks")
        if dp is not None:
            for key in ("Enabled", "Disabled"):
                lst = dp.v.get(key)
                if lst is None:
                    continue
                kept = []
                for s in lst.v[1]:
                    if s.v in VANILLA_FEATURES or s.v.startswith("file/"):
                        kept.append(s)
                    elif s.v.startswith("mod:") and s.v[4:] in self.keep:
                        kept.append(s)
                    else:
                        if key == "Enabled":
                            notes.append(f"disabled datapack {s.v}")
                lst.v = (STRING, kept)
        ef = d.get("enabled_features")
        if ef is not None:
            ef.v = (STRING, [s for s in ef.v[1] if not self.foreign(s.v)])
        if self.reset_end and d.pop("DragonFight", None) is not None:
            notes.append("reset the End: the dragon will be back")
        spawn = (d["SpawnX"].v, d["SpawnY"].v, d["SpawnZ"].v)
        if "Player" in d:
            self.clean_player(d["Player"], spawn)
        return spawn, notes


class FixedList(Tag):
    __slots__ = ()
    _fixed = True


def has_foreign(tag, cleaner):
    if tag.t == STRING:
        return cleaner.foreign(tag.v) is not None
    if tag.t == COMPOUND:
        return any(has_foreign(c, cleaner) for c in tag.v.values())
    if tag.t == LIST:
        return any(has_foreign(c, cleaner) for c in tag.v[1])
    return False


def vanilla_dimension(name):
    dtype, settings, source = VANILLA_DIMS[name]
    src = Tag(COMPOUND, {k: Tag(STRING, v) for k, v in source.items()})
    gen = Tag(COMPOUND, {"type": Tag(STRING, "minecraft:noise"), "settings": Tag(STRING, settings),
                         "biome_source": src})
    return Tag(COMPOUND, {"type": Tag(STRING, dtype), "generator": gen})


def bits_for(n, blocks):
    b = max(1, (n - 1).bit_length())
    return max(4, b) if blocks else b


def unpack(longs, bits, size):
    per = 64 // bits
    mask = (1 << bits) - 1
    out = []
    for v in longs:
        v &= 0xFFFFFFFFFFFFFFFF
        for j in range(per):
            out.append((v >> (j * bits)) & mask)
            if len(out) == size:
                return out
    return out + [0] * (size - len(out))


def pack(values, bits):
    per = 64 // bits
    out = []
    for start in range(0, len(values), per):
        v = 0
        for j, x in enumerate(values[start:start + per]):
            v |= x << (j * bits)
        if v >= 1 << 63:
            v -= 1 << 64
        out.append(v)
    return out


# ---- per-file workers ----

def dim_of(rel):
    if rel.startswith("DIM-1"):
        return "nether"
    if rel.startswith("DIM1"):
        return "end"
    return "overworld"


def process_region(args):
    src, dst, rel, keep = args
    c = Cleaner(keep)
    kind = os.path.basename(os.path.dirname(rel))  # region / entities / poi
    dim = dim_of(rel)
    out, bad = {}, 0
    for i, (ts, comp, payload) in nbt.read_region(src).items():
        try:
            root = nbt.decode_chunk(comp, payload)
        except Exception:
            bad += 1
            continue
        if kind == "poi":
            c.clean_poi(root)
        else:
            c.clean_chunk(root, dim)
        out[i] = (ts, root)
    if out:
        nbt.write_region(dst, out)
    return c.removed, bad, rel


def process_player(args):
    src, dst, keep, spawn, reset_end = args
    c = Cleaner(keep, reset_end)
    (name, root), gz = nbt.read_file(src)
    c.clean_player(root, spawn)
    nbt.write_file(dst, root, name, gz)
    return c.removed


def clean_json(path, dst, cleaner):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    def walk(o):
        if isinstance(o, dict):
            return {k: walk(v) for k, v in o.items() if not cleaner.foreign(k)}
        return o
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(walk(data), fh)


def find_world(path):
    for dirpath, dirnames, filenames in os.walk(path):
        if "level.dat" in filenames:
            return dirpath
    sys.exit(f"no level.dat found under {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("world", help="world folder, or a .zip of it")
    ap.add_argument("output", help="folder to write the cleaned world into (must not exist)")
    ap.add_argument("--keep", nargs="*", default=[], help="mod namespaces to keep (mods also in ATM10)")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--reset-end", action="store_true",
                    help="leave the End out so it regenerates with a new Ender Dragon")
    ap.add_argument("--zip", action="store_true", help="also write <output>.zip")
    a = ap.parse_args()

    tmp = None
    src = a.world
    if zipfile.is_zipfile(src):
        tmp = tempfile.mkdtemp(prefix="world_src_")
        with zipfile.ZipFile(src) as z:
            z.extractall(tmp)
        src = tmp
    src = find_world(src)
    out = a.output
    if os.path.exists(out):
        sys.exit(f"{out} already exists; pick a new output folder")
    os.makedirs(out)

    cleaner = Cleaner(a.keep, a.reset_end)
    totals = collections.Counter()

    (lname, level), lgz = nbt.read_file(os.path.join(src, "level.dat"))
    spawn, notes = cleaner.clean_level(level)
    nbt.write_file(os.path.join(out, "level.dat"), level, lname, lgz)
    totals.update(cleaner.removed)

    dropped = []
    region_jobs, player_jobs = [], []
    for dirpath, dirnames, filenames in os.walk(src):
        rel_dir = os.path.relpath(dirpath, src)
        parts = [] if rel_dir == "." else rel_dir.split(os.sep)
        if parts:
            top = parts[0]
            if a.reset_end and top == "DIM1":
                dirnames[:] = []
                continue
            if top not in VANILLA_TOP or (top == "dimensions" and len(parts) > 1 and parts[1] not in cleaner.keep):
                if (top == "dimensions" and len(parts) == 2) or len(parts) == 1:
                    dropped.append(rel_dir)
                dirnames[:] = []
                continue
        os.makedirs(os.path.join(out, rel_dir), exist_ok=True)
        for fn in filenames:
            rel = os.path.normpath(os.path.join(rel_dir, fn))
            s, dpath = os.path.join(dirpath, fn), os.path.join(out, rel)
            if not parts:
                if fn in ("level.dat",) or fn not in VANILLA_TOP:
                    if fn not in ("level.dat", "level.dat_old", "session.lock"):
                        dropped.append(rel)
                    continue
                shutil.copy2(s, dpath)
            elif fn.endswith(".mca") and parts[-1] in ("region", "entities", "poi"):
                region_jobs.append((s, dpath, rel, a.keep))
            elif parts[0] == "playerdata" and fn.endswith(".dat"):
                player_jobs.append((s, dpath, a.keep, spawn, a.reset_end))
            elif parts[0] in ("advancements", "stats") and fn.endswith(".json"):
                clean_json(s, dpath, cleaner)
            elif parts[0] == "data" and len(parts) == 1:
                if VANILLA_DATA.match(fn):
                    shutil.copy2(s, dpath)
                else:
                    dropped.append(rel)
            elif fn.endswith((".dat_old", ".mcc")):
                continue
            else:
                shutil.copy2(s, dpath)

    print(f"Cleaning {len(region_jobs)} region files with {a.jobs} workers ...", flush=True)
    bad_total = 0
    with multiprocessing.Pool(a.jobs) as pool:
        for n, (removed, bad, rel) in enumerate(pool.imap_unordered(process_region, region_jobs), 1):
            totals.update(removed)
            bad_total += bad
            if n % 50 == 0 or n == len(region_jobs):
                print(f"  {n}/{len(region_jobs)}", flush=True)
        for removed in pool.imap_unordered(process_player, player_jobs):
            totals.update(removed)

    print("\nDone. Cleaned world:", os.path.abspath(out))
    for n in notes:
        print("  level.dat:", n)
    if dropped:
        print("  left out mod data:", ", ".join(sorted(dropped)))
    if bad_total:
        print(f"  {bad_total} chunk(s) were corrupt and were left out (they will regenerate)")
    if totals:
        print("\nRemoved, by mod:")
        by_mod = collections.defaultdict(list)
        for (what, ns), n in totals.items():
            by_mod[ns].append(f"{n} {what}{'s' if n != 1 and not what.startswith('player') else ''}")
        for ns in sorted(by_mod):
            print(f"  {ns}: {', '.join(sorted(by_mod[ns]))}")
    else:
        print("\nNothing modded was found.")

    if a.zip:
        base = shutil.make_archive(out.rstrip("/\\"), "zip", os.path.dirname(os.path.abspath(out)),
                                   os.path.basename(os.path.abspath(out)))
        print("\nZipped:", base)
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
