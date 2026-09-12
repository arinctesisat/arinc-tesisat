from PIL import Image
import numpy as np

def brute_force_transparency(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    
    # Target dark trapezoid
    # #211D22 is (33, 29, 34)
    # Target white background #FFFFFF
    
    # We remove anything that is very dark OR very bright EXCEPT the logo content.
    # We can detect the plumber/text which have high chroma or specific colors.
    
    # Mask for trapezoid:
    mask_trap = (r < 70) & (g < 70) & (b < 70)
    
    # Mask for white outer:
    # Actually, we can use the fact that the white outer is contiguous.
    # But let's just use a high threshold for white.
    mask_white = (r > 230) & (g > 230) & (b > 230)
    
    # But "Yıltek Mühendislik ve Yapı Market" text is also white!
    # We can distinguish "Yıltek Mühendislik ve Yapı Market" because it's INSIDE the dark area.
    # A simple trick: if we remove the trap FIRST, the "Yıltek Mühendislik ve Yapı Market" text will have transparency around it.
    
    data[mask_trap, 3] = 0
    # Now, only the white background at the very edges should be removed.
    # We can use flood fill for this.
    
    res_img = Image.fromarray(data)
    # Flood fill corners
    for x, y in [(0,0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)]:
        p = res_img.getpixel((x,y))
        if p[0] > 200 and p[1] > 200 and p[2] > 200:
            Image.floodfill(res_img, (x,y), (0,0,0,0), thresh=100) # Higher threshold
            
    # Crop
    bbox = res_img.getbbox()
    if bbox:
        res_img = res_img.crop(bbox)
        
    res_img.save(output_path)
    print(f"Brute force processing done. Saved to {output_path}")

if __name__ == "__main__":
    brute_force_transparency('static/uploads/WhatsApp_Image_2025-12-28_at_17._1.png', 'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_original_transparent_v5.png')
