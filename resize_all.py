from PIL import Image
import os
import sys

# DPI для друку
DPI = 300

# Список форматів у см (ширина, висота)
sizes_cm = [
    (15, 20),   # 6x8 inch
    (25, 25),   # 10x10 inch
    (30, 30),   # 12x12 inch
    (40, 40),   # 16x16 inch
    (45, 45),   # 18x18 inch
    (30, 45),   # 12x18 inch
    (45, 60),   # 18x24 inch
    (50, 70),   # 20x28 inch
    (60, 80),   # 24x32 inch
    (66, 90),   # 24x33 inch
    (50, 50),   # 20x20 inch
    (70, 70),   # 28x28 inch
]

# Пошук зображення в поточній директорії
def find_image():
    exts = (".jpg", ".jpeg", ".png", ".webp")
    for file in os.listdir("."):
        if file.lower().endswith(exts):
            return file
    return None

# 1. Просте масштабування
def resize_scale(img):
    output_dir = "resized_images_scale"
    os.makedirs(output_dir, exist_ok=True)
    for w_cm, h_cm in sizes_cm:
        w_px = int(w_cm / 2.54 * DPI)
        h_px = int(h_cm / 2.54 * DPI)
        resized = img.resize((w_px, h_px), Image.LANCZOS)
        output_path = os.path.join(output_dir, f"{w_cm}x{h_cm}cm.jpg")
        resized.save(output_path, quality=95)

# 2. Масштабування з обрізкою
def resize_crop(img):
    output_dir = "resized_images_crop"
    os.makedirs(output_dir, exist_ok=True)
    for w_cm, h_cm in sizes_cm:
        w_px = int(w_cm / 2.54 * DPI)
        h_px = int(h_cm / 2.54 * DPI)
        target_ratio = w_px / h_px
        img_ratio = img.width / img.height
        if img_ratio > target_ratio:
            new_height = h_px
            new_width = int(h_px * img_ratio)
        else:
            new_width = w_px
            new_height = int(w_px / img_ratio)
        resized = img.resize((new_width, new_height), Image.LANCZOS)
        left = (resized.width - w_px) // 2
        top = (resized.height - h_px) // 2
        right = left + w_px
        bottom = top + h_px
        cropped = resized.crop((left, top, right, bottom))
        output_path = os.path.join(output_dir, f"{w_cm}x{h_cm}cm.jpg")
        cropped.save(output_path, quality=95)

# 3. Масштабування з білими полями
def resize_fit(img):
    output_dir = "resized_images_fit"
    os.makedirs(output_dir, exist_ok=True)
    for w_cm, h_cm in sizes_cm:
        w_px = int(w_cm / 2.54 * DPI)
        h_px = int(h_cm / 2.54 * DPI)
        img_copy = img.copy()
        img_copy.thumbnail((w_px, h_px), Image.LANCZOS)
        background = Image.new("RGB", (w_px, h_px), (255, 255, 255))
        offset_x = (w_px - img_copy.width) // 2
        offset_y = (h_px - img_copy.height) // 2
        background.paste(img_copy, (offset_x, offset_y))
        output_path = os.path.join(output_dir, f"{w_cm}x{h_cm}cm.jpg")
        background.save(output_path, quality=95)

# Основна логіка
if __name__ == "__main__":
    image_file = find_image()
    if not image_file:
        print("❌ У цій папці не знайдено зображення!")
        sys.exit(1)

    print(f"📷 Знайдено файл: {image_file}")
    img = Image.open(image_file)

    resize_scale(img)
    print("✅ Масштабування без пропорцій готове.")
    resize_crop(img)
    print("✅ Масштабування з обрізкою готове.")
    resize_fit(img)
    print("✅ Масштабування з білими полями готове.")

    print("🎉 Всі варіанти збережені у відповідних папках!")
