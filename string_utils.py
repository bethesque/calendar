import re

def sanitise_filename(text):
    """Convert text to a safe filename by removing/replacing unsafe characters."""
    # Remove or replace unsafe characters
    safe_text = re.sub(r'[<>:"/\\|?*]', '', text)  # Remove filesystem-unsafe chars
    safe_text = re.sub(r'[^\w\s-]', '', safe_text)  # Remove other special chars except spaces, hyphens, underscores
    safe_text = re.sub(r'\s+', '_', safe_text)  # Replace spaces with underscores
    safe_text = safe_text.strip('_-')  # Remove leading/trailing underscores/hyphens
    safe_text = safe_text.lower()  # Convert to lowercase for consistency

    # Limit length to avoid filesystem issues
    if len(safe_text) > 200:
        safe_text = safe_text[:200].rstrip('_-')

    return safe_text
