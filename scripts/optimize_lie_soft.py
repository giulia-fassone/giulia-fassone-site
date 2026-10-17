from pathlib import Path
from PIL import Image, ImageOps
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "optimized"
OUTPUT.mkdir(exist_ok=True)

# Images used on lie-soft.html. Original files are never changed.
SOURCES = [
    "Butter2.jpg",
    "Lie-Soft2.jpg",
    "Lie_soft_text.png",
    "Cast-Moss-Fingers.jpg",
    "Sin-Proof-2025.jpg",
    "Baton-P1100275-1-2.jpg",
    "Hooked-stone-thumbnail.png",
    "Butter3.jpg",
    "Givetake2.jpg",
    "1.jpg",
    "2.jpg",
    "Butter-Fingers.jpg",
    "ClippedClamped.jpg",
    "Cushion.jpg",
    "Givetake.jpg",
    "Joint-pain.jpg",
    "Cushion-P1100288.jpg",
]

MAX_EDGE = 2400

def main():
    missing = []
    converted = []
    for filename in SOURCES:
        source = ROOT / filename
        if not source.is_file():
            missing.append(filename)
            continue

        target = OUTPUT / (source.stem + ".webp")
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original)
            has_alpha = "A" in image.getbands() or "transparency" in image.info
            # Keep written text and transparent PNG artwork lossless.
            lossless = source.suffix.lower() == ".png"
            image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
            save_args = {"format": "WEBP", "method": 6, "lossless": lossless}
            if not lossless:
                save_args["quality"] = 84
            if has_alpha:
                image = image.convert("RGBA")
            elif image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            image.save(target, **save_args)
        converted.append((filename, target.stat().st_size))

    print(f"Converted {len(converted)} images:")
    for filename, size in converted:
        print(f"  {filename} -> optimized/{Path(filename).stem}.webp ({size:,} bytes)")
    if missing:
        print("Missing source images: " + ", ".join(missing))
        sys.exit(1)

if __name__ == "__main__":
    main()
