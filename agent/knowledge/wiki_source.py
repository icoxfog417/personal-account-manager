"""WikiKnowledgeSource - File I/O operations for GitHub wiki repository."""

from pathlib import Path
from typing import List

import git


class WikiKnowledgeSource:
    """Provides file I/O operations for GitHub wiki repository.
    
    Handles cloning/updating GitHub wiki repository and provides
    file access operations. No search logic - only data access.
    """
    
    def __init__(self, repo_url: str, local_path: Path) -> None:
        """Initialize WikiKnowledgeSource.
        
        Args:
            repo_url: GitHub wiki repository URL
            local_path: Local directory to clone/store wiki
        """
        self.repo_url = repo_url
        self.local_path = Path(local_path)
    
    def clone_or_update(self) -> None:
        """Clone repository if not exists, otherwise pull latest changes."""
        # Skip if directory exists with markdown/txt files but no .git (bundled data)
        if self.local_path.exists() and not (self.local_path / ".git").exists():
            data_files = list(self.local_path.glob("*.md")) + list(self.local_path.glob("*.txt"))
            if data_files:
                return  # Bundled data, no need to clone
        
        if not self.local_path.exists():
            # Clone if directory doesn't exist
            self.local_path.mkdir(parents=True, exist_ok=True)
            git.Repo.clone_from(self.repo_url, self.local_path)
        elif (self.local_path / ".git").exists():
            # Pull if it's a git repository
            repo = git.Repo(self.local_path)
            repo.remotes.origin.pull()
        else:
            # Directory exists but not a git repo - clone fresh
            import shutil
            shutil.rmtree(self.local_path)
            self.local_path.mkdir(parents=True, exist_ok=True)
            git.Repo.clone_from(self.repo_url, self.local_path)
    
    def load_file(self, path: Path) -> str:
        """Load file contents by path.
        
        Args:
            path: Path to file relative to wiki root or absolute path
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if path.is_absolute():
            file_path = path
        else:
            file_path = self.local_path / path
            
        return file_path.read_text(encoding='utf-8')
    
    def list_files(self) -> List[Path]:
        """List all files in the wiki repository.
        
        Returns:
            List of file paths relative to wiki root
        """
        if not self.local_path.exists():
            print(f"DEBUG: wiki path does not exist: {self.local_path}")
            return []
            
        files = []
        for file_path in self.local_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Return path relative to wiki root
                relative_path = file_path.relative_to(self.local_path)
                files.append(relative_path)
        
        print(f"DEBUG: Found {len(files)} files in {self.local_path}")
        for f in files[:10]:  # Print first 10
            print(f"DEBUG: - {f}")
        
        return files
