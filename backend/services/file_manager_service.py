import os
import shutil
from typing import List, Dict, Any

class FileManagerService:
    def __init__(self, base_dir: str = None):
        if base_dir:
            self.base_dir = os.path.abspath(base_dir)
        else:
            # Default to the parent folder of backend/ (the project root directory)
            self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            
        # Ensure the base directory exists
        os.makedirs(self.base_dir, exist_ok=True)

    def _safe_path(self, path: str) -> str:
        """Resolves target path and strictly verifies it remains inside the safe base directory."""
        # Convert to absolute path
        if os.path.isabs(path):
            target_abs = os.path.abspath(path)
        else:
            target_abs = os.path.abspath(os.path.join(self.base_dir, path))

        # Check for path traversal using commonpath
        try:
            common = os.path.commonpath([self.base_dir, target_abs])
            if common != self.base_dir:
                raise PermissionError(f"Access Denied: Path '{path}' is outside the authorized sandbox directory.")
        except Exception as e:
            if isinstance(e, PermissionError):
                raise e
            raise PermissionError("Access Denied: Path is invalid or insecure.")
            
        return target_abs

    def list_directory(self, relative_path: str = ".") -> List[Dict[str, Any]]:
        """Lists directory contents securely, including size and type metadata."""
        target_dir = self._safe_path(relative_path)
        if not os.path.isdir(target_dir):
            raise NotADirectoryError(f"Path is not a directory: {relative_path}")

        items = []
        for name in os.listdir(target_dir):
            full_path = os.path.join(target_dir, name)
            is_dir = os.path.isdir(full_path)
            stats = os.stat(full_path)
            
            # Use relative path from sandbox base for return info to avoid exposing system paths
            rel_path = os.path.relpath(full_path, self.base_dir)
            
            items.append({
                "name": name,
                "relative_path": rel_path,
                "type": "directory" if is_dir else "file",
                "size_bytes": stats.st_size if not is_dir else None,
                "modified": stats.st_mtime
            })
        return items

    def read_text_file(self, file_path: str) -> str:
        """Reads content of a text file securely."""
        target_file = self._safe_path(file_path)
        if not os.path.isfile(target_file):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def write_text_file(self, file_path: str, content: str) -> str:
        """Writes content to a file securely, automatically creating parent subfolders."""
        target_file = self._safe_path(file_path)
        
        # Ensure parent directories are safe and exist
        parent_dir = os.path.dirname(target_file)
        os.makedirs(parent_dir, exist_ok=True)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        return os.path.relpath(target_file, self.base_dir)

    def copy_item(self, source_path: str, dest_path: str) -> str:
        """Copies a file or folder securely within the sandbox."""
        safe_src = self._safe_path(source_path)
        safe_dst = self._safe_path(dest_path)

        if not os.path.exists(safe_src):
            raise FileNotFoundError(f"Source not found: {source_path}")

        # If dest is a directory that exists, append src filename
        if os.path.isdir(safe_dst):
            safe_dst = os.path.join(safe_dst, os.path.basename(safe_src))

        # Check dst path again after append
        safe_dst = self._safe_path(safe_dst)

        if os.path.isdir(safe_src):
            shutil.copytree(safe_src, safe_dst, dirs_exist_ok=True)
        else:
            # Ensure parent of destination exists
            os.makedirs(os.path.dirname(safe_dst), exist_ok=True)
            shutil.copy2(safe_src, safe_dst)
            
        return os.path.relpath(safe_dst, self.base_dir)

    def move_item(self, source_path: str, dest_path: str) -> str:
        """Moves a file or folder securely within the sandbox."""
        safe_src = self._safe_path(source_path)
        safe_dst = self._safe_path(dest_path)

        if not os.path.exists(safe_src):
            raise FileNotFoundError(f"Source not found: {source_path}")

        # Ensure parent of destination exists
        os.makedirs(os.path.dirname(safe_dst), exist_ok=True)
        
        shutil.move(safe_src, safe_dst)
        return os.path.relpath(safe_dst, self.base_dir)

    def delete_item(self, target_path: str) -> Dict[str, str]:
        """Deletes a file or directory recursively and securely."""
        safe_target = self._safe_path(target_path)

        if not os.path.exists(safe_target):
            raise FileNotFoundError(f"Target not found: {target_path}")

        # Protect the sandbox root from deletion
        if safe_target == self.base_dir:
            raise PermissionError("Access Denied: Cannot delete the sandbox root directory.")

        if os.path.isdir(safe_target):
            shutil.rmtree(safe_target)
            item_type = "directory"
        else:
            os.remove(safe_target)
            item_type = "file"
            
        return {
            "status": "success",
            "type": item_type,
            "path": os.path.relpath(safe_target, self.base_dir)
        }
