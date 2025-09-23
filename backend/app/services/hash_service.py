# import hashlib
# import os
# import psutil
# from datetime import datetime
# from typing import Optional, Tuple

# def calculate_file_hash(file_path: str) -> Optional[str]:
#     """Calcule le SHA256 d'un fichier"""
#     try:
#         if not os.path.exists(file_path):
#             return None
            
#         hasher = hashlib.sha256()
#         with open(file_path, 'rb') as f:
#             for chunk in iter(lambda: f.read(4096), b""):
#                 hasher.update(chunk)
#         return hasher.hexdigest()
#     except Exception:
#         return None

# def calculate_folder_fingerprint(folder_path: str) -> Optional[Tuple[str, int]]:
#     """Calcule une empreinte du dossier (hash + nombre de fichiers)"""
#     try:
#         if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
#             return None
            
#         file_hashes = []
#         file_count = 0
        
#         for root, dirs, files in os.walk(folder_path):
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 file_hash = calculate_file_hash(file_path)
#                 if file_hash:
#                     file_hashes.append(file_hash)
#                 file_count += 1
        
#         if not file_hashes:
#             return ("empty_folder", 0)
            
#         # Créer un hash unique pour le dossier basé sur tous les fichiers
#         combined_hash = hashlib.sha256(''.join(sorted(file_hashes)).encode()).hexdigest()
#         return (combined_hash, file_count)
#     except Exception:
#         return None

# def check_ip_activity(ip: str) -> dict:
#     """Vérifie l'activité d'une IP via les connexions réseau"""
#     try:
#         connections = psutil.net_connections()
#         ip_connections = []
        
#         for conn in connections:
#             if conn.raddr and conn.raddr.ip == ip:
#                 ip_connections.append({
#                     'status': conn.status,
#                     'local_port': conn.laddr.port,
#                     'remote_port': conn.raddr.port
#                 })
        
#         return {
#             'ip': ip,
#             'is_active': len(ip_connections) > 0,
#             'connections': ip_connections,
#             'timestamp': datetime.utcnow().isoformat()
#         }
#     except Exception as e:
#         return {'ip': ip, 'is_active': False, 'error': str(e)}

import hashlib
import os
import subprocess
from datetime import datetime
from typing import Optional, Tuple

def calculate_file_hash(file_path: str) -> Optional[str]:
    """Calcule le SHA256 d'un fichier"""
    try:
        if not os.path.exists(file_path):
            return None
            
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def calculate_folder_fingerprint(folder_path: str) -> Optional[Tuple[str, int]]:
    """Calcule une empreinte du dossier (hash + nombre de fichiers)"""
    try:
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return None
            
        file_hashes = []
        file_count = 0
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = calculate_file_hash(file_path)
                if file_hash:
                    file_hashes.append(file_hash)
                file_count += 1
        
        if not file_hashes:
            return ("empty_folder", 0)
            
        # Créer un hash unique pour le dossier basé sur tous les fichiers
        combined_hash = hashlib.sha256(''.join(sorted(file_hashes)).encode()).hexdigest()
        return (combined_hash, file_count)
    except Exception:
        return None

def check_ip_activity(ip: str) -> dict:
    """
    Surveillance IP alternative sans psutil
    Utilise les commandes système pour vérifier les connexions
    """
    try:
        # Méthode 1: Utiliser netstat (Linux/Windows)
        try:
            result = subprocess.run(
                ["netstat", "-an"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            is_connected = ip in result.stdout
            return {
                'ip': ip,
                'is_active': is_connected,
                'method': 'netstat',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception:
            pass
            
        # Méthode 2: Utiliser ping comme fallback
        try:
            # Sur Windows
            param = "-n" if os.name == "nt" else "-c"
            result = subprocess.run(
                ["ping", param, "1", ip], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            is_connected = result.returncode == 0
            return {
                'ip': ip,
                'is_active': is_connected,
                'method': 'ping',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception:
            pass
            
        # Fallback si tout échoue
        return {
            'ip': ip,
            'is_active': False,
            'method': 'fallback',
            'error': 'Unable to determine IP status',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'ip': ip, 
            'is_active': False, 
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }