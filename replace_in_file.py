import os

# НАСТРОЙКИ
old_text = '1_task_jun'
new_text = 'task'
root_dir = '.'

current_script = os.path.abspath(__file__)
changed = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    if '.git' in dirnames:
        dirnames.remove('.git')
    
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        
        if os.path.abspath(filepath) == current_script:
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_text in content:
                new_content = content.replace(old_text, new_text)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                changed += 1
                print(f"✅ {filepath}")
        except:
            pass

print(f"\n✅ Изменено файлов: {changed}")