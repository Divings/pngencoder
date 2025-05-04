# Copyright (c) 2025 Innovation Craft Inc. All Rights Reserved.
# 本ソフトウェアはプロプライエタリライセンスに基づき提供されています。

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import math
import lzma
import json
import os

def compress_binary(data: bytes) -> bytes:
    return lzma.compress(data)

def decompress_binary(data: bytes) -> bytes:
    return lzma.decompress(data)

def encode_image_from_compressed_data(compressed: bytes) -> Image.Image:
    pixels = []
    for i in range(0, len(compressed), 3):
        r = compressed[i]
        g = compressed[i+1] if i+1 < len(compressed) else 0
        b = compressed[i+2] if i+2 < len(compressed) else 0
        pixels.append((r, g, b))

    num_pixels = len(pixels)
    width = math.ceil(math.sqrt(num_pixels))
    height = math.ceil(num_pixels / width)

    while len(pixels) < width * height:
        pixels.append((0, 0, 0))

    img = Image.new("RGB", (width, height))
    img.putdata(pixels)
    return img

def decode_image_to_compressed_data(img: Image.Image, compressed_length: int) -> bytes:
    pixels = list(img.getdata())
    raw_bytes = bytearray()
    for r, g, b in pixels:
        raw_bytes += bytes([r, g, b])
    return raw_bytes[:compressed_length]

def encode_file():
    file_path = filedialog.askopenfilename(title="エンコードするファイルを選択")
    if not file_path:
        return

    with open(file_path, "rb") as f:
        original_data = f.read()

    compressed = compress_binary(original_data)
    img = encode_image_from_compressed_data(compressed)

    save_path = filedialog.asksaveasfilename(defaultextension=".png", title="画像として保存", filetypes=[("PNG画像", "*.png")])
    if not save_path:
        return

    img.save(save_path, "PNG")

    # メタデータ生成
    metadata = {
        "compressed_length": len(compressed),
        "original_filename": os.path.basename(file_path),
        "original_extension": os.path.splitext(file_path)[1]
    }
    meta_path = save_path + ".meta"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    messagebox.showinfo("完了", f"PNGとメタデータを保存しました。\n\n{save_path}\n{meta_path}")

def decode_file():
    image_path = filedialog.askopenfilename(title="PNG画像を選択", filetypes=[("PNG画像", "*.png")])
    if not image_path:
        return

    meta_path = filedialog.askopenfilename(title="メタデータ（.meta）を選択", filetypes=[("METAファイル", "*.meta")])
    if not meta_path:
        return

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        compressed_length = metadata["compressed_length"]
        original_extension = metadata.get("original_extension", "")
    except Exception as e:
        messagebox.showerror("エラー", f"メタデータの読み込みに失敗しました:\n{str(e)}")
        return

    try:
        img = Image.open(image_path)
        compressed = decode_image_to_compressed_data(img, compressed_length)
        restored = decompress_binary(compressed)
    except Exception as e:
        messagebox.showerror("エラー", f"復元処理中にエラーが発生しました:\n{str(e)}")
        return

    save_path = filedialog.asksaveasfilename(title="復元ファイルの保存先を選択", defaultextension=original_extension)
    if not save_path:
        return

    with open(save_path, "wb") as f:
        f.write(restored)

    messagebox.showinfo("完了", f"復元ファイルを保存しました。\n\n{save_path}")

# GUI構築
window = tk.Tk()
window.title("外部メタデータ対応 PNGステガノ圧縮ツール")
window.geometry("420x220")
window.configure(bg="#F8FAFF")

btn_encode = tk.Button(window, text="ファイル → PNG + メタデータ", font=("Arial", 14), command=encode_file)
btn_encode.pack(pady=20)

btn_decode = tk.Button(window, text="PNG + メタ → ファイル復元", font=("Arial", 14), command=decode_file)
btn_decode.pack(pady=20)

window.mainloop()
