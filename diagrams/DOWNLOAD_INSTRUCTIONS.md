# 📥 Download Diagrams - Quick Links

Since `npm` is not installed, here are **direct URLs** to view and download your diagrams as PNG/SVG:

## 🎨 Diagram 1: System Architecture
**Copy the contents of `1-system-architecture.mmd` and paste into:**
👉 https://mermaid.live

Then:
- ⬇️ Click **"Download"** → Choose **PNG** or **SVG**
- 📋 Screenshot the diagram
- 🔗 Share the URL

---

## 🎨 Diagram 2: Data Flow
**Copy the contents of `2-data-flow.mmd` and paste into:**
👉 https://mermaid.live

---

## 🎨 Diagram 3: User Workflows  
**Copy the contents of `3-user-workflows.mmd` and paste into:**
👉 https://mermaid.live

---

## ⚡ Quick Steps to Export as Image

1. Open https://mermaid.live in your browser
2. Click **"Edit"** button (top-left)
3. Clear the default diagram
4. Open file `diagrams/1-system-architecture.mmd` in VS Code
5. Select all text (Ctrl+A) → Copy (Ctrl+C)
6. Paste into Mermaid Live Editor
7. Wait for diagram to render
8. Click **"Download"** button
9. Select **PNG** or **SVG** format
10. Save to your downloads folder

---

## 📁 Alternative: Manual Image Generation

If you want to generate images **locally** without npm:

### Option A: Use Python + Kroki API
```bash
# Python script to render diagrams (paste into a terminal)
python3 -c "
import requests
import base64

files = ['1-system-architecture', '2-data-flow', '3-user-workflows']

for filename in files:
    with open(f'diagrams/{filename}.mmd', 'r') as f:
        mermaid_code = f.read()
    
    # Encode for Kroki API
    encoded = base64.b64encode(mermaid_code.encode()).decode()
    url = f'https://kroki.io/mermaid/png/{encoded}'
    
    # Download
    r = requests.get(url)
    with open(f'diagrams/{filename}.png', 'wb') as out:
        out.write(r.content)
    print(f'✓ Generated: diagrams/{filename}.png')
"
```

### Option B: Use Docker
```bash
# If Docker is installed
docker run --rm -v $(pwd)/diagrams:/data aw3ly/mmdc -i /data/1-system-architecture.mmd -o /data/1-system-architecture.png
docker run --rm -v $(pwd)/diagrams:/data aw3ly/mmdc -i /data/2-data-flow.mmd -o /data/2-data-flow.png
docker run --rm -v $(pwd)/diagrams:/data aw3ly/mmdc -i /data/3-user-workflows.mmd -o /data/3-user-workflows.png
```

---

## 📸 What You'll Get

All three diagrams will be available as:
- ✅ **PNG** (raster image - good for presentations)
- ✅ **SVG** (vector image - scalable, good for documentation)
- ✅ **High resolution** (2560x1440+ pixels)

---

## 📍 File Locations

The Mermaid source files are located at:
```
/home/ruturajwairkar/Desktop/SPE_MP/diagrams/
├── 1-system-architecture.mmd
├── 2-data-flow.mmd
├── 3-user-workflows.mmd
└── README.md
```

---

**All files are ready! Choose your preferred download method above.** 🎉
