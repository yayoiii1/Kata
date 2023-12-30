from janome.tokenizer import Tokenizer
import re
from pykakasi import kakasi
from bs4 import BeautifulSoup
import os
import shutil
from ebooklib import epub

output_folder = "C:\\Kata\\kernel\\temp"
output_html_path = 'C:\\Kata\\kernel\\html'

def extract_and_save_html_from_epub(epub_path, output_folder):
    book = epub.read_epub(epub_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for index, item in enumerate(book.items):
        if item.get_type() == 9:
            content = item.get_content()
            filename = os.path.basename(item.get_name())
            output_path = os.path.join(output_folder, filename)
            with open(output_path, 'wb') as file:
                file.write(content)
            print(f"Saved {filename} to {output_folder}")

def replace_files_in_epub(epub_path, folder_a_path, output_epub_path):
    book = epub.read_epub(epub_path)
    for item in book.items:
        if item.get_type() == 9:
            file_name = os.path.basename(item.file_name)
            file_a_path = os.path.join(folder_a_path, file_name)
            if os.path.exists(file_a_path):
                with open(file_a_path, 'rb') as file_a:
                    file_a_content = file_a.read()
                    item.content = file_a_content
    epub.write_epub(output_epub_path, book)

def empty_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)

def convert_to_gotou(word):
    conv = kakasi()
    conv.setMode("J", "H")
    result = conv.getConverter().do(word)
    result_with_brackets = f"<ruby><rb>{word}</rb><rt>{result}</rt></ruby>"
    return result_with_brackets

def is_first_character_kanji(word):
    kanji_pattern = re.compile(r'^[\u4e00-\u9faf]')
    return bool(re.match(kanji_pattern, word[0]))

def process_japanese_text(text):
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(text)
    result = ""
    for token in tokens:
        word = token.surface
        if is_first_character_kanji(word):
            result += convert_to_gotou(word)
        else:
            result += f"{word}"
    return result

def create_new_html(file_path, output_html_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.body.find_all('p')
    for paragraph in paragraphs:
        processed_text = process_japanese_text(paragraph.get_text(strip=True))
        paragraph.string = ''
        paragraph.append(BeautifulSoup(processed_text, 'html.parser'))
    filename = os.path.basename(file_path)
    output_new_html_path = os.path.join(output_html_path, filename)
    with open(output_new_html_path, 'wb') as new_file:
        new_file.write(str(soup).encode('utf-8'))

def process_all_files_in_folder(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        create_new_html(file_path, output_html_path)
        print("working\r")

def process_epub(epub_file_path):
    print("working\r")
    empty_folder(output_folder)
    empty_folder(output_html_path)
    extract_and_save_html_from_epub(epub_file_path, output_folder)
    process_all_files_in_folder(output_folder)
    final_output_path = os.path.join(os.path.dirname(epub_file_path), "new_" + os.path.basename(epub_file_path))
    replace_files_in_epub(epub_file_path, output_html_path, final_output_path)

def process_file(epub_file_path):
    if epub_file_path.lower().endswith('.epub'):
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

file_path = input("INPUT FILE PATH: ")
process_file(file_path)
print("Completed! Press any botton.")
input()
