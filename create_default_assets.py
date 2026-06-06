import os
from PIL import Image, ImageDraw, ImageFilter

def create_default_background(output_path="assets/background.png", width=1080, height=1080):
    # Ensure assets directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create gradient background
    base = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(base)
    
    # Draw linear/radial gradient
    for y in range(height):
        # Blend from deep indigo/slate to rich dark purple
        r = int(24 + (40 - 24) * (y / height))
        g = int(20 + (16 - 20) * (y / height))
        b = int(38 + (55 - 38) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Draw some abstract soft glow circles in background
    # Circle 1: Top-Left (Soft Pinkish Glow)
    glow1 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw1 = ImageDraw.Draw(glow1)
    glow_draw1.ellipse([(-200, -200), (600, 600)], fill=(255, 105, 180, 40))
    glow1 = glow1.filter(ImageFilter.GaussianBlur(120))
    base = Image.alpha_composite(base, glow1)
    
    # Circle 2: Bottom-Right (Soft Gold/Cyan Glow)
    glow2 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw2 = ImageDraw.Draw(glow2)
    glow_draw2.ellipse([(width-600, height-600), (width+200, height+200)], fill=(0, 206, 209, 30))
    glow2 = glow2.filter(ImageFilter.GaussianBlur(150))
    base = Image.alpha_composite(base, glow2)
    
    # Add a thin stylish border
    draw_final = ImageDraw.Draw(base)
    border_margin = 40
    # Gold/Bronze-ish border
    draw_final.rectangle(
        [(border_margin, border_margin), (width - border_margin, height - border_margin)],
        outline=(212, 175, 55, 100), # semi-transparent gold
        width=2
    )
    
    # Add thin outer white border
    draw_final.rectangle(
        [(15, 15), (width - 15, height - 15)],
        outline=(255, 255, 255, 30), # very faint white
        width=1
    )
    
    # Save the background
    base.convert("RGB").save(output_path, "PNG")
    print(f"Created a premium default background image at {output_path} ({width}x{height})")

if __name__ == "__main__":
    create_default_background()
