# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 13:21:13 2024

@author: 28187
"""
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 12:48:07 2024

@author: 28187
"""
from janome.tokenizer import Tokenizer
import re
from pykakasi import kakasi
from bs4 import BeautifulSoup
import os
import shutil
import zipfile
from concurrent.futures import ProcessPoolExecutor

output_folder = "C:\\Kata\\kernel\\temp"
output_html_path = 'C:\\Kata\\kernel\\html'

def empty_folder(folder_path):
    shutil.rmtree(folder_path, ignore_errors=True)
    os.makedirs(folder_path, exist_ok=True)

def convert_to_gotou(word):
    conv = kakasi()
    result = conv.convert(word)
    result_with_brackets = ""

    for item in result:
        result_with_brackets += "<ruby><rb>{}</rb><rt>{}</rt></ruby>".format(item['orig'], item['hira'])

    return result_with_brackets

def is_first_character_kanji(word):
    kanji_pattern = re.compile(r'^[\u4e00-\u9faf]')
    return bool(re.match(kanji_pattern, word[0]))

def process_japanese_text_with_conversion(text, flag):
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(text)
    result = ""

    for token in tokens:
        word = token.surface
        if word in ['<', 'ruby', '>', '</', 'rt', '></', '><']:
            result += f"{word}"
        elif word == "rb":
            flag = not flag
            result += f"{word}"
        elif flag and is_first_character_kanji(word):
            conv = kakasi()
            converted_word = conv.convert(word)[0]
            result += f"<ruby><rb>{converted_word['orig']}</rb><rt>{converted_word['hira']}</rt></ruby>"
        else:
            result += f"{word}"

    return result

def extract_and_save_html_from_epub(epub_file_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with zipfile.ZipFile(epub_file_path, 'r') as epub_zip:
        file_list = epub_zip.namelist()

        for file_name in file_list:
            if file_name.lower().endswith(('.html', '.xhtml')):
                content = epub_zip.read(file_name).decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                clean_content = soup.prettify()

                output_file_path = os.path.join(output_folder, os.path.basename(file_name))

                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(clean_content)

                print(f"Extracted: {output_file_path}")

def create_new_html(file_path, output_html_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html5lib')

    paragraphs = soup.body.find_all('p')
    flag = True
    for paragraph in paragraphs:
        processed_text = process_japanese_text_with_conversion(paragraph.prettify(), flag)
        paragraph.string = ''
        paragraph.append(BeautifulSoup(processed_text, 'html5lib'))
    filename = os.path.basename(file_path)
    output_new_html_path = os.path.join(output_html_path, filename)
    with open(output_new_html_path, 'wb') as new_file:
        new_file.write(str(soup).encode('utf-8'))

def replace_files_in_epub(epub_path, source_folder, output_epub_path):
    temp_dir = "temp_epub"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        shutil.rmtree(os.path.join(temp_dir, 'text'), ignore_errors=True)
        shutil.copytree(source_folder, os.path.join(temp_dir, 'text'))

        with zipfile.ZipFile(output_epub_path, 'w') as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_dir))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def process_single_html_file(file_name):
    file_path = os.path.join(output_folder, file_name)
    create_new_html(file_path, output_html_path)
    print(f"Working on {file_name}...")

def process_all_files_in_folder_parallel(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    with ProcessPoolExecutor() as executor:
        executor.map(process_single_html_file, files)

def process_epub(epub_file_path):
    print("Working...")
    empty_folder(output_folder)
    empty_folder(output_html_path)
    extract_and_save_html_from_epub(epub_file_path, output_folder)
    process_all_files_in_folder_parallel(output_folder)
    final_output_path = os.path.join(os.path.dirname(epub_file_path), "new_" + os.path.basename(epub_file_path))
    replace_files_in_epub(epub_file_path, output_html_path, final_output_path)

def process_file(epub_file_path):
    if os.path.splitext(epub_file_path.lower())[1] == '.epub':
        try:
            process_epub(epub_file_path)
        except FileNotFoundError:
            print(f"'{epub_file_path}' NOT FOUND.")
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            print("COMPLETED")
    else:
        print("NOT EPUB FILE!")

if __name__ == "__main__":
    file_path = input("INPUT FILE PATH: ")
    process_file(file_path)
    print("Completed! Press any button.")
    input()
