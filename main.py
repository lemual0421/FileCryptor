import os
import time
from cryptography.fernet import Fernet
from art import text2art
import random as rd
from simple_term_menu import TerminalMenu
from tqdm import tqdm
import sys

def generate_key():
    return Fernet.generate_key()

def save_key(key, key_path):
    with open(key_path, "wb") as f:
        f.write(key)

def load_key(key_path):
    return open(key_path, "rb").read()

def encrypt_file(file_path, key, save_path):
    fernet = Fernet(key)
    
    with open(file_path, "rb") as f:
        original_data = f.read()

    with tqdm(total=100, desc="Шифрование", ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        encrypted_data = fernet.encrypt(original_data)
        for i in range(100):
            time.sleep(0.015)
            pbar.update(1)

    with open(save_path, "wb") as f:
        f.write(encrypted_data)

def decrypt_file(file_path, key, save_path):
    fernet = Fernet(key)
    
    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    with tqdm(total=100, desc="Дешифрование", ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        decrypted_data = fernet.decrypt(encrypted_data)
        for i in range(100):
            time.sleep(0.015)
            pbar.update(1)

    with open(save_path, "wb") as f:
        f.write(decrypted_data)

def select_file(start_dir="."):
    current_dir = os.path.abspath(start_dir)
    while True:
        entries = []
        if current_dir != os.path.abspath(os.sep):
            entries.append("..")
        entries.extend(sorted(os.listdir(current_dir)))
        
        menu = TerminalMenu(
            entries,
            title=f"Текущая директория: {current_dir}\n",
            clear_screen=True,
            show_search_hint=True,
            status_bar="[Enter] Выбрать файл [q] Выход\n"
        )
        choice_index = menu.show()
        if choice_index is None:
            return None
        choice = entries[choice_index]
        
        if choice == "..":
            current_dir = os.path.dirname(current_dir)
        else:
            selected_path = os.path.join(current_dir, choice)
            if os.path.isdir(selected_path):
                current_dir = selected_path
            else:
                return selected_path

def select_directory(start_dir="."):
    current_dir = os.path.abspath(start_dir)
    while True:
        entries = []
        if current_dir != os.path.abspath(os.sep):
            entries.append("..")
        entries.append("[ПОДТВЕРДИТЬ ВЫБОР]")
        entries.extend(sorted(os.listdir(current_dir)))
        
        menu = TerminalMenu(
            entries,
            title=f"Выберите директорию: {current_dir}",
            clear_screen=True,
            show_search_hint=True,
            status_bar="[Enter] Выбрать папку [q] Выход"
        )
        choice_index = menu.show()
        if choice_index is None:
            return None
        choice = entries[choice_index]
        
        if choice == "..":
            current_dir = os.path.dirname(current_dir)
        elif choice == "[ПОДТВЕРДИТЬ ВЫБОР]":
            return current_dir
        else:
            selected_path = os.path.join(current_dir, choice)
            if os.path.isdir(selected_path):
                current_dir = selected_path

def loading_screen():
    print(text2art("shkoldin"))
    with tqdm(total=100, desc="Загрузка", ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        for _ in range(100):
            time.sleep(0.01)
            pbar.update(1)

def main_menu():
    menu_items = [
        "[1] Зашифровать файл",
        "[2] Расшифровать файл",
        "[3] Обработать директорию",
        "[4] Выход"
    ]
    menu = TerminalMenu(
        menu_items,
        title="ГЛАВНОЕ МЕНЮ",
        clear_screen=True,
        cycle_cursor=True,
        status_bar="[↑↓] Навигация [Enter] Выбор"
    )
    return menu.show()

def handle_encryption(key_path):
    file_path = select_file()
    if not file_path:
        return
    
    save_dir = select_directory()
    if not save_dir:
        return
    
    file_name = os.path.basename(file_path) + ".enc"
    new_name = input(f"Имя файла (по умолчанию {file_name}): ") or file_name
    save_path = os.path.join(save_dir, new_name)
    
    try:
        key = load_key(key_path)
        encrypt_file(file_path, key, save_path)
        print("Файл успешно зашифрован!")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
    input("\nНажмите Enter для продолжения...")

def handle_decryption(key_path):
    file_path = select_file()
    if not file_path:
        return
    
    save_dir = select_directory()
    if not save_dir:
        return
    
    default_name = os.path.basename(file_path).replace(".enc", "")
    new_name = input(f"Имя файла (по умолчанию {default_name}): ") or default_name
    save_path = os.path.join(save_dir, new_name)
    
    try:
        key = load_key(key_path)
        decrypt_file(file_path, key, save_path)
        print("Файл успешно расшифрован!")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
    input("\nНажмите Enter для продолжения...")

def handle_directory_processing(key_path):
    dir_path = select_directory()
    if not dir_path:
        return
    
    action_menu = TerminalMenu(
        ["Зашифровать все файлы", "Расшифровать все файлы"],
        title="Выберите действие для директории:",
        clear_screen=True
    )
    action_idx = action_menu.show()
    if action_idx is None:
        return
    
    try:
        key = load_key(key_path)
    except Exception as e:
        print(f"Ошибка загрузки ключа: {e}")
        input("\nНажмите Enter для продолжения...")
        return
    
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    
    for file in files:
        file_path = os.path.join(dir_path, file)
        if action_idx == 0:
            save_name = file + ".enc"
            save_path = os.path.join(dir_path, save_name)
            if os.path.exists(save_path):
                print(f"Файл {save_name} уже существует, пропускается.")
                continue
            try:
                encrypt_file(file_path, key, save_path)
                print(f"Зашифрован: {file}")
            except Exception as e:
                print(f"Ошибка шифрования {file}: {e}")
        elif action_idx == 1:
            if not file.endswith(".enc"):
                print(f"Файл {file} не имеет расширения .enc, пропускается.")
                continue
            save_name = file[:-4]
            save_path = os.path.join(dir_path, save_name)
            if os.path.exists(save_path):
                print(f"Файл {save_name} уже существует, пропускается.")
                continue
            try:
                decrypt_file(file_path, key, save_path)
                print(f"Расшифрован: {file}")
            except Exception as e:
                print(f"Ошибка дешифрования {file}: {e}")
    
    print("Обработка директории завершена.")
    input("\nНажмите Enter для продолжения...")

def main():
    print("\033[?25l")
    loading_screen()
    
    config_path = os.path.expanduser("~/.filecryptor.cfg")
    key_path = None
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            key_path = f.read().strip()
    
    if not key_path or not os.path.exists(key_path):
        print("Создание нового ключа...")
        key_dir = select_directory()
        if not key_dir:
            print("Отменено пользователем")
            return
        
        key_name = input("Имя ключевого файла (secret.key): ") or "secret.key"
        key_path = os.path.join(key_dir, key_name)
        save_key(generate_key(), key_path)
        
        with open(config_path, "w") as f:
            f.write(key_path)
        print(f"Ключ сохранен в {key_path}")
        time.sleep(1)
    
    while True:
        try:
            choice = main_menu()
            if choice == 0:
                handle_encryption(key_path)
            elif choice == 1:
                handle_decryption(key_path)
            elif choice == 2:
                handle_directory_processing(key_path)
            elif choice == 3 or choice is None:
                print("\033[?25h")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\033[?25h")
            sys.exit(0)
        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
