# Adobe India Hackathon 2025 - Round 1A
## 🧠 Project: PDF Outline Extractor - "Connecting the Dots"

### 📌 Problem Statement
Transform a static PDF into a structured outline including title and hierarchical headings (H1, H2, H3) with page numbers.

### 🔍 Our Approach
- We use **PyMuPDF** to extract text spans, font sizes, and layout info.
- **Font size heuristics** are applied to categorize headings into H1/H2/H3.
- The **title** is inferred from early pages based on font size and position.
- Outputs valid JSON for each PDF.

### 📂 Input/Output
- Input PDFs: `/app/input/*.pdf`
- Output JSONs: `/app/output/*.json`

### ⚙️ Dependencies
- PyMuPDF
- NumPy

### 🐳 Docker Instructions

#### 🔨 Build
```bash
docker build --platform linux/amd64 -t pdf-extractor:yourtag .
