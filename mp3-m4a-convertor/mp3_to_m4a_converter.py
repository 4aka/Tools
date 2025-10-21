import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

def install_ffmpeg():
    """Завантажує та встановлює ffmpeg"""
    print("Завантаження ffmpeg...")
    
    ffmpeg_dir = Path.cwd() / "ffmpeg"
    ffmpeg_exe = ffmpeg_dir / "bin" / "ffmpeg.exe"
    
    if ffmpeg_exe.exists():
        return str(ffmpeg_exe)
    
    # URL для Windows 64-bit
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = Path.cwd() / "ffmpeg.zip"
    
    try:
        urllib.request.urlretrieve(url, zip_path)
        print("Розпакування...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(Path.cwd())
        
        # Знаходимо розпаковану папку
        extracted = list(Path.cwd().glob("ffmpeg-*"))
        if extracted:
            extracted[0].rename(ffmpeg_dir)
        
        zip_path.unlink()
        print("ffmpeg встановлено")
        return str(ffmpeg_exe)
        
    except Exception as e:
        print(f"Помилка завантаження ffmpeg: {e}")
        return None

def get_ffmpeg_path():
    """Перевіряє наявність ffmpeg або встановлює його"""
    try:
        subprocess.run(["ffmpeg", "-version"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        return "ffmpeg"
    except (subprocess.CalledProcessError, FileNotFoundError):
        local_ffmpeg = Path.cwd() / "ffmpeg" / "bin" / "ffmpeg.exe"
        if local_ffmpeg.exists():
            return str(local_ffmpeg)
        return install_ffmpeg()

def convert_mp3_to_m4a():
    """Конвертує всі MP3 файли в поточній директорії в один M4A файл"""
    
    current_dir = Path.cwd()
    mp3_files = sorted(current_dir.glob("*.mp3"))
    
    if not mp3_files:
        print("MP3 файли не знайдено в поточній директорії")
        return
    
    print(f"Знайдено {len(mp3_files)} MP3 файл(ів)")
    
    # Отримуємо ffmpeg
    ffmpeg = get_ffmpeg_path()
    if not ffmpeg:
        print("Не вдалося встановити ffmpeg")
        return
    
    output_file = current_dir / "output.m4a"
    
    # Один файл - проста конвертація
    if len(mp3_files) == 1:
        print(f"Конвертація: {mp3_files[0].name} → {output_file.name}")
        cmd = [
            ffmpeg, "-i", str(mp3_files[0]),
            "-c:a", "aac", "-b:a", "192k",
            "-y", str(output_file)
        ]
        subprocess.run(cmd, check=True)
    
    # Кілька файлів - об'єднуємо
    else:
        concat_file = current_dir / "concat_list.txt"
        with open(concat_file, "w", encoding="utf-8") as f:
            for mp3 in mp3_files:
                f.write(f"file '{mp3.absolute()}'\n")
        
        print(f"Об'єднання {len(mp3_files)} файлів в {output_file.name}")
        cmd = [
            ffmpeg, "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c:a", "aac", "-b:a", "192k",
            "-y", str(output_file)
        ]
        subprocess.run(cmd, check=True)
        concat_file.unlink()
    
    print(f"Готово! Створено: {output_file.name}")

if __name__ == "__main__":
    try:
        convert_mp3_to_m4a()
    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        input("Натисніть Enter для виходу...")
