import os

def search_and_replace_fragment():
    """
    Ищет и заменяет фрагмент в именах файлов и директорий
    """
    # НАСТРОЙКИ (измените здесь нужные значения)
    old_fragment = "1_task_jun"      # Что ищем
    new_fragment = "task"     # На что заменяем
    root_dir = '.'                  # Текущая папка
    
    if not old_fragment:
        print("Ошибка: Фрагмент для поиска не может быть пустым!")
        return
    
    if old_fragment == new_fragment:
        print("Старый и новый фрагменты совпадают. Замена не требуется.")
        return
    
    print(f"\n🔍 Поиск '{old_fragment}' → замена на '{new_fragment}'")
    print(f"📂 Директория: {os.path.abspath(root_dir)}\n")
    
    # Собираем элементы для переименования
    items_to_rename = []
    
    # Важно: topdown=False для корректной обработки вложенных папок
    for root, dirs, files in os.walk(root_dir, topdown=False):
        # Проверяем папки
        for dirname in dirs:
            if old_fragment in dirname:
                old_path = os.path.join(root, dirname)
                new_name = dirname.replace(old_fragment, new_fragment)
                new_path = os.path.join(root, new_name)
                items_to_rename.append((old_path, new_path, dirname, new_name))
        
        # Проверяем файлы
        for filename in files:
            if old_fragment in filename:
                old_path = os.path.join(root, filename)
                new_name = filename.replace(old_fragment, new_fragment)
                new_path = os.path.join(root, new_name)
                items_to_rename.append((old_path, new_path, filename, new_name))
    
    if not items_to_rename:
        print(f"❌ Не найдено элементов с фрагментом '{old_fragment}'")
        return
    
    # Показываем что будет изменено
    print(f"✅ Найдено элементов для замены: {len(items_to_rename)}\n")
    print("Планируемые изменения:")
    print("-" * 60)
    
    for old_path, new_path, old_name, new_name in items_to_rename:
        old_highlighted = old_name.replace(old_fragment, f"\033[91m{old_fragment}\033[0m")
        new_highlighted = new_name.replace(new_fragment, f"\033[92m{new_fragment}\033[0m")
        print(f"  {old_highlighted} → {new_highlighted}")
    
    # Подтверждение
    print("-" * 60)
    confirm = input(f"\n⚠️  Выполнить переименование {len(items_to_rename)} элементов? (y/N): ")
    
    if confirm.lower() not in ['y', 'yes', 'да']:
        print("❌ Операция отменена")
        return
    
    # Выполняем переименование
    print("\n🔄 Выполняется переименование...")
    success = 0
    
    for old_path, new_path, old_name, new_name in items_to_rename:
        try:
            os.rename(old_path, new_path)
            print(f"  ✅ {old_name} → {new_name}")
            success += 1
        except Exception as e:
            print(f"  ❌ Ошибка при {old_name}: {e}")
    
    print(f"\n✅ Успешно переименовано: {success} из {len(items_to_rename)}")
    print("=" * 60)

if __name__ == "__main__":
    search_and_replace_fragment()