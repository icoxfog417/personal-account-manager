"""Tool definitions for the AWS Support Agent."""


from strands import tool

from knowledge.wiki_source import WikiKnowledgeSource


class SupportAgentTools:
    """Tools for the AWS Support Agent.
    
    Centralizes all search and retrieve logic for knowledge sources.
    WikiKnowledgeSource provides I/O operations only.
    """
    
    def __init__(self, wiki_source: WikiKnowledgeSource) -> None:
        """Initialize tools with knowledge source.
        
        Args:
            wiki_source: WikiKnowledgeSource instance for file I/O
        """
        self.wiki_source = wiki_source
    
    @tool
    def search_wiki(self, query: str) -> str:
        """Search through wiki files for relevant content.
        
        Args:
            query: Search query to find relevant information
            
        Returns:
            Relevant content from wiki files
        """
        try:
            # Ensure wiki is up to date
            self.wiki_source.clone_or_update()
            
            # Get all files from wiki
            files = self.wiki_source.list_files()
            
            # Simple keyword-based search (Phase 1 implementation)
            query_lower = query.lower()
            relevant_content = []
            
            for file_path in files:
                # Only search markdown files for now
                if file_path.suffix.lower() in ['.md', '.txt']:
                    try:
                        content = self.wiki_source.load_file(file_path)
                        content_lower = content.lower()
                        
                        # Check if query keywords appear in content
                        if any(keyword.strip() in content_lower for keyword in query_lower.split()):
                            # Add file with some context
                            relevant_content.append(f"## From {file_path}\n\n{content[:2000]}...")
                            
                            # Limit results to avoid overwhelming the context
                            if len(relevant_content) >= 10:
                                break
                                
                    except Exception:
                        continue  # Skip files that can't be read
            
            if relevant_content:
                return "\n\n".join(relevant_content)
            else:
                return f"No relevant content found for query: {query}"
                
        except Exception as e:
            return f"Error searching wiki: {str(e)}"
    
    @tool
    def list_wiki_files(self) -> str:
        """List available files in the wiki repository.
        
        Returns:
            List of available files for reference
        """
        try:
            # Ensure wiki is up to date
            self.wiki_source.clone_or_update()
            
            files = self.wiki_source.list_files()
            
            # Group files by type
            markdown_files = [f for f in files if f.suffix.lower() == '.md']
            other_files = [f for f in files if f.suffix.lower() != '.md']
            
            result = "Available wiki files:\n\n"
            
            if markdown_files:
                result += "Markdown files:\n"
                for file_path in sorted(markdown_files):
                    result += f"- {file_path}\n"
            
            if other_files:
                result += "\nOther files:\n"
                for file_path in sorted(other_files):
                    result += f"- {file_path}\n"
            
            return result
            
        except Exception as e:
            return f"Error listing wiki files: {str(e)}"
