from janome.tokenizer import Tokenizer
import re
from pykakasi import kakasi
from bs4 import BeautifulSoup
import os
import shutil
import zipfile

output_folder = "C:\\Kata\\kernel\\temp"
output_html_path = 'C:\\Kata\\kernel\\html'

def extract_and_save_html_from_epub(epub_file_path, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 解压 EPUB 文件
    with zipfile.ZipFile(epub_file_path, 'r') as epub_zip:
        # 获取所有文件列表
        file_list = epub_zip.namelist()

        # 提取 HTML 和 XHTML 文件
        for file_name in file_list:
            if file_name.lower().endswith(('.html', '.xhtml')):
                # 读取文件内容
                content = epub_zip.read(file_name).decode('utf-8')

                # 使用 BeautifulSoup 移除可能存在的不必要标签
                soup = BeautifulSoup(content, 'html.parser')
                clean_content = soup.prettify()

                # 构建输出文件路径
                output_file_path = os.path.join(output_folder, os.path.basename(file_name))

                # 写入内容到文件
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(clean_content)

                print(f"Extracted: {output_file_path}")

def replace_files_in_epub(epub_path, source_folder, output_epub_path):
    # Create a temporary directory
    temp_dir = "temp_epub"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Extract the original EPUB file to the temporary directory
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Delete the 'text' directory in the temporary directory
        text_dir = os.path.join(temp_dir, 'text')
        if os.path.exists(text_dir):
            shutil.rmtree(text_dir)

        # Copy the entire source_folder to the temporary directory with the name 'text'
        shutil.copytree(source_folder, text_dir)

        # Create a new EPUB file
        with zipfile.ZipFile(output_epub_path, 'w') as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_dir))

    finally:
        # Delete the temporary directory
        shutil.rmtree(temp_dir)

def empty_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)

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

def process_japanese_text(text,flag):
    # print(text)
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(text)
    result = ""
    for token in tokens:
        word = token.surface
        # print(word)
        if word in ['<', 'ruby', '>', '</','rt','></','><']:
            result += f"{word}"
        elif word == "rb":
            flag = not flag
            result += f"{word}"
        elif flag and is_first_character_kanji(word):
            result += convert_to_gotou(word)
        else:
            result += f"{word}"
    return result


def create_new_html(file_path, output_html_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html5lib')
    
    paragraphs = soup.body.find_all('p')
    flag = True
    for paragraph in paragraphs:
        processed_text = process_japanese_text(paragraph.prettify(),flag)
        paragraph.string = ''
        paragraph.append(BeautifulSoup(processed_text, 'html5lib'))
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
