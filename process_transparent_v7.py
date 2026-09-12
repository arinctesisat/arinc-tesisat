from PIL import Image
import numpy as np

def make_transparent(input_path, output_path, target_color=(1, 44, 76), tolerance=15):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)
    
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    tr, tg, tb = target_color
    
    dist = np.sqrt((r - tr)**2 + (g - tg)**2 + (b - tb)**2)
    mask = dist < tolerance
    
    # Set alpha to 0 for background
    data[mask, 3] = 0
    
    # Optional: Soften the edges by reducing alpha for pixels slightly outside the tolerance
    # But for a sharp logo, a clean cut is often better.
    
    res_img = Image.fromarray(data)
    # Crop to content
    bbox = res_img.getbbox()
    if bbox:
        res_img = res_img.crop(bbox)
        
    res_img.save(output_path, "PNG")
    print(f"Transparency applied (tol={tolerance}). Saved to {output_path}")

if __name__ == "__main__":
    input_file = r'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_v7_sharp.png'
    output_file = r'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_v7_transparent.png'
    make_transparent(input_file, output_file)
