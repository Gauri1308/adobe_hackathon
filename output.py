from typing import Any, Dict, List

class OutputFormatter:
    """Formats the extracted document structure for API responses."""

    def format_output(self, title: str, outline: List[Dict[str, Any]], full_structure: bool = False) -> Dict[str, Any]:
        """
        Formats the extracted title and outline into a structured dictionary.

        Args:
            title: The document title.
            outline: A list of heading dictionaries.
            full_structure: If True, includes detailed heading attributes.

        Returns:
            A dictionary containing the formatted title and outline.
        """
        formatted_outline = [
            self._format_heading(item, full_structure) for item in outline
        ]
        return {"title": title, "outline": formatted_outline}

    def _format_heading(self, heading: Dict[str, Any], full_structure: bool) -> Dict[str, Any]:
        """Formats a single heading item."""
        if full_structure:
            return {
                "level": heading.get("level", "H3"),
                "text": heading.get("text", "").strip(),
                "page": heading.get("page", 0),
                "font_size": heading.get("font_size", 0),
                "is_bold": heading.get("is_bold", False),
            }
        return {
            "level": heading.get("level", "H3"),
            "text": heading.get("text", "").strip(),
        } 