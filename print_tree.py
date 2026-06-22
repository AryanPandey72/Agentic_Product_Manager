import os

def generate_clean_tree(startpath, exclude_dirs):
    for root, dirs, files in os.walk(startpath):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        print(f"{indent}├── {os.path.basename(root)}/")
        
        subindent = '│   ' * (level + 1)
        for f in files:
            # Ignore hidden files and python compiled files
            if not f.startswith('.') and not f.endswith('.pyc'):
                print(f"{subindent}├── {f}")

# Add any other folders you want to hide in this list
exclude = ['.git', 'venv', 'env', '.venv', '__pycache__', 'node_modules']
generate_clean_tree('.', exclude)