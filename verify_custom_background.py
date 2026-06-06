import os
import sys
from PIL import Image

def test_custom_background():
    print("=== INSTAGRAM GREETING & MARKETING WEB APP - CUSTOM BACKGROUND VERIFICATION ===")
    
    bg_path = "assets/background.png"
    if not os.path.exists(bg_path):
        print(f"❌ FAILED: background image does not exist at {bg_path}!")
        sys.exit(1)
        
    # 1. Load background and verify size
    from utils import get_background_image
    bg_img, bg_w, bg_h = get_background_image(bg_path)
    print(f"✅ Successfully loaded custom background: {bg_w} x {bg_h} pixels.")
    
    # 2. Test Pillow Portrait Photo processing
    print("\nProcessing sample photo...")
    from utils import process_portrait_photo
    # Create mock portrait photo (400x400 cyan square)
    mock_photo = Image.new("RGBA", (400, 400), (0, 255, 255, 255))
    processed_photo = process_portrait_photo(
        mock_photo,
        size=(250, 250),
        crop_shape="Rounded Square",
        border_color="#D4AF37", # Gold
        border_thickness=8,
        shadow=True
    )
    print("✅ Successfully processed sample photo (cropped, border and shadow applied).")
    
    # 3. Test Composition
    print("\nMerging mock AI graphic onto custom background...")
    from utils import compose_final_marketing_image
    
    # Create mock AI image (1200x900 landscape square, different aspect ratio)
    mock_ai_img = Image.new("RGBA", (1200, 900), (255, 165, 0, 255))
    
    # Try the Background Frame Overlay style
    composite = compose_final_marketing_image(
        bg_path=bg_path,
        ai_image=mock_ai_img,
        composition_style="Background Frame Overlay",
        blend_ratio=0.5,
        overlay_photo=processed_photo,
        photo_coords=(bg_w // 2, bg_h // 2), # center
        photo_scale=1.0
    )
    
    print(f"Output composite size: {composite.size}")
    if composite.size != (bg_w, bg_h):
        print(f"❌ FAILED: Composite size {composite.size} does not match custom background size ({bg_w}, {bg_h})!")
        sys.exit(1)
        
    # Save the composite as a test verify image
    output_verify_path = "assets/custom_background_test_output.png"
    composite.save(output_verify_path, "PNG")
    print(f"✅ SUCCESS: Composite image created and matches custom background size exactly.")
    print(f"Saved verify output to: {output_verify_path}")
    print("\n=== CUSTOM BACKGROUND TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_custom_background()
