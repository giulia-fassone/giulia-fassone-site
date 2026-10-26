from pathlib import Path
from PIL import Image, ImageOps
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "originals"
OUTPUT_ROOT = ROOT / "optimized"
FOLDERS = (
    "archaeology-of-self",
    "ruderal-i",
    "ruderal-ii",
    "fruits-of-labour",
    "the-remains-of-a-meal",
    "tools",
    "sketchbook",
)
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
MAX_EDGE = 2400

def main():
    total_before = total_after = count = 0
    for folder in FOLDERS:
        source_dir = SOURCE_ROOT / folder
        if not source_dir.is_dir():
            print(f"Skipping missing folder: {source_dir}")
            continue
        output_dir = OUTPUT_ROOT / folder
        output_dir.mkdir(parents=True, exist_ok=True)
        images = sorted(p for p in source_dir.iterdir()
                        if p.is_file() and p.suffix.lower() in EXTENSIONS)
        for source in images:
            target = output_dir / (source.stem + ".webp")
            try:
                before = source.stat().st_size
                with Image.open(source) as original:
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
                count += 1
                print(f"{source.relative_to(ROOT)} -> {target.relative_to(ROOT)}: {before:,} -> {after:,} bytes")
            except Exception as exc:
                print(f"Could not process {source}: {exc}")
                sys.exit(1)
    print(f"Processed {count} images. Total: {total_before:,} -> {total_after:,} bytes.")

if __name__ == "__main__":
    main()

# Trigger a fresh optimisation run after the workflow was added.
