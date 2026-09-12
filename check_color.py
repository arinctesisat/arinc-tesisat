from PIL import Image

def get_bg_color(path):
    img = Image.open(path).convert("RGB")
    # Get top-left pixel
    color = img.getpixel((10, 10))
    print(f"Background color: {color}")
    # Hex
    hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
    print(f"Hex color: {hex_color}")

if __name__ == "__main__":
    get_bg_color(r"C:\Users\MUHAMMED ASAF BUDAK\.gemini\antigravity\brain\9ce5a6aa-522f-4ef0-b39a-31589753a006\Yıltek Mühendislik ve Yapı Market_logo_v7_ultra_integrated_bg_1775506106059.png")
