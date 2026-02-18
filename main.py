import argparse
import os
from generator import create_liminal_reel
from uploader import upload_to_tiktok, upload_to_instagram

def main():
    parser = argparse.ArgumentParser(description="Liminal Horror Reel Generator")
    parser.add_argument("--upload", action="store_true", help="Upload to social media after generation")
    args = parser.parse_args()

    print("--- Starting Horror Reel Generator ---")
    
    # Generate video
    try:
        video_path = "output_reel.mp4"
        create_liminal_reel() # This creates output_reel.mp4
        
        if not os.path.exists(video_path):
            print("Error: Video generation failed.")
            return

        print(f"Video generated successfully at {video_path}")

        # Upload if requested
        if args.upload:
            caption = "#liminalspaces #horror #fyp #choice #scary"
            upload_to_tiktok(video_path, caption)
            upload_to_instagram(video_path, caption)
        else:
            print("Skipping upload. Use --upload to publish.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
