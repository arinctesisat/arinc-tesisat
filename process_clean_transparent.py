import numpy as np
from PIL import Image
import scipy.ndimage as nd

def remove_bg(input_path, output_path, tolerance=30):
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    
    # We assume the top-left pixel is the background color
    tr, tg, tb = arr[0, 0, 0:3].astype(int)
    
    # Compute color distance (Manhattan)
    diff = np.abs(arr[:,:,0].astype(int) - tr) + \
           np.abs(arr[:,:,1].astype(int) - tg) + \
           np.abs(arr[:,:,2].astype(int) - tb)
           
    is_bg_color = diff < tolerance
    
    # Label connected components of the background color
    # Note: nd.label uses 4-connectivity by default. 8-connectivity is usually better to bleed through diagonal gaps.
    structure = np.ones((3, 3), dtype=int)
    labeled, num_features = nd.label(is_bg_color, structure=structure)
    
    # We will identify all the corners. If a component connects to a corner, it's outside BG.
    h, w, _ = arr.shape
    corners = [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]
    bg_labels = {labeled[r, c] for r, c in corners if labeled[r, c] != 0}
    
    # Create mask for all confirmed outside background parts
    bg_mask = np.isin(labeled, list(bg_labels))
    
    # To improve edges (anti-aliasing logic),
    # we can partially blend the pixels that are right next to the boundary.
    # A simple approach: 
    # 1. binary dilation of bg_mask -> boundary mask
    # 2. for boundary, alpha = (diff / tolerance) * 255 but let's stick to sharp first.
    # The previous attempt might have had a high tolerance causing the whole image to vanish.
    
    # Set outside pixels to transparent
    arr[bg_mask, 3] = 0
    
    res_img = Image.fromarray(arr)
    
    # Crop
    bbox = res_img.getbbox()
    if bbox:
        res_img = res_img.crop(bbox)
        
    res_img.save(output_path, "PNG")
    print(f"Clean background removal successful. Saved to {output_path}")

if __name__ == "__main__":
    remove_bg('static/uploads/Yıltek Mühendislik ve Yapı Market_logo_v7_sharp.png', 'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_v7_clean_transparent.png')
