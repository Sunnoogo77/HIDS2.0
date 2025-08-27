import os

def generate_tree(path, prefix=""):
    """
    Génère une arborescence de fichiers et dossiers, en ignorant les répertoires communs de dépendances.
    """
    # Liste des dossiers à ignorer pour éviter de lister les dépendances
    ignored_dirs = ['__pycache__', '.git', 'venv', 'node_modules', 'dist', 'build']
    output = []
    
    entries = sorted(os.listdir(path))
    
    for i, entry in enumerate(entries):
        if entry in ignored_dirs:
            continue
            
        is_last = i == len(entries) - 1
        
        # Le connecteur pour l'arborescence
        connector = "└── " if is_last else "├── "
        output.append(f"{prefix}{connector}{entry}")
        
        # S'il s'agit d'un répertoire, faire un appel récursif
        if os.path.isdir(os.path.join(path, entry)):
            new_prefix = prefix + ("    " if is_last else "│   ")
            output.extend(generate_tree(os.path.join(path, entry), new_prefix))
            
    return output

# Remplacez '.' par le chemin de votre projet si nécessaire.
project_path = "."
tree_output = generate_tree(project_path)
project_name = os.path.basename(os.path.abspath(project_path))

# Écrire la sortie dans un fichier
output_filename = "tree2.txt"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(project_name + "\n")
    f.write("\n".join(tree_output))

print(f"L'arborescence a été générée avec succès dans {output_filename}")
