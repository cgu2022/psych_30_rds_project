# rds_chinese_character_generator.py
# Requires: pip install pillow numpy

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import random, os, sys

TEXT = "你好"
OUTPUT_SIZE = (1200, 800)
FONT_SIZE = 500
SUBTLETY = 0.425  # 0.0 very subtle --> 1.0 obvious
DOT_DENSITY = 0.10  # dot probability per pixel
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
        "[!] No listed CJK fonts found; using default (likely missing Chinese character font)."
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

    # Sanity check: make sure we actually drew the characters
    nonzero_ratio = (arr > 1e-3).mean()
    if nonzero_ratio < 0.001:
        print(
            "[!] Warning: depth map appears empty. This probably means the font did not render the Chinese characters."
        )
        print(
            "--> Install a CJK font (e.g., Noto Sans CJK) or update the font path list above."
        )
    else:
        print(f"[i] Depth map OK. Non-zero pixels: {nonzero_ratio:.3%}")

    return arr


def make_text_image(text, size, font_size):
    """Generate a simple black text on white background image."""
    W, H = size
    img = Image.new("RGB", (W, H), (255, 255, 255))  # white background
    draw = ImageDraw.Draw(img)
    font = get_font(font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    tx, ty = (W - (bbox[2] - bbox[0])) // 2, (H - (bbox[3] - bbox[1])) // 2

    # draw black text
    draw.text((tx, ty), text, fill=(0, 0, 0), font=font)

    return img


# ------------- RDS generator (single anaglyph canvas) -------------
def draw_square(canvas, x, y, size, color):
    H, W, _ = canvas.shape
    r = size // 2
    x0, x1 = max(0, x - r), min(W, x + r + 1)
    y0, y1 = max(0, y - r), min(H, y + r + 1)
    canvas[y0:y1, x0:x1] = color


def generate_random_dot_pattern(size, dot_density, dot_size, seed):
    """Generates a random dot pattern image (no depth/disparity)."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    W, H = size
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)  # white bg
    mask = np.random.rand(H, W) < dot_density

    for y in range(H):
        xs = np.where(mask[y])[0]
        for x in xs:
            # Draw black dots for the pattern
            draw_square(canvas, x, y, dot_size, [0, 0, 0])

    return Image.fromarray(canvas)


def rds_anaglyph_single(
    depth_map, max_disparity, dot_density, dot_size, seed, mode="anaglyph"
):
    """
    Generates an RDS image.

    Args:
        mode: "anaglyph" (both red and cyan), "red_only", or "cyan_only"
    """
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
            if mode in ["anaglyph", "cyan_only"]:
                draw_square(canvas, x, y, dot_size, [0, 255, 255])
            if mode in ["anaglyph", "red_only"]:
                if 0 <= xr < W:
                    draw_square(canvas, xr, y, dot_size, [255, 0, 0])
    return Image.fromarray(canvas)


# ------------- run -------------
if __name__ == "__main__":
    depth = make_text_depth_map(TEXT, OUTPUT_SIZE, FONT_SIZE, SUBTLETY, BLUR_RADIUS)

    # Generate random dot pattern (no depth)
    img_pattern = generate_random_dot_pattern(
        OUTPUT_SIZE, DOT_DENSITY, DOT_SIZE, RANDOM_SEED
    )
    out_pattern = "nihao_dot_pattern.png"
    img_pattern.save(out_pattern)
    print(f"Saved {out_pattern}")

    # Generate anaglyph (both red and cyan) - default depth
    img_anaglyph = rds_anaglyph_single(
        depth, MAX_DISPARITY, DOT_DENSITY, DOT_SIZE, RANDOM_SEED, mode="anaglyph"
    )
    out_anaglyph = "nihao_rds_subtle.png"
    img_anaglyph.save(out_anaglyph)
    print(f"Saved {out_anaglyph}")

    # Generate red-only version
    img_red = rds_anaglyph_single(
        depth, MAX_DISPARITY, DOT_DENSITY, DOT_SIZE, RANDOM_SEED, mode="red_only"
    )
    out_red = "nihao_rds_red_only.png"
    img_red.save(out_red)
    print(f"Saved {out_red}")

    # Generate cyan-only version
    img_cyan = rds_anaglyph_single(
        depth, MAX_DISPARITY, DOT_DENSITY, DOT_SIZE, RANDOM_SEED, mode="cyan_only"
    )
    out_cyan = "nihao_rds_cyan_only.png"
    img_cyan.save(out_cyan)
    print(f"Saved {out_cyan}")

    # Generate simple text image (black on white)
    img_text = make_text_image(TEXT, OUTPUT_SIZE, FONT_SIZE)
    out_text = "nihao_text.png"
    img_text.save(out_text)
    print(f"Saved {out_text}")

    # Generate multiple depth variations
    print("\n[i] Generating depth variations...")
    depth_variations = [
        (8, "shallow"),  # shallow depth
        (16, "medium"),  # medium depth (default)
        (24, "deep"),  # deep depth
        (32, "very_deep"),  # very deep depth
    ]

    for disparity, label in depth_variations:
        img_var = rds_anaglyph_single(
            depth, disparity, DOT_DENSITY, DOT_SIZE, RANDOM_SEED, mode="anaglyph"
        )
        out_var = f"nihao_rds_{label}_depth.png"
        img_var.save(out_var)
        print(f"Saved {out_var} (disparity={disparity}px)")
