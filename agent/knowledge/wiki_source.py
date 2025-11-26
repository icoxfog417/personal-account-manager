"""WikiKnowledgeSource - File I/O operations for repository knowledge files."""

from pathlib import Path
from typing import List

import git


class WikiKnowledgeSource:
    """Provides file I/O operations for knowledge files in a repository.
    
    Manages files stored in a specified directory within a repository.
    Handles cloning/updating repository and provides file access operations.
    No search logic - only data access.
    """
    
    def __init__(self, repo_url: str, knowledge_dir: str, local_path: Path) -> None:
        """Initialize WikiKnowledgeSource.
        
        Args:
            repo_url: Repository URL (e.g., 'https://github.com/user/repo')
            knowledge_dir: Directory path within repository containing knowledge files (e.g., 'docs', 'wiki')
            local_path: Local directory to clone/store repository
        """
        self.repo_url = repo_url
        self.knowledge_dir = knowledge_dir
        self.local_path = Path(local_path)
        self.knowledge_path = self.local_path / knowledge_dir
    
    def clone_or_update(self) -> None:
        """Clone repository if not exists, otherwise pull latest changes."""
        if not self.local_path.exists():
            self.local_path.mkdir(parents=True, exist_ok=True)
            git.Repo.clone_from(self.repo_url, self.local_path)
        elif (self.local_path / ".git").exists():
            repo = git.Repo(self.local_path)
            repo.remotes.origin.pull()
    
    def load_file(self, path: Path) -> str:
        """Load file contents by path.
        
        Args:
            path: Path to file relative to knowledge directory or absolute path
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if path.is_absolute():
            file_path = path
        else:
            file_path = self.knowledge_path / path
            
        return file_path.read_text(encoding='utf-8')
    
    def list_files(self) -> List[Path]:
        """List all files in the knowledge directory.
        
        Returns:
            List of file paths relative to knowledge directory
        """
        if not self.knowledge_path.exists():
            return []
            
        files = []
        for file_path in self.knowledge_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(self.knowledge_path)
                files.append(relative_path)
        
        return files
