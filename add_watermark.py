#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量加入「摩瑪建材」浮水印腳本
- 位置：中間斜向
- 透明度：30%
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import math

# 設定
WATERMARK_TEXT = "摩瑪建材"
OPACITY = 0.15  # 15% 透明度（更淡）
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"  # 微軟雅黑
ANGLE = -30  # 旋轉角度（負數為順時針）
BASE_DIR = r"C:\Users\詹家騏\Desktop\website\型錄網站"

# 排除的檔案或資料夾
EXCLUDE_FILES = ["LINE@_QR.jpg", "brand-system.jpg"]
EXCLUDE_DIRS = [".git", "__pycache__", "node_modules"]


def add_watermark(image_path):
    """為單張圖片加入浮水印"""
    try:
        # 開啟圖片
        img = Image.open(image_path)

        # 確保圖片是 RGBA 模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        width, height = img.size

        # 根據圖片大小計算字體大小
        font_size = max(20, min(width, height) // 8)

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            print(f"  警告：無法載入字體，使用預設字體")
            font = ImageFont.load_default()

        # 建立透明圖層用於浮水印
        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # 取得文字尺寸
        bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 計算對角線長度，確保旋轉後可以覆蓋整張圖片
        diagonal = int(math.sqrt(width**2 + height**2))

        # 建立一個更大的透明圖層來放置重複的浮水印
        big_layer = Image.new('RGBA', (diagonal * 2, diagonal * 2), (255, 255, 255, 0))
        big_draw = ImageDraw.Draw(big_layer)

        # 計算浮水印間距（加大間距，減少重複）
        spacing_x = text_width + 200
        spacing_y = text_height + 250

        # 浮水印顏色（灰色，帶透明度）
        alpha = int(255 * OPACITY)
        watermark_color = (128, 128, 128, alpha)

        # 在大圖層上重複繪製浮水印
        y = 0
        row = 0
        while y < diagonal * 2:
            x = -spacing_x // 2 if row % 2 else 0  # 交錯排列
            while x < diagonal * 2:
                big_draw.text((x, y), WATERMARK_TEXT, font=font, fill=watermark_color)
                x += spacing_x
            y += spacing_y
            row += 1

        # 旋轉浮水印圖層
        rotated = big_layer.rotate(ANGLE, expand=False, center=(diagonal, diagonal))

        # 裁切到原始圖片大小
        crop_x = (diagonal * 2 - width) // 2
        crop_y = (diagonal * 2 - height) // 2
        cropped = rotated.crop((crop_x, crop_y, crop_x + width, crop_y + height))

        # 合併圖層
        result = Image.alpha_composite(img, cropped)

        # 判斷原始格式
        original_format = image_path.lower().split('.')[-1]

        # 儲存
        if original_format in ['jpg', 'jpeg']:
            # JPEG 不支援透明，轉換為 RGB
            result = result.convert('RGB')
            result.save(image_path, 'JPEG', quality=95)
        elif original_format == 'webp':
            result.save(image_path, 'WEBP', quality=95)
        else:
            result.save(image_path, 'PNG')

        return True

    except Exception as e:
        print(f"  錯誤：{e}")
        return False


def find_images(base_dir):
    """找出所有圖片檔案"""
    images = []
    valid_extensions = {'.png', '.jpg', '.jpeg', '.webp'}

    for root, dirs, files in os.walk(base_dir):
        # 排除特定資料夾
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file in EXCLUDE_FILES:
                continue

            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                images.append(os.path.join(root, file))

    return images


def main():
    print("=" * 60)
    print("摩瑪建材 - 批量浮水印工具")
    print("=" * 60)
    print(f"設定：")
    print(f"  浮水印文字：{WATERMARK_TEXT}")
    print(f"  透明度：{int(OPACITY * 100)}%")
    print(f"  位置：中間斜向（{ANGLE}度）")
    print(f"  目標資料夾：{BASE_DIR}")
    print("=" * 60)

    # 找出所有圖片
    images = find_images(BASE_DIR)
    total = len(images)

    print(f"\n找到 {total} 張圖片")

    if total == 0:
        print("沒有找到圖片，結束程式。")
        return

    # 開始處理
    success = 0
    failed = 0

    for i, image_path in enumerate(images, 1):
        relative_path = os.path.relpath(image_path, BASE_DIR)
        try:
            display_path = relative_path.encode('cp950', errors='replace').decode('cp950')
        except:
            display_path = f"image_{i}"

        print(f"[{i}/{total}] {display_path}", end="")

        if add_watermark(image_path):
            print(" [OK]")
            success += 1
        else:
            print(" [FAIL]")
            failed += 1

    print("\n" + "=" * 60)
    print(f"完成！成功：{success}，失敗：{failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
