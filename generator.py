import os
import random
import requests
from dotenv import load_dotenv
from openai import OpenAI
from moviepy import ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
load_dotenv()

# Initialize OpenAI client
# Client initialized lazily
client = None

def generate_image(prompt, size="1024x1792"): # Vertical aspect ratio for Reels/TikTok
    """
    Generates an image using OpenAI's DALL-E 3.
    Returns the local path to the saved image.
    """
    print(f"Generating image for prompt: {prompt}")
    
    # Mock Mode
    if os.getenv("MOCK_GENERATION") == "true":
        print("Mock mode enabled. Returning placeholder.")
        from PIL import Image
        # 9:16 aspect ratio approx 1024x1792
        img = Image.new('RGB', (1024, 1792), color = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)))
        filename = f"assets/mock_{random.randint(0, 10000)}.png"
        os.makedirs("assets", exist_ok=True)
        img.save(filename)
        return filename

    try:
        global client
        if not client:
             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="hd",
            n=1,
        )
        image_url = response.data[0].url
        
        img_data = requests.get(image_url).content
        filename = f"assets/gen_{random.randint(0, 10000)}.png"
        os.makedirs("assets", exist_ok=True)
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        
        return filename
    except Exception as e:
        print(f"Error generating image: {e}")
        raise Exception(f"Failed to generate image from OpenAI. Error: {e}")

def add_overlays(image_path, text, arrows=False):
    """
    Uses PIL to draw text and arrows on the image.
    Returns path to the modified image.
    """
    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            w, h = img.size
            
            # 1. Draw Text (Retro 8-bit style or Typewriter)
            # Try to load a font, fallback to default
            try:
                # Attempt to use a system font or a specific ttf if available
                # For this env, we might not have many, so we loop common ones
                font_path = "/System/Library/Fonts/Monaco.ttf" # Mac retro font
                font = ImageFont.truetype(font_path, 80)
            except:
                font = ImageFont.load_default() 

            # Calculate text position (bottom center)
            # bbox = draw.textbbox((0, 0), text, font=font)
            # text_w = bbox[2] - bbox[0]
            # text_h = bbox[3] - bbox[1]
            
            # Simple centering logic
            text_x = w / 2 - 200 # Approx centering without exact metrics if font fails
            text_y = h - 400
            
            # Draw Text with outline
            draw.text((text_x-2, text_y-2), text, font=font, fill="black")
            draw.text((text_x+2, text_y+2), text, fill="black")
            draw.text((text_x, text_y), text, font=font, fill="white")

            # 2. Draw Arrows (if requested) - "Hand drawn" simplified
            if arrows:
                # Draw crudely drawn arrows pointing to the doors
                # Assuming doors are somewhat central-ish. 
                # Left arrow
                draw.line([(100, h/2), (250, h/2 - 50)], fill="black", width=15)
                draw.line([(250, h/2 - 50), (220, h/2 - 20)], fill="black", width=15)
                draw.line([(250, h/2 - 50), (200, h/2 - 60)], fill="black", width=15)

                # Right arrow
                draw.line([(w-100, h/2), (w-250, h/2 - 50)], fill="black", width=15)
                draw.line([(w-250, h/2 - 50), (w-220, h/2 - 20)], fill="black", width=15)
                draw.line([(w-250, h/2 - 50), (w-200, h/2 - 60)], fill="black", width=15)

            output_path = f"assets/overlay_{random.randint(0,10000)}.png"
            img.save(output_path)
            return output_path
    except Exception as e:
        print(f"Overlay failed: {e}")
        return image_path

def create_liminal_reel(theme="classic"):
    """
    Orchestrates the creation of the reel.
    """
    print(f"Creating reel with theme: {theme}")

    # 0. Validate API Key
    if not os.getenv("OPENAI_API_KEY") and os.getenv("MOCK_GENERATION") != "true":
         raise Exception("Missing OPENAI_API_KEY. Please set it in your environment variables.")

    # 1. Define Prompts (Viral Style)
    # Refined for "Backrooms" aesthetic: beige carpet, drop ceiling, dark entity
    base_prompt = "Vertical 9:16. Liminal space, The Backrooms level 0. Endless beige carpet, yellow wallpaper, buzzing fluorescent lights. Two doors at the end of the hallway. Left door is RED, Right door is BLUE. A tall, dark, skinny shadow entity is peeking from the far left corner. POV shot, realistic, vhs camcorder style."
    
    horror_prompt = "Vertical 9:16. POV horror. Inside a small dark room, a terrifying pale face with wide eyes is screaming directly at the camera. Glitch effect, distorted, analog horror style. 0% survival chance."
    
    heaven_prompt = "Vertical 9:16. POV. A beautiful surreal meadow with giant floating geometric shapes, clouds, soft pink and blue sky. Dreamcore aesthetic. 100% survival chance. Peaceful."

    # 2. Generate Assets
    print("Generating assets...")
    # generate_image now raises Exception on failure
    intro_raw = generate_image(base_prompt)
    
    # Add "PICK A DOOR" and Arrows to Intro
    intro_img = add_overlays(intro_raw, "PICK A DOOR", arrows=True)

    outcome_type = random.choice(["survival", "heaven"])
    if outcome_type == "survival":
        outcome_raw = generate_image(horror_prompt)
        outcome_text = "SURVIVAL: 0%"
    else:
        outcome_raw = generate_image(heaven_prompt)
        outcome_text = "YOU SURVIVED"
        
    outcome_img = add_overlays(outcome_raw, outcome_text, arrows=False)

    # 3. Create Video Clips
    # Intro: 4 seconds (Viral pace is fast)
    intro_clip = ImageClip(intro_img).with_duration(4)
    
    # Outcome: 4 seconds
    outcome_clip = ImageClip(outcome_img).with_duration(4)

    # Transitions? Simple cut is often scarier/more viral for this style.
    
    final_clip = concatenate_videoclips([intro_clip, outcome_clip])
    
    output_filename = f"output_reel_{random.randint(0,999)}.mp4"
    output_path = os.path.join("static", "output", output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_clip.write_videofile(output_path, fps=24, codec="libx264") # Ensure compatible codec
    print(f"Video saved to {output_path}")
    return output_filename # Return filename for web URL construction

if __name__ == "__main__":
    create_liminal_reel()
