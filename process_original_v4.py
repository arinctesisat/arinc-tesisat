from PIL import Image, ImageOps
import numpy as np

def process_original_logo_v4(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    
    # Get the data
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    
    # 1. Target the black trapezoid. 
    # Usually around (33, 29, 34) or similar dark values.
    # We use a threshold for very dark pixels.
    dark_mask = (r < 65) & (g < 65) & (b < 65)
    
    # 2. Target the white background.
    # Usually around (240-255, 240-255, 240-255).
    # But we must avoid the white text "Yıltek Mühendislik ve Yapı Market".
    # Yıltek Mühendislik ve Yapı Market is white on the black trapezoid.
    
    # We can use flood fill for the EXTERIOR white.
    # Let's try to do it properly with a mask.
    
    mask = Image.new('L', img.size, 255) # Start with all opaque
    
    # Create a mask for dark pixels
    dark_pixels = (r < 65) & (g < 65) & (b < 65)
    
    # Create a mask for white pixels
    white_pixels = (r > 230) & (g > 230) & (b > 230)
    
    # We'll set dark pixels to transparent
    data[dark_pixels, 3] = 0
    
    # Now for white pixels, we only want the ones that are NOT the text.
    # The text "Yıltek Mühendislik ve Yapı Market" is in the middle-right.
    # The background white is on the borders.
    # We can use flood fill from the corners of a temporary mask.
    temp_img = Image.fromarray(data)
    
    # Use floodfill to make exterior white transparent
    # We start from corner
    for seed in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)]:
        p = temp_img.getpixel(seed)
        if p[0] > 200 and p[1] > 200 and p[2] > 200:
            Image.floodfill(temp_img, seed, (0, 0, 0, 0), thresh=50)
            
    # Crop to content
    bbox = temp_img.getbbox()
    if bbox:
        temp_img = temp_img.crop(bbox)
        
    temp_img.save(output_path)
    print(f"Processed logo (v4) saved to {output_path}")

if __name__ == "__main__":
    process_original_logo_v4('static/uploads/WhatsApp_Image_2025-12-28_at_17._1.png', 'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_original_transparent_v4.png')
