# 🎯 Complete Guide to Download & View Your Diagrams

Your three system architecture diagrams have been created as Mermaid files. Here's how to download them as images.

## ✅ Files Ready for Export
Located in: `/home/ruturajwairkar/Desktop/SPE_MP/diagrams/`

```
1-system-architecture.mmd     (12 KB)  - Complete system with all components
2-data-flow.mmd              (3.1 KB) - Left-to-right data flow
3-user-workflows.mmd         (6.9 KB) - Three complete user workflows
```

---

## 🚀 EASIEST METHOD: Mermaid Live Editor (Recommended)

**No installation needed. Takes 2 minutes.**

### Step 1: Open Mermaid Live Editor
👉 **Go to:** https://mermaid.live

### Step 2: Load Your Diagram
1. In Mermaid Live, click the **"Edit"** button (pencil icon, top-left)
2. Select all text in the editor (`Ctrl+A`)
3. Delete it
4. Open this file in VS Code: `/home/ruturajwairkar/Desktop/SPE_MP/diagrams/1-system-architecture.mmd`
5. Copy all content (`Ctrl+A` → `Ctrl+C`)
6. Paste into Mermaid Live (`Ctrl+V`)
7. **Wait for diagram to render** (2-5 seconds)

### Step 3: Download as Image
1. Click **"Download"** button (bottom-right)
2. Choose **PNG** (raster) or **SVG** (vector)
3. File will download automatically
4. **Repeat for diagrams 2 and 3**

**Result:** You'll have 3 PNG/SVG files in your downloads folder ✨

---

## 💻 DEVELOPER METHOD: Install Mermaid CLI

### Prerequisites
- Node.js and npm installed
- (If not installed: `sudo apt install nodejs npm`)

### Installation & Usage

```bash
# Install globally
npm install -g mermaid-cli

# Generate PNG images
cd /home/ruturajwairkar/Desktop/SPE_MP
mmdc -i diagrams/1-system-architecture.mmd -o diagrams/1-system-architecture.png
mmdc -i diagrams/2-data-flow.mmd -o diagrams/2-data-flow.png
mmdc -i diagrams/3-user-workflows.mmd -o diagrams/3-user-workflows.png

# Generate SVG images (vector format, scalable)
mmdc -i diagrams/1-system-architecture.mmd -o diagrams/1-system-architecture.svg
mmdc -i diagrams/2-data-flow.mmd -o diagrams/2-data-flow.svg
mmdc -i diagrams/3-user-workflows.mmd -o diagrams/3-user-workflows.svg
```

**Result:** PNG and SVG files in the `diagrams/` folder

---

## 🐳 DOCKER METHOD: No Local Installation

If Docker is installed on your system:

```bash
# Generate all PNG images
docker run --rm -v $(pwd)/diagrams:/data aw3ly/mmdc \
  -i /data/1-system-architecture.mmd -o /data/1-system-architecture.png

docker run --rm -v $(pwd)/diagrams:/data aw3ly/mmdc \
  -i /data/2-data-flow.mmd -o /data/2-data-flow.png

docker run --rm -v $(pwd)/diagrams:/data aw3ly/mmdc \
  -i /data/3-user-workflows.mmd -o /data/3-user-workflows.png
```

**Result:** PNG files generated without installing npm

---

## 🌐 ONLINE ALTERNATIVES

### Option 1: GitHub/GitLab (Free)
1. Commit the `.mmd` files to your GitHub repo
2. They'll render automatically in the README
3. Click "..." on the diagram → Download

### Option 2: Diagrams.net (formerly Draw.io)
1. Go to: https://app.diagrams.net/
2. File → Import → URL → Paste Mermaid code
3. Export as PNG/SVG

### Option 3: Use Mermaid with Pandoc
```bash
# If Pandoc is installed
pandoc -f mermaid -t png diagrams/1-system-architecture.mmd -o diagrams/1-system-architecture.png
```

---

## 📊 What Each Diagram Contains

### Diagram 1: System Architecture (Most Detailed)
- 🚀 Startup sequence
- 🧠 ML model core  
- 🌐 14 Flask API endpoints
- 📦 All components and flows
- **Best for:** Complete overview, presentations

### Diagram 2: Data Flow (Linear View)
- ⬅️➡️ Left-to-right flow
- Shows which components communicate
- **Best for:** Understanding data movement

### Diagram 3: User Workflows (Step-by-Step)
- 👨‍💼 Admin optimization flow (18 steps)
- 🛍️ Customer shopping flow (33 steps)
- 🔄 Retrain workflow (20 steps)
- **Best for:** Understanding user interactions

---

## 🎨 Image Quality Options

| Format | Quality | Size | Best For |
|--------|---------|------|----------|
| **PNG** | Raster, 1920x1080 | ~300-500KB | Presentations, web |
| **SVG** | Vector, scalable | ~200-400KB | Documents, printing, scaling |
| **PDF** | High quality | ~500KB | Professional reports |

---

## 📍 Quick Reference

**Mermaid Files Location:**
```
/home/ruturajwairkar/Desktop/SPE_MP/diagrams/
├── 1-system-architecture.mmd
├── 2-data-flow.mmd
├── 3-user-workflows.mmd
├── README.md
└── DOWNLOAD_INSTRUCTIONS.md
```

**After downloading, your structure will be:**
```
/home/ruturajwairkar/Desktop/SPE_MP/diagrams/
├── *.mmd                           (Mermaid source)
├── *.png                           (PNG images)
├── *.svg                           (SVG images)
└── *.md                            (Documentation)
```

---

## ⚡ Recommended Workflow

1. **For quick preview:** Use Mermaid Live (2 min)
2. **For presentations:** Download PNG (high res)
3. **For documentation:** Download SVG (scalable)
4. **For version control:** Keep `.mmd` files in git

---

## 🆘 Troubleshooting

### Mermaid Live not loading?
- Clear browser cache (Ctrl+Shift+Delete)
- Try a different browser
- Check internet connection

### PNG too large?
- SVG is smaller and scales better
- Compress PNG online: https://tinypng.com

### Can't copy from VS Code?
- Select all with triple-click
- Or use: Ctrl+A (in the file)

### Diagrams look truncated?
- Use SVG instead (vector format)
- Or increase PNG resolution

---

## ✨ You're All Set!

**Your diagrams are ready to download.** Choose the method that works best for you.

**Questions?** All files are self-contained and can be viewed/edited at any time.

Happy diagramming! 📊
