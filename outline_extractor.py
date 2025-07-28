import re
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

class OutlineExtractor:
    """Extracts a hierarchical outline from a processed PDF's text elements."""

    def __init__(self, debug: bool = False):
        self.debug = debug

    def extract_hierarchical_structure(self, pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts the title and a structured outline from PDF data.

        Args:
            pdf_data: A dictionary containing text elements and document statistics.

        Returns:
            A dictionary with the document title and a list of outline items.
        """
        try:
            text_elements = pdf_data.get("text_elements", [])
            if not text_elements:
                return {"title": "", "outline": []}

            title = self._extract_title(text_elements, pdf_data.get("document_stats", {}))
            outline = self._extract_outline(text_elements, pdf_data.get("document_stats", {}))
            
            return {"title": title, "outline": outline}
        except Exception as e:
            if self.debug:
                print(f"Error during outline extraction: {e}")
            return {"title": "", "outline": []}

    def _extract_title(self, text_elements: List[Any], doc_stats: Dict) -> str:
        """Extracts the document title based on font size and position."""
        title_candidates = [
            elem for elem in text_elements 
            if elem.page_num == 1 and elem.font_size > doc_stats.get("body_font_size", 12) * 1.5
        ]
        
        if not title_candidates:
            return "No Title Found"
        
        # Select the highest positioned, largest font candidate
        title_candidates.sort(key=lambda elem: (-elem.font_size, elem.y_position))
        return title_candidates[0].text.strip()

    def _extract_outline(self, text_elements: List[Any], doc_stats: Dict) -> List[Dict]:
        """Extracts the outline by identifying and structuring headings."""
        lines = self._group_elements_into_lines(text_elements)
        headings = self._identify_headings(lines, doc_stats)
        return self._structure_headings(headings, doc_stats)

    def _group_elements_into_lines(self, elements: List[Any]) -> List[Dict]:
        """Groups text elements into lines based on their vertical position."""
        if not elements:
            return []

        # Use a more tolerant grouping to handle slight misalignments
        lines, y_tolerance = defaultdict(list), 3
        for elem in elements:
            # Find a nearby line to join, otherwise start a new one
            match = next((y for y in lines if abs(y - elem.y_position) < y_tolerance), None)
            lines[match or elem.y_position].append(elem)

        processed_lines = []
        for y_pos in sorted(lines.keys()):
            elements_on_line = sorted(lines[y_pos], key=lambda e: e.x_position)
            combined_text = " ".join(elem.text for elem in elements_on_line).strip()
            
            if len(combined_text) > 2:
                processed_lines.append({
                    'text': combined_text,
                    'font_size': elements_on_line[0].font_size,
                    'is_bold': any(e.is_bold for e in elements_on_line),
                    'page_num': elements_on_line[0].page_num,
                })
        return processed_lines

    def _identify_headings(self, lines: List[Dict], doc_stats: Dict) -> List[Dict]:
        """Identifies potential headings from a list of text lines."""
        body_font_size = doc_stats.get("body_font_size", 12)
        headings = []
        for line in lines:
            if self._is_heading(line, body_font_size):
                headings.append(line)
        return headings

    def _is_heading(self, line: Dict, body_font_size: float) -> bool:
        """Determines if a line is a heading based on several criteria."""
        text = line['text']
        if len(text) < 3 or len(text) > 200 or len(text.split()) > 20:
            return False

        if not re.match(r"^(?:\d+\.?\s*|[A-Z]\.\s*|•\s*)?[A-Z]", text):
            return False # Must start with a number, letter, or bullet

        # Must be bold or have a larger font size than body text
        is_structurally_significant = line['is_bold'] or line['font_size'] > body_font_size + 1
        
        # Exclude lines that resemble regular sentences
        ends_with_punctuation = text.endswith('.') and not text.endswith('...')
        
        return is_structurally_significant and not ends_with_punctuation

    def _structure_headings(self, headings: List[Dict], doc_stats: Dict) -> List[Dict]:
        """Assigns levels to headings to create a hierarchical structure."""
        if not headings:
            return []

        # Determine heading levels based on font sizes
        font_sizes = sorted(list(set(h['font_size'] for h in headings)), reverse=True)
        size_to_level = {size: f"H{i+1}" for i, size in enumerate(font_sizes)}

        structured_outline = []
        for heading in headings:
            level = size_to_level.get(heading['font_size'], "H3") # Default to H3
            structured_outline.append({
                "level": level,
                "text": heading['text'],
                "page": heading['page_num'],
            })
        return structured_outline
