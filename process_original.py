from PIL import Image
import numpy as np

def process_original_logo(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    
    # 1. Remove the black trapezoid (roughly #211D22)
    # Range 0-60
    trap_mask = (r < 65) & (g < 65) & (b < 65)
    
    # 2. Remove the white background (roughly #FFFFFF)
    # But wait, Yıltek Mühendislik ve Yapı Market is white.
    # We'll use the fact that Yıltek Mühendislik ve Yapı Market is white but it HAS an outline.
    # If we remove all white, the outline remains. 
    # Actually, let's see. 
    # If we only remove the trapezoid, does it look okay?
    # In the previous step, removing only the trapezoid left the white outer box.
    
    # Let's remove BOTH the trapezoid and the white background.
    white_mask = (r > 240) & (g > 240) & (b > 240)
    
    # Apply both masks to transparency
    arr[trap_mask, 3] = 0
    arr[white_mask, 3] = 0
    
    img = Image.fromarray(arr)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    img.save(output_path)
    print(f"Processed logo (version 3) saved to {output_path}")

if __name__ == "__main__":
    process_original_logo('static/uploads/WhatsApp_Image_2025-12-28_at_17._1.png', 'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_original_transparent.png')
