import os
import sys
from PIL import Image

def run_tests():
    print("=== INSTAGRAM GREETING & MARKETING WEB APP - OFFLINE VERIFICATION ===")
    
    # 1. Test Asset Creation
    print("\n1. Testing Asset Creation...")
    from create_default_assets import create_default_background
    bg_path = "assets/background.png"
    if os.path.exists(bg_path):
        os.remove(bg_path)
        print("Removed existing background to test generation.")
        
    create_default_background(bg_path, width=1080, height=1080)
    
    if not os.path.exists(bg_path):
        print("❌ FAILED: background.png was not created!")
        sys.exit(1)
    print("✅ SUCCESS: Default background.png created.")
    
    # 2. Test Dimension Detection
    print("\n2. Testing Background Image Loading and Size Detection...")
    from utils import get_background_image
    bg_img, bg_w, bg_h = get_background_image(bg_path)
    print(f"Detected background dimensions: {bg_w} x {bg_h}")
    if bg_w != 1080 or bg_h != 1080:
        print("❌ FAILED: Dimensions are not 1080x1080!")
        sys.exit(1)
    print("✅ SUCCESS: Background dimensions correctly detected as 1080x1080.")
    
    # 3. Test Portrait Photo Processing (Circular crop, borders, shadows)
    print("\n3. Testing Pillow Portrait Photo Processing...")
    from utils import process_portrait_photo
    # Create a mock team member photo (500x500 green square)
    mock_photo = Image.new("RGBA", (500, 500), (0, 180, 0, 255))
    
    # Process photo
    processed = process_portrait_photo(
        mock_photo,
        size=(300, 300),
        crop_shape="Circle",
        border_color="#FFD700",
        border_thickness=10,
        shadow=True
    )
    
    # The processed photo size should be 300 + 40 (shadow margin * 2) = 340
    print(f"Processed photo size with shadow margins: {processed.size}")
    if processed.size[0] != 340 or processed.size[1] != 340:
        print("❌ FAILED: Processed image size does not match expected margin dimensions!")
        sys.exit(1)
    print("✅ SUCCESS: Portrait photo circular crop, border, and shadow applied.")
    
    # 4. Test Final Composition & Sizing Match
    print("\n4. Testing Final Image Layout and Merge Compositions...")
    from utils import compose_final_marketing_image
    
    # Create a mock AI image (800x800 magenta square)
    mock_ai_img = Image.new("RGBA", (800, 800), (255, 0, 255, 255))
    
    styles = [
        "Background Frame Overlay", 
        "Blend (Adjustable Opacity)", 
        "AI Image Framed in Center", 
        "Overlay AI Image on Background"
    ]
    
    for style in styles:
        print(f"   Testing style: {style}")
        composite = compose_final_marketing_image(
            bg_path=bg_path,
            ai_image=mock_ai_img,
            composition_style=style,
            blend_ratio=0.3,
            overlay_photo=processed,
            photo_coords=(540, 700), # Lower center-ish
            photo_scale=1.2
        )
        
        # Verify sizes match background exactly
        if composite.size != (1080, 1080):
            print(f"❌ FAILED: Composite size {composite.size} does not match background size (1080, 1080) for style {style}!")
            sys.exit(1)
            
    print("✅ SUCCESS: All composition styles successfully merged, and sizes match background exactly.")
    print("\n=== ALL OFFLINE TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
