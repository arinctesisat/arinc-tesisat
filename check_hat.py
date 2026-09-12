from PIL import Image

def get_hat_color(path):
    img = Image.open(path).convert("RGB")
    # Hat is roughly at (250, 300) in a 1024x1024 image
    color = img.getpixel((250, 300))
    print(f"Hat color: {color}")

if __name__ == "__main__":
    get_hat_color(r"static/uploads/Yıltek Mühendislik ve Yapı Market_logo_v7_sharp.png")
