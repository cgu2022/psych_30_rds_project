# Random Dot Stereogram (RDS) - Chinese Character Generator

This project generates Random Dot Stereograms (RDS) featuring Chinese characters that create a 3D effect when viewed with red-cyan anaglyph glasses.

## What is a Random Dot Stereogram?

A Random Dot Stereogram (RDS) is a type of stereoscopic image that creates the illusion of depth using random dot patterns. When viewed with red-cyan 3D glasses, certain regions appear to pop out or recede, revealing hidden shapes or text. This project creates RDS images of Chinese characters (currently specified to display "你好").

## Files in This Repository

### Main Script
- **`rds_chinese_character_generator.py`** - The main Python script that generates all RDS variations

### Generated Output Images

The script generates 9 different images:

1. **`nihao_dot_pattern.png`** - Random dot pattern without any depth (baseline reference)
2. **`nihao_text.png`** - Simple black text on white background (reference image)
3. **`nihao_rds_subtle.png`** - Full anaglyph RDS (red + cyan dots together)
4. **`nihao_rds_red_only.png`** - Red channel only (right eye view)
5. **`nihao_rds_cyan_only.png`** - Cyan channel only (left eye view)
6. **`nihao_rds_shallow_depth.png`** - Shallow 3D effect (8px disparity)
7. **`nihao_rds_medium_depth.png`** - Medium 3D effect (16px disparity)
8. **`nihao_rds_deep_depth.png`** - Deep 3D effect (24px disparity)
9. **`nihao_rds_very_deep_depth.png`** - Very deep 3D effect (32px disparity)

## How It Works

### The Process

The RDS generation follows these steps:

1. **Create Depth Map**
   - Render the Chinese characters onto a grayscale image
   - Text regions have higher brightness values than the background
   - Apply optional blur for smoother depth transitions
   - The "subtlety" parameter controls how bright the text is (0.0 = invisible, 1.0 = maximum)

2. **Generate Random Dots**
   - Create a random pattern of dots across the entire image
   - Dots are placed randomly based on the dot density parameter
   - Each dot is a small square (3x3 pixels by default)

3. **Apply Disparity (Depth Shift)**
   - For each dot position, calculate the horizontal shift based on the depth map
   - Brighter regions in the depth map get more shift
   - Create two layers: cyan dots at base position, red dots shifted horizontally
   - The shift amount is controlled by the "disparity" parameter

4. **Generate Variations**
   - Combine red and cyan for anaglyph viewing
   - Save individual color channels for analysis
   - Create multiple depth variations by changing the disparity value

### Key Parameters

Located at the top of `rds_chinese_character_generator.py`:

```python
TEXT = "你好"              # Chinese characters to render
OUTPUT_SIZE = (1200, 800)  # Image dimensions (width, height)
FONT_SIZE = 500           # Size of the text
SUBTLETY = 0.425          # Depth map contrast (0.0 = subtle, 1.0 = obvious)
DOT_DENSITY = 0.12        # Probability of dot per pixel
DOT_SIZE = 3              # Size of each dot in pixels (3x3 squares)
MAX_DISPARITY = 16        # Horizontal shift in pixels
BLUR_RADIUS = 1.0         # Gaussian blur for depth map smoothing
RANDOM_SEED = 42          # For reproducible results
```

### Understanding Subtlety vs Depth

These are two **different** parameters:

- **SUBTLETY** (0.425 by default)
  - Controls the **contrast** in the depth map
  - Determines how much the text brightness differs from the background
  - Lower values = more subtle, harder to see the depth difference
  - Higher values = more obvious depth separation
  - Range: 0.0 (no difference) to 1.0 (maximum difference)

- **MAX_DISPARITY** (16 by default)
  - Controls the **magnitude** of the 3D effect
  - Determines how many pixels the dots shift horizontally
  - Lower values = shallow 3D effect, easier to fuse
  - Higher values = deep 3D effect, more dramatic but harder to view
  - Typical range: 4-32 pixels

**Together:** The formula `(depth_map - 0.5) * 2.0 * max_disparity` combines both:
- Subtlety determines the depth map values (how bright the text is)
- Disparity multiplies those values to create the actual pixel shift

## Installation & Usage

### Requirements

```bash
pip install pillow numpy
```

### Running the Script

Simply run:

```bash
python rds_chinese_character_generator.py
```

The script will generate all 9 output images in the current directory.

### Customization

Edit the parameters at the top of the script to customize:
- Change `TEXT` to different Chinese characters
- Adjust `SUBTLETY` to make the depth more/less obvious
- Modify `MAX_DISPARITY` for different depth strengths
- Change `DOT_DENSITY` for more/fewer dots
- Update `DOT_SIZE` for larger/smaller dots

### Font Requirements

The script attempts to use common Chinese fonts:
- **Windows**: Microsoft YaHei (msyh.ttc), SimHei (simhei.ttf)
- **macOS**: PingFang, Hiragino Sans GB

If no Chinese font is found, it will use the default font (which may not display Chinese characters correctly). Install a CJK (Chinese-Japanese-Korean) font if needed.

## Viewing the Results

### With Red-Cyan Glasses
1. Put on red-cyan anaglyph 3D glasses
2. View the `nihao_rds_*.png` images
3. The Chinese characters should appear to float in 3D space

### Without Glasses
- Compare the red-only and cyan-only images to see the horizontal shift
- The dot pattern image shows the baseline random pattern
- The text image provides a clear reference of what the hidden text looks like

### Depth Variations
Try viewing the different depth files to see how disparity affects the 3D effect:
- Shallow depth (8px) is easier to fuse but less dramatic
- Deep depth (32px) is more impressive but may be harder to see

## Technical Details

### Anaglyph Method
- Uses **crossed disparity** for the standard red-left/cyan-right glasses
- Red channel = right eye view (dots shifted right in text regions)
- Cyan channels (G+B) = left eye view (dots at base position)
- Your brain fuses the two views to perceive depth

### Dot Generation
- Each dot is deterministic based on `RANDOM_SEED`
- Dots are 3x3 pixel squares by default
- White background with colored dots for better visibility

## License

This is an educational project for understanding stereoscopic vision and depth perception.

---

**Created for**: Psych 30 @ Stanford | Fall 2025  
**Topic**: Random Dot Stereograms and Depth Perception
**Author**: Chris Gu
