from pathlib import Path
from html import escape
from PIL import Image, ImageOps
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "originals" / "appetite"
OUTPUT_DIR = ROOT / "optimized" / "appetite"
REVIEW_PAGE = ROOT / "appetite-review.html"
MAX_EDGE = 2400  # Full regeneration after the latest Appetite originals upload

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

def main():
    if not SOURCE_DIR.is_dir():
        print(f"Missing source folder: {SOURCE_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    images = sorted(
        p for p in SOURCE_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    )
    if not images:
        print("No supported images found.")
        sys.exit(1)

    cards = []
    total_before = total_after = 0
    for source in images:
        target = OUTPUT_DIR / (source.stem + ".webp")
        try:
            with Image.open(source) as original:
                before = source.stat().st_size
                image = ImageOps.exif_transpose(original)
                has_alpha = "A" in image.getbands() or "transparency" in image.info
                is_png = source.suffix.lower() == ".png"
                image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
                if has_alpha:
                    image = image.convert("RGBA")
                elif image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGB")
                args = {"format": "WEBP", "method": 6, "lossless": is_png}
                if not is_png:
                    args["quality"] = 86
                image.save(target, **args)
            after = target.stat().st_size
            total_before += before
            total_after += after
            print(f"{source.name} -> optimized/appetite/{target.name}: {before:,} -> {after:,} bytes")
            cards.append((source.name, target.name, before, after))
        except Exception as exc:
            print(f"Could not process {source.name}: {exc}")
            sys.exit(1)

    card_html = []
    for original_name, output_name, before, after in cards:
        card_html.append(
            '<figure class="card">'
            f'<a href="optimized/appetite/{escape(output_name, quote=True)}" target="_blank" rel="noopener">'
            f'<img loading="lazy" src="optimized/appetite/{escape(output_name, quote=True)}" alt="{escape(original_name, quote=True)}">'
            '</a>'
            f'<figcaption><strong>{escape(original_name)}</strong>'
            f'<span>{after / 1024:.0f} KB · was {before / 1024:.0f} KB</span></figcaption>'
            '</figure>'
        )

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Appetite — image review grid</title>
<style>
*{box-sizing:border-box}body{margin:0;padding:24px;font:14px/1.4 Arial,sans-serif;color:#222;background:#f7f6f2}
header{max-width:1500px;margin:0 auto 24px}h1{font-size:22px;font-weight:500;margin:0 0 8px}
p{margin:0;color:#666}.grid{max-width:1500px;margin:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px}
.card{margin:0;min-width:0}.card a{display:block;background:#e8e6e0;aspect-ratio:4/3;overflow:hidden}
.card img{width:100%;height:100%;object-fit:contain;display:block}.card figcaption{padding:8px 1px;display:grid;gap:4px;overflow-wrap:anywhere}
.card strong{font-weight:500}.card span{font-size:12px;color:#777}
</style></head><body><header><h1>Appetite — image review</h1>
<p>Temporary contact sheet for choosing the strongest images. Originals are untouched. Click an image to open the optimised version.</p></header>
<div class="grid">""" + "\n".join(card_html) + """</div></body></html>"""
    REVIEW_PAGE.write_text(page, encoding="utf-8")
    print(f"Processed {len(cards)} images. Total: {total_before:,} -> {total_after:,} bytes.")
    print(f"Created {REVIEW_PAGE.name}")

if __name__ == "__main__":
    main()
