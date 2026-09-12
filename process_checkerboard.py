from PIL import Image
import numpy as np

def remove_checkerboard(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    
    # 1. Detect light gray color in checkerboard: approx (204, 204, 204)
    # 2. Detect dark gray color in checkerboard: approx (255, 255, 255) in some areas?
    # No, usually checkerboards have two gray levels.
    
    # Let's target any pixel where (R==G==B) AND (R is medium gray) 
    # OR any pixel that matches the common checkerboard colors.
    
    # Actually, a better way: anything that is NOT part of the logo.
    # The logo has specific colors (Green, Blue, Yellow, Black outline).
    
    # Let's try to remove anything where R=G=B and they are within common gray ranges.
    gray_mask = (r == g) & (g == b) & (r > 150) & (r < 255)
    
    # But wait, some white parts of the plumber's tooth or eyes might be pure white (255,255,255).
    # Those should stay. 255 is not in our mask.
    
    data[gray_mask, 3] = 0
    
    # Also remove some noise
    # Any pixel very close to gray (R~G~B)
    noise_mask = (abs(r.astype(int) - g.astype(int)) < 5) & (abs(g.astype(int) - b.astype(int)) < 5) & (r > 150) & (r < 255)
    data[noise_mask, 3] = 0
    
    res_img = Image.fromarray(data)
    # Crop to content
    bbox = res_img.getbbox()
    if bbox:
        res_img = res_img.crop(bbox)
        
    res_img.save(output_path)
    print(f"Checkerboard removed. Saved to {output_path}")

if __name__ == "__main__":
    # Correct path from the tool's generated image (even though it gave error, I see it in metadata)
    # Wait, the tool gave error so the file might NOT have been saved.
    # Ah, I don't see it in the list_dir from previous turn.
    # I'll try to find it.
    pass
