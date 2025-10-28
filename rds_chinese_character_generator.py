# rds_chinese_character_generator.py
# Requires: pip install pillow numpy

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import random, os, sys

TEXT = "你好"
OUTPUT_SIZE = (1200, 800)
FONT_SIZE = 500
SUBTLETY = 0.425  # 0.0 very subtle --> 1.0 obvious
DOT_DENSITY = 0.12  # dot probability per pixel
DOT_SIZE = 3  # 3x3 squares
MAX_DISPARITY = 16  # pixels
BLUR_RADIUS = 1.0
RANDOM_SEED = 42


# ------------- font helper -------------
def try_load_font(candidates, size):
    for path in candidates:
        try:
            f = ImageFont.truetype(path, size)
            print(f"[OK] Using font: {path}")
            return f
        except Exception:
            pass
    print(
        "[!] No listed CJK fonts found; using default (likely missing Chinese glyphs)."
    )
    return ImageFont.load_default()


def get_font(size):
    # Add/modify paths that exist on your machine (absolute paths work too)
    candidates = [
        # Common Windows
        r"C:\Windows\Fonts\msyh.ttc",  # Microsoft YaHei
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\msjh.ttc",
        # Common macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB W3.ttc",
    ]
    return try_load_font(candidates, size)


# ------------- depth map from text -------------
def make_text_depth_map(text, size, font_size, subtlety, blur_radius):
    W, H = size
    img = Image.new("L", (W, H), 0)  # black=far
    draw = ImageDraw.Draw(img)
    font = get_font(font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    tx, ty = (W - (bbox[2] - bbox[0])) // 2, (H - (bbox[3] - bbox[1])) // 2

    # draw with reduced intensity for subtlety
    draw.text((tx, ty), text, fill=int(255 * float(subtlety)), font=font)

    if blur_radius > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur_radius))

    arr = np.asarray(img).astype(np.float32) / 255.0

    # Sanity check: make sure we actually drew glyphs
    nonzero_ratio = (arr > 1e-3).mean()
    if nonzero_ratio < 0.001:
        print(
            "[!] Warning: depth map appears empty. This means the font did not render Chinese glyphs."
        )
        print(
            "    -> Install a CJK font (e.g., Noto Sans CJK) or update the font path list above."
        )
    else:
        print(f"[i] Depth map OK. Non-zero pixels: {nonzero_ratio:.3%}")

    return arr


# ------------- RDS generator (single anaglyph canvas) -------------
def draw_square(canvas, x, y, size, color):
    H, W, _ = canvas.shape
    r = size // 2
    x0, x1 = max(0, x - r), min(W, x + r + 1)
    y0, y1 = max(0, y - r), min(H, y + r + 1)
    canvas[y0:y1, x0:x1] = color


def rds_anaglyph_single(depth_map, max_disparity, dot_density, dot_size, seed):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    H, W = depth_map.shape
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)  # white bg

    # map 0..1 depth around 0.5 baseline to +/- disparity
    disp = np.rint((depth_map - 0.5) * 2.0 * max_disparity).astype(np.int32)
    mask = np.random.rand(H, W) < dot_density

    for y in range(H):
        xs = np.where(mask[y])[0]
        for x in xs:
            d = int(disp[y, x])
            xr = x + d
            # cyan at base; red shifted horizontally
            draw_square(canvas, x, y, dot_size, [0, 255, 255])
            if 0 <= xr < W:
                draw_square(canvas, xr, y, dot_size, [255, 0, 0])
    return Image.fromarray(canvas)


# ------------- run -------------
if __name__ == "__main__":
    depth = make_text_depth_map(TEXT, OUTPUT_SIZE, FONT_SIZE, SUBTLETY, BLUR_RADIUS)
    img = rds_anaglyph_single(depth, MAX_DISPARITY, DOT_DENSITY, DOT_SIZE, RANDOM_SEED)
    out = "nihao_rds_subtle.png"
    img.save(out)
    print(f"[✓] Saved {out}")
