import fitz  # PyMuPDF
import os
import json
from collections import defaultdict
from outline_extractor import OutlineExtractor
from output import OutputFormatter

class TextElement:
    def __init__(self, text, x, y, font_size, page_num, is_bold):
        self.text = text.strip()
        self.x_position = x
        self.y_position = y
        self.font_size = font_size
        self.page_num = page_num
        self.is_bold = is_bold

def extract_text_elements(pdf_path):
    doc = fitz.open(pdf_path)
    elements = []
    font_sizes = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:  # text only
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    size = round(span["size"], 1)
                    font = span["font"]
                    flags = span["flags"]
                    is_bold = bool(flags & 2) or "bold" in font.lower() or "bd" in font.lower()

                    elements.append(TextElement(
                        text=text,
                        x=span["bbox"][0],
                        y=span["bbox"][1],
                        font_size=size,
                        page_num=page_num,
                        is_bold=is_bold
                    ))
                    font_sizes.append(size)

    # Estimate body font size using mode
    font_count = defaultdict(int)
    for s in font_sizes:
        font_count[s] += 1
    body_font_size = max(font_count.items(), key=lambda x: x[1])[0] if font_count else 12

    return {
        "text_elements": elements,
        "document_stats": {
            "body_font_size": body_font_size
        }
    }

def process_all_pdfs(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    extractor = OutlineExtractor(debug=True)
    formatter = OutputFormatter()

    for filename in os.listdir(input_dir):
        if not filename.endswith(".pdf"):
            continue
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
        try:
            print(f"Processing {filename}")
            pdf_data = extract_text_elements(input_path)
            extracted = extractor.extract_hierarchical_structure(pdf_data)
            formatted = formatter.format_output(extracted["title"], extracted["outline"], full_structure=False)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(formatted, f, indent=2, ensure_ascii=False)
            print(f"Saved to {output_path}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"
    process_all_pdfs(input_dir, output_dir)
