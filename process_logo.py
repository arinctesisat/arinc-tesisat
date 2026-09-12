from PIL import Image
import numpy as np

def make_transparent(input_path, output_path, target_color=(0, 29, 61), tolerance=15):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    tr, tg, tb = target_color
    dist = np.sqrt((r - tr)**2 + (g - tg)**2 + (b - tb)**2)
    mask = dist < tolerance
    data[mask, 3] = 0
    result = Image.fromarray(data)
    result.save(output_path, "PNG")
    print(f"Transparency applied (tol={tolerance}). Saved to {output_path}")

if __name__ == "__main__":
    input_file = r'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_wide_v4.png'
    output_file = r'static/uploads/Yıltek Mühendislik ve Yapı Market_logo_transparent_final.png'
    make_transparent(input_file, output_file)
