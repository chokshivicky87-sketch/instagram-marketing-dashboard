import streamlit as st
import os
import io
from PIL import Image
from utils import (
    get_background_image,
    get_genai_client,
    brainstorm_marketing_concepts,
    expand_concept_prompt,
    generate_marketing_image,
    process_portrait_photo,
    compose_final_marketing_image
)
from create_default_assets import create_default_background

# Set page config
st.set_page_config(
    page_title="Instagram Greeting & Marketing Dashboard",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern glassmorphism UI & premium aesthetics
st.markdown("""
<style>
    /* Main Background and Colors */
    .stApp {
        background-color: #0F0E17;
        color: #FFFFFE;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header and Typography */
    h1, h2, h3 {
        color: #FFFFFE !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .main-title {
        background: linear-gradient(135deg, #FF8E53 0%, #FF2E93 50%, #8A2387 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .subtitle {
        text-align: center;
        color: #A7A9BE;
        font-size: 1.1rem;
        margin-top: -1.5rem;
        margin-bottom: 3rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #16161A !important;
        border-right: 1px solid #242629;
    }
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
        color: #FF2E93 !important;
    }
    
    /* Glassmorphism Card Style */
    .glass-card {
        background: rgba(22, 22, 26, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .concept-card {
        border-left: 5px solid #FF2E93;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .concept-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(255, 46, 147, 0.15);
    }
    
    /* Streamlit widgets modifications */
    div.stButton > button {
        background: linear-gradient(135deg, #FF8E53 0%, #FF2E93 100%);
        color: white !important;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity 0.2s ease, transform 0.1s ease;
    }
    
    div.stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }
    
    div.stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Badge styling */
    .step-badge {
        background-color: #72757E;
        color: #FFFFFE;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 10px;
    }
    
    .step-active {
        background-color: #FF2E93 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "concepts" not in st.session_state:
    st.session_state.concepts = None
if "selected_concept_idx" not in st.session_state:
    st.session_state.selected_concept_idx = 0
if "refined_prompt" not in st.session_state:
    st.session_state.refined_prompt = ""
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "composite_image" not in st.session_state:
    st.session_state.composite_image = None

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # API Key Handling
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Provide your Gemini API key. If unset, the app will look for the GEMINI_API_KEY environment variable."
    )
    
    st.markdown("---")
    
    # Background Image Asset Sizing Info
    st.markdown("### 🖼️ Permanent Background Asset")
    bg_path = "assets/background.png"
    
    # Check if default background exists
    if not os.path.exists(bg_path):
        st.warning("No background image found. Generating a premium default placeholder...")
        create_default_background(bg_path)
        
    try:
        bg_img, bg_w, bg_h = get_background_image(bg_path)
        st.success(f"Detected Background Image: **{bg_w} x {bg_h} px**")
        st.image(bg_img, caption="Current Background Template", use_container_width=True)
    except Exception as e:
        st.error(f"Error loading background: {e}")
        bg_w, bg_h = 1080, 1080
        
    # Option to upload/replace the permanent background
    new_bg_file = st.file_uploader(
        "Upload Custom Background.png",
        type=["png"],
        help="Upload a new background image to replace the permanent asset. Dimensions will be auto-detected."
    )
    if new_bg_file:
        try:
            # Overwrite the background.png file
            with open(bg_path, "wb") as f:
                f.write(new_bg_file.getbuffer())
            st.success("Background replaced successfully! Reloading dimensions...")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save custom background: {e}")
            
    # Reset/Generate default button
    if st.button("Reset Default Background"):
        create_default_background(bg_path)
        st.success("Default background restored!")
        st.rerun()

# Header
st.markdown('<div class="main-title">Instagram Greeting & Marketing Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">An intelligent engine to brainstorm, generate, and composite premium marketing visuals.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Wizard Steps Navigation Banner
# ---------------------------------------------------------------------------
step_cols = st.columns(5)
steps_info = [
    ("1. Inputs", 1),
    ("2. Brainstorm", 2),
    ("3. Prompt & Gen", 3),
    ("4. Layout & Merge", 4),
    ("5. Download", 5)
]

for idx, (label, s_num) in enumerate(steps_info):
    is_active = st.session_state.step == s_num
    badge_class = "step-badge step-active" if is_active else "step-badge"
    step_cols[idx].markdown(
        f'<div style="text-align: center;"><span class="{badge_class}">{s_num}</span><b>{label}</b></div>',
        unsafe_allow_html=True
    )
st.markdown("---")

# Verify client configuration
client = None
if api_key_input:
    client = get_genai_client(api_key_input)
else:
    # Attempt to fall back to environment variable
    try:
        client = get_genai_client()
    except Exception:
        pass

if not client:
    st.warning("⚠️ Please provide a **Gemini API Key** in the sidebar to run brainstorming and image generation.")

# ---------------------------------------------------------------------------
# Step 1: UI & Feature Selection (Use Cases)
# ---------------------------------------------------------------------------
if st.session_state.step == 1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Step 1: Select Use Case & Provide Details")
    
    purpose = st.selectbox(
        "Choose Purpose / Use Case",
        ["Festive Greeting", "Service Promotion", "Birthday Wish"],
        help="Select the marketing or greeting focus of your Instagram post."
    )
    
    # Store in session state to handle step changes
    st.session_state.purpose = purpose
    
    user_input = ""
    birthday_name = ""
    birthday_wishes = ""
    uploaded_photo = None
    
    if purpose in ["Festive Greeting", "Service Promotion"]:
        user_input = st.text_area(
            "Enter Description & Key Features",
            placeholder="e.g. A gorgeous Diwali greeting post welcoming Prosperity. Mention a 20% discount on all software items.",
            height=150,
            help="Describe the event, features, services, offers, or tone you want."
        )
    else: # Birthday Wish
        col1, col2 = st.columns(2)
        with col1:
            birthday_name = st.text_input(
                "Team Member's Name",
                placeholder="e.g. Sarah Jenkins",
                help="Enter the name of the birthday celebrant."
            )
        with col2:
            birthday_wishes = st.text_area(
                "Wishes & Traits",
                placeholder="e.g. Wishing Sarah a fantastic birthday! She is a senior developer who loves coffee, hiking, and coding clean apps.",
                height=100,
                help="Describe their personality, job role, hobbies, or specific birthday wishes."
            )
            
        st.markdown("---")
        st.markdown("### 👤 Portrait Photo Input")
        uploaded_photo = st.file_uploader(
            "Upload Team Member's Photograph (Optional)",
            type=["png", "jpg", "jpeg"],
            help="Upload a portrait photo. Pillow will crop it elegantly and place it over the generated artwork."
        )
        
    # Save inputs to session state
    st.session_state.user_input = user_input
    st.session_state.birthday_name = birthday_name
    st.session_state.birthday_wishes = birthday_wishes
    st.session_state.uploaded_photo_raw = uploaded_photo

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_prev, col_next = st.columns([1, 8])
    if col_next.button("Next: Brainstorm Concepts ➡️"):
        # Validate inputs
        if not client:
            st.error("API Key must be configured to proceed.")
        elif purpose in ["Festive Greeting", "Service Promotion"] and not user_input.strip():
            st.error("Please provide a description/features to brainstorm.")
        elif purpose == "Birthday Wish" and not birthday_name.strip():
            st.error("Please provide the team member's name.")
        else:
            st.session_state.step = 2
            st.rerun()

# ---------------------------------------------------------------------------
# Step 2: Brainstorming & Concept Selection (Gemini API)
# ---------------------------------------------------------------------------
elif st.session_state.step == 2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("💡 Step 2: Brainstorming Concepts")
    st.info(f"Targeting: **{st.session_state.purpose}**")
    
    # Generate concepts using Gemini if not already generated
    if st.session_state.concepts is None:
        with st.spinner("🧠 Gemini is brainstorming concepts and marketing hooks..."):
            try:
                # Build context string
                if st.session_state.purpose == "Birthday Wish":
                    context = f"Name: {st.session_state.birthday_name}. Wishes/Traits: {st.session_state.birthday_wishes}"
                else:
                    context = st.session_state.user_input
                
                concepts = brainstorm_marketing_concepts(
                    client,
                    st.session_state.purpose,
                    context
                )
                st.session_state.concepts = concepts
            except Exception as e:
                st.error(f"Error during brainstorming: {e}")
                
    if st.session_state.concepts:
        st.write("Review the concepts generated by Gemini and select the one you want to expand:")
        
        # Display concepts beautifully
        for idx, concept in enumerate(st.session_state.concepts):
            st.markdown(f"""
            <div class="glass-card concept-card">
                <h4>Option {idx + 1}: {concept.headline}</h4>
                <p><b>Visual Concept:</b> {concept.visual_description}</p>
                <p><i><b>Suggested Caption:</b> {concept.caption}</i></p>
            </div>
            """, unsafe_allow_html=True)
            
        # Selection radio
        selected_option = st.radio(
            "Select Concept",
            options=[0, 1, 2],
            format_func=lambda x: f"Option {x + 1}: {st.session_state.concepts[x].headline}",
            help="Choose the concept to convert into the final prompt."
        )
        st.session_state.selected_concept_idx = selected_option
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_prev, col_next = st.columns([1, 8])
    if col_prev.button("⬅️ Back"):
        st.session_state.step = 1
        st.session_state.concepts = None  # Reset concepts so we generate fresh if inputs change
        st.rerun()
    if col_next.button("Next: Refine Prompt ➡️"):
        # Expand concept prompt
        with st.spinner("✍️ Expanding selected concept into detailed AI image prompt..."):
            try:
                concept = st.session_state.concepts[st.session_state.selected_concept_idx]
                extra = ""
                if st.session_state.purpose == "Birthday Wish":
                    extra = f"Create beautiful background space for a portrait photo of {st.session_state.birthday_name} who loves {st.session_state.birthday_wishes}."
                expanded_prompt = expand_concept_prompt(
                    client,
                    st.session_state.purpose,
                    concept,
                    extra
                )
                st.session_state.refined_prompt = expanded_prompt
                st.session_state.step = 3
                st.rerun()
            except Exception as e:
                st.error(f"Error expanding prompt: {e}")

# ---------------------------------------------------------------------------
# Step 3: Prompt Refinement & Image Generation (Imagen 3)
# ---------------------------------------------------------------------------
elif st.session_state.step == 3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎨 Step 3: Refine Prompt & Generate AI Artwork")
    
    st.markdown("Here is the detailed prompt expanded by Gemini. You can review and edit it before running the generator:")
    
    # Prompt text area
    refined_prompt = st.text_area(
        "Final Image Prompt",
        value=st.session_state.refined_prompt,
        height=180,
        help="Edit this prompt to add specific colors, objects, or stylization before calling Imagen 3."
    )
    st.session_state.refined_prompt = refined_prompt
    
    # Detect background aspect ratio to choose matching option
    aspect_ratio_option = "1:1"
    ratio_float = bg_w / bg_h
    if abs(ratio_float - 1.0) < 0.05:
        aspect_ratio_option = "1:1"
    elif abs(ratio_float - 0.75) < 0.05 or abs(ratio_float - 0.8) < 0.05:
        aspect_ratio_option = "3:4"
    elif abs(ratio_float - 1.33) < 0.05:
        aspect_ratio_option = "4:3"
    elif abs(ratio_float - 0.56) < 0.05:
        aspect_ratio_option = "9:16"
    elif abs(ratio_float - 1.77) < 0.05:
        aspect_ratio_option = "16:9"
        
    st.markdown(f"**Auto-Selected Aspect Ratio (matched to background): {aspect_ratio_option}**")
    
    st.markdown("---")
    
    image_provider = st.radio(
        "Select AI Image Generation Engine",
        ["Pollinations AI (Flux) - FREE", "Google Imagen 4.0 (Requires Paid Key)"],
        index=0,
        help="Pollinations AI uses the open-source Flux model, completely free with no API limits. Google Imagen 4.0 is premium but requires billing enabled on your key."
    )
    
    # Generate button
    if st.button("🚀 Generate AI Artwork"):
        with st.spinner("✨ Rendering your custom artwork (takes ~5-10 seconds)..."):
            try:
                gen_img = generate_marketing_image(
                    client,
                    st.session_state.refined_prompt,
                    aspect_ratio_option,
                    provider=image_provider
                )
                st.session_state.generated_image = gen_img
                st.success("Image generated successfully!")
            except Exception as e:
                st.error(f"Image generation failed: {e}")
                
    # Show preview of generated image if exists
    if st.session_state.generated_image:
        st.markdown("### Generated Image Preview")
        st.image(st.session_state.generated_image, caption="AI Generated Image", width=400)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_prev, col_next = st.columns([1, 8])
    if col_prev.button("⬅️ Back"):
        st.session_state.step = 2
        st.rerun()
    if col_next.button("Next: Layout & Merge ➡️"):
        if not st.session_state.generated_image:
            st.error("Please generate an image first before proceeding.")
        else:
            st.session_state.step = 4
            st.rerun()

# ---------------------------------------------------------------------------
# Step 4: Image Processing, Layout & Merging (Pillow)
# ---------------------------------------------------------------------------
elif st.session_state.step == 4:
    st.subheader("📐 Step 4: Canvas Layout & Pillow Compositions")
    
    col_settings, col_preview = st.columns([1, 1])
    
    with col_settings:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎛️ Composition Settings")
        
        comp_style = st.selectbox(
            "Composition Mode",
            [
                "Fit AI Image in Content Area (Preserve Header/Footer)",
                "Background Frame Overlay", 
                "Blend (Adjustable Opacity)", 
                "AI Image Framed in Center", 
                "Overlay AI Image on Background"
            ],
            index=0,
            help="Fit AI Image: Fits the graphic into the middle white-space of the letterhead. Background Frame Overlay: AI image sits under background template (requires template to have transparent center). Blend: Fuses both images. Framed: Fits AI image in center. Overlay: Pastes AI image over background."
        )
        
        blend_ratio = 0.5
        header_margin = 180
        footer_margin = 150
        side_margin = 20
        
        if comp_style == "Blend (Adjustable Opacity)":
            blend_ratio = st.slider("Background / AI Blend Ratio", 0.0, 1.0, 0.5, 0.05, help="0.0 = Background only, 1.0 = AI image only.")
        elif comp_style == "Fit AI Image in Content Area (Preserve Header/Footer)":
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                header_margin = st.slider("Header Margin (px)", 0, bg_h // 2, 180, 10, help="Space to reserve for the logo/header at the top.")
            with col_m2:
                footer_margin = st.slider("Footer Margin (px)", 0, bg_h // 2, 150, 10, help="Space to reserve for contact info/footer at the bottom.")
            with col_m3:
                side_margin = st.slider("Side Margin (px)", 0, bg_w // 2, 20, 5, help="Space to reserve on left/right edges.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display settings for portrait photo overlay (For Birthday Wish)
        # Note: We support upload photo for all workflows if they want to override, but specifically highlight for Birthday
        has_photo = st.session_state.uploaded_photo_raw is not None
        
        if has_photo:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 👤 Portrait Photo Customization")
            
            # Load photo
            raw_photo = Image.open(st.session_state.uploaded_photo_raw)
            
            col_crop, col_border = st.columns(2)
            with col_crop:
                crop_shape = st.selectbox("Crop Shape", ["Circle", "Rounded Square", "Square"], index=0)
                photo_size = st.slider("Photo Pixel Size", 200, 600, 350, 50)
                photo_scale = st.slider("Photo Display Scale", 0.5, 2.0, 1.0, 0.1)
                
            with col_border:
                border_color = st.color_picker("Border Color", "#D4AF37") # Default gold
                border_thickness = st.slider("Border Thickness", 0, 25, 6)
                shadow_toggle = st.checkbox("Enable Drop Shadow", value=True)
                
            st.markdown("---")
            st.markdown("#### Positioning on Canvas")
            # Default center of background image
            def_x = bg_w // 2
            def_y = bg_h // 2
            
            # Simple presets
            preset_pos = st.selectbox(
                "Position Preset",
                ["Center", "Center Bottom", "Center Top", "Left Center", "Right Center", "Custom"],
                index=0
            )
            
            if preset_pos == "Center":
                pos_x, pos_y = bg_w // 2, bg_h // 2
            elif preset_pos == "Center Bottom":
                pos_x, pos_y = bg_w // 2, int(bg_h * 0.7)
            elif preset_pos == "Center Top":
                pos_x, pos_y = bg_w // 2, int(bg_h * 0.3)
            elif preset_pos == "Left Center":
                pos_x, pos_y = int(bg_w * 0.3), bg_h // 2
            elif preset_pos == "Right Center":
                pos_x, pos_y = int(bg_w * 0.7), bg_h // 2
            else: # Custom sliders
                col_x, col_y = st.columns(2)
                with col_x:
                    pos_x = st.slider("X Coordinate", 0, bg_w, def_x, 10)
                with col_y:
                    pos_y = st.slider("Y Coordinate", 0, bg_h, def_y, 10)
            
            # Process the photo with Pillow
            processed_photo = process_portrait_photo(
                raw_photo,
                size=(photo_size, photo_size),
                crop_shape=crop_shape,
                border_color=border_color,
                border_thickness=border_thickness,
                shadow=shadow_toggle
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            processed_photo = None
            pos_x, pos_y = 0, 0
            photo_scale = 1.0
            if st.session_state.purpose == "Birthday Wish":
                st.warning("⚠️ No portrait photo was uploaded in Step 1. The birthday card will be generated using only the AI artwork + background.")
                
    # Run the composition and live render
    with col_preview:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("### 👁️ Real-time Canvas Preview")
        
        # Assemble
        try:
            composite = compose_final_marketing_image(
                bg_path=bg_path,
                ai_image=st.session_state.generated_image,
                composition_style=comp_style,
                blend_ratio=blend_ratio,
                overlay_photo=processed_photo,
                photo_coords=(pos_x, pos_y),
                photo_scale=photo_scale,
                header_margin=header_margin,
                footer_margin=footer_margin,
                side_margin=side_margin
            )
            st.session_state.composite_image = composite
            st.image(composite, caption=f"Live Composite Canvas ({bg_w} x {bg_h})", use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering composition: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Navigation
    col_prev, col_next = st.columns([1, 8])
    if col_prev.button("⬅️ Back"):
        st.session_state.step = 3
        st.rerun()
    if col_next.button("Next: Review & Download ➡️"):
        st.session_state.step = 5
        st.rerun()

# ---------------------------------------------------------------------------
# Step 5: Review, Caption & Download
# ---------------------------------------------------------------------------
elif st.session_state.step == 5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📥 Step 5: Review & Download Final Post")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### Final Instagram Graphic")
        if st.session_state.composite_image:
            st.image(st.session_state.composite_image, use_container_width=True)
            
            # Prepare image buffer for download
            buf = io.BytesIO()
            st.session_state.composite_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Download High-Res PNG",
                data=byte_im,
                file_name="instagram_marketing_post.png",
                mime="image/png"
            )
        else:
            st.error("No composite image found. Please go back and complete the layout.")
            
    with col2:
        st.markdown("### 📝 Suggested Instagram Caption")
        concept = st.session_state.concepts[st.session_state.selected_concept_idx]
        
        # Display editable text box with suggested caption
        final_caption = st.text_area(
            "Copy Caption",
            value=concept.caption,
            height=280,
            help="Copy this text and paste it into your Instagram post caption."
        )
        
        st.markdown("#### Post Details Info")
        st.markdown(f"- **Purpose / Use Case**: {st.session_state.purpose}")
        st.markdown(f"- **Selected Hook**: *{concept.headline}*")
        st.markdown(f"- **Final Resolution**: {bg_w} x {bg_h} pixels")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Restart
    if st.button("🔄 Create New Post"):
        st.session_state.step = 1
        st.session_state.concepts = None
        st.session_state.generated_image = None
        st.session_state.composite_image = None
        st.rerun()
