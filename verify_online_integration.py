import os
import sys
from utils import get_genai_client, brainstorm_marketing_concepts, expand_concept_prompt, generate_marketing_image

def run_online_tests():
    print("=== INSTAGRAM GREETING & MARKETING WEB APP - LIVE API VERIFICATION ===")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ SKIPPED: GEMINI_API_KEY environment variable is not set.")
        print("To run online integration tests, set the environment variable:")
        print("  export GEMINI_API_KEY='your_api_key'")
        return
        
    print("Initializing GenAI Client...")
    client = get_genai_client(api_key)
    
    # 1. Test Brainstorming
    print("\n1. Testing Brainstorming...")
    purpose = "Service Promotion"
    context = "A web design agency offering a 10% summer discount on landing page designs."
    concepts = brainstorm_marketing_concepts(client, purpose, context)
    
    print(f"Generated {len(concepts)} concepts:")
    for idx, c in enumerate(concepts):
        print(f"   [{idx + 1}] Hook: {c.headline}")
        print(f"       Visual description: {c.visual_description}")
        
    if len(concepts) != 3:
        print("❌ FAILED: Did not generate exactly 3 concepts.")
        sys.exit(1)
    print("✅ SUCCESS: Gemini Brainstorming works.")
    
    # 2. Test Prompt Expansion
    print("\n2. Testing Prompt Expansion...")
    selected_concept = concepts[0]
    expanded_prompt = expand_concept_prompt(client, purpose, selected_concept)
    print(f"Expanded Prompt:\n{expanded_prompt}")
    
    if not expanded_prompt.strip():
        print("❌ FAILED: Expanded prompt is empty.")
        sys.exit(1)
    print("✅ SUCCESS: Gemini Prompt Expansion works.")
    
    # 3. Test Imagen 3 Image Generation
    print("\n3. Testing Imagen 3 Image Generation...")
    try:
        # Generate a small image to verify API access
        gen_img = generate_marketing_image(client, "A clean minimalistic landing page mockup, warm lighting, 3d render", "1:1")
        print(f"Generated image format: {gen_img.format}, size: {gen_img.size}")
        gen_img.save("assets/test_generated_image.png")
        print("✅ SUCCESS: Imagen 3 Image Generation works. Image saved to assets/test_generated_image.png")
    except Exception as e:
        print(f"❌ FAILED: Image generation failed: {e}")
        sys.exit(1)
        
    print("\n=== ALL LIVE API TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_online_tests()
