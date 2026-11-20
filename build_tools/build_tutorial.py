"""Build the self-contained Framosik guide from its template and real screenshots."""
import argparse
import base64
from html import escape
import json
from pathlib import Path
import re
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_info import ICONS, VERSION
from i18n import CATALOGS, LANGUAGES

DOCS = ROOT / "docs"
SHOTS = ("workspace", "blending", "result", "appearance")
LITERALS = {"exe", "bin", "internal", "demoFile", "ctrlO", "ctrlS"}
TOKEN = re.compile(r"\{([a-zA-Z_]+)\}")


def data_uri(data, mime):
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def script_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def load_guide():
    directory = DOCS / "tutorial" / "languages"
    if {p.stem for p in directory.glob("*.json")} != set(LANGUAGES):
        raise ValueError("Tutorial languages must match the desktop app.")
    guides = {lang: json.loads((directory / f"{lang}.json").read_text(encoding="utf-8"))
              for lang in LANGUAGES}
    base = guides["en"]
    controls = json.loads((directory.parent / "controls.json").read_text(encoding="utf-8"))
    group_ids = {group["id"] for group in controls}
    items = [item for group in controls for item in group["items"]]
    entry_ids = {item["labels"][0] for item in items}
    keys = {"website", "repository", "donate", "play", "pause"}
    keys.update(label for item in items for label in item["labels"])
    keys.update(TOKEN.findall(json.dumps(controls)))
    reference_tokens = set(TOKEN.findall(json.dumps(base)))
    for lang, guide in guides.items():
        reference = guide["reference"]
        if (set(reference["groups"]) != group_ids or set(reference["entries"]) != entry_ids
                or set(reference["ui"]) != set(base["reference"]["ui"])
                or len(reference["workshops"]) != len(base["reference"]["workshops"])
                or not all(text.strip() for text in reference["entries"].values())
                or not all(all(exercise.get(k) for k in ("title", "try", "expect"))
                           for exercise in reference["workshops"])):
            raise ValueError(f"Incomplete parameter reference in {lang}")
        if (set(guide["ui"]) != set(base["ui"]) or len(guide["sections"]) != 6
                or len(guide["captions"]) != len(SHOTS) or len(guide["faq"]) != 3):
            raise ValueError(f"Incomplete tutorial in {lang}")
        for i, (chapter, reference) in enumerate(zip(guide["sections"], base["sections"])):
            if not chapter["title"] or len(chapter["p"]) != len(reference["p"]):
                raise ValueError(f"Incomplete chapter {i + 1} in {lang}")
        tokens = set(TOKEN.findall(json.dumps(guide)))
        if tokens != reference_tokens:
            raise ValueError(f"Control references differ in {lang}: {tokens ^ reference_tokens}")
        keys.update(tokens - LITERALS)
    app = {lang: {k: CATALOGS[lang][k] for k in sorted(keys)} for lang in LANGUAGES}
    return {"names": LANGUAGES, "app": app, "guides": guides, "controls": controls}


def build(output):
    images = {}
    for key in SHOTS:
        path = DOCS / "images" / f"{key}.webp"
        with Image.open(path) as im:
            if im.format != "WEBP" or im.size != (1250, 840):
                raise ValueError(f"Unexpected screenshot: {path}")
        images[key] = data_uri(path.read_bytes(), "image/webp")
    robot = DOCS / "images" / "demo.webp"
    with Image.open(robot) as im:
        if im.size != (480, 1080):
            raise ValueError("The frame explorer expects the bundled 480 × 1080 demo.")
    images["robot"] = data_uri(robot.read_bytes(), "image/webp")
    values = {"version": escape(VERSION), "icon": data_uri((ICONS / "framosik_64.png").read_bytes(), "image/png"),
              "locales": script_json(load_guide()), "images": script_json(images)}
    template = (DOCS / "tutorial" / "page.html").read_text(encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    page = re.sub(r"@@([a-z]+)@@", lambda m: values[m[1]], template)
    output.write_bytes(page.encode("utf-8"))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "Framosik-Tutorial.html")
    print(build(parser.parse_args().output))
