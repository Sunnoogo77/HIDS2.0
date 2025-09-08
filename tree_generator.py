import os

def concatenate_backend_files(files_to_concatenate, output_filename):
    """
    Concatenate the content of multiple files into a single output file.

    Args:
        files_to_concatenate (list): A list of file paths to read.
        output_filename (str): The name of the file to write the content to.
    """
    print(f"Début de la concaténation des fichiers dans '{output_filename}'...")

    # We make sure the output file is writable
    try:
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            for file_path in files_to_concatenate:
                # Add a clear header for each file
                outfile.write(f"---------- START OF FILE: {file_path} ----------\n\n")
                
                # Open and read the content of the current file
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        print(f"  - Fichier lu avec succès : {file_path}")
                except FileNotFoundError:
                    # Handle case where a file is not found
                    outfile.write(f"Error: The file {file_path} was not found.\n")
                    print(f"  - ERREUR : Fichier non trouvé : {file_path}")
                except Exception as e:
                    # Handle other potential reading errors
                    outfile.write(f"Error reading file {file_path}: {e}\n")
                    print(f"  - ERREUR de lecture sur le fichier {file_path} : {e}")

                # Add a clear footer for each file
                outfile.write(f"\n---------- END OF FILE: {file_path} ----------\n\n\n")

    except Exception as e:
        print(f"\nERREUR FATALE : Impossible d'écrire dans le fichier de sortie '{output_filename}': {e}")
        return

    print(f"\nProcessus de concaténation terminé. Le contenu est dans '{output_filename}'.")

# List of files to concatenate, relative to the project root
files_to_process = [
'backend/app/api/auth.py',
'backend/app/core/security.py',
'backend/app/services/auth_service.py',
'backend/app/models/user.py',
'backend/app/db/models.py',
'backend/app/core/config.py',
'backend/app/db/session.py',
'backend/app/main.py',
'backend/app/api/users.py',
'backend/app/api/configs.py',
'backend/app/api/logs.py',
'backend/app/api/backend_logs.py',
'backend/app/api/hids_logs.py',
'backend/app/api/engine.py',
'backend/app/api/monitoring.py',
'backend/app/services/user_service.py',
'hids-web/src/context/AuthProvider.jsx',
'hids-web/src/lib/api.js',
'hids-web/src/pages/Settings.jsx',
'inventaire_routes.md',

]

# Name of the output file
output_file = 'backend_to_review.txt'

# Run the function to concatenate the files
concatenate_backend_files(files_to_process, output_file)
