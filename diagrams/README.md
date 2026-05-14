# System Architecture Diagrams

Three comprehensive diagrams have been generated showing different aspects of the AI-Powered Smart Ecommerce Pricing Platform.

## 📋 Files Created

1. **1-system-architecture.mmd** - Complete system architecture with all components
2. **2-data-flow.mmd** - Data flow from input to output  
3. **3-user-workflows.mmd** - Three complete user workflows (Admin, Customer, Retrain)

## 🖼️ How to View & Export

### Option 1: View Online (Recommended for Quick Preview)
Copy the contents of any `.mmd` file and paste into:
- **Mermaid Live Editor**: https://mermaid.live
- Supports instant rendering and export to PNG/SVG

### Option 2: Use CLI Tools

#### Install Mermaid CLI:
```bash
npm install -g mermaid-cli
```

#### Generate PNG images:
```bash
mmdc -i diagrams/1-system-architecture.mmd -o diagrams/1-system-architecture.png
mmdc -i diagrams/2-data-flow.mmd -o diagrams/2-data-flow.png
mmdc -i diagrams/3-user-workflows.mmd -o diagrams/3-user-workflows.png
```

#### Generate SVG images (vector format):
```bash
mmdc -i diagrams/1-system-architecture.mmd -o diagrams/1-system-architecture.svg
mmdc -i diagrams/2-data-flow.mmd -o diagrams/2-data-flow.svg
mmdc -i diagrams/3-user-workflows.mmd -o diagrams/3-user-workflows.svg
```

### Option 3: Use Markdown Preview Extensions
If using VS Code with Markdown Preview Mermaid Support extension:
1. Open any `.mmd` file
2. File will render automatically if you have the extension installed
3. Right-click diagram → "Export as PNG/SVG"

### Option 4: GitHub/GitLab/Gitea
These platforms automatically render Mermaid diagrams if the `.mmd` files are committed to the repository.

## 📊 What Each Diagram Shows

### Diagram 1: Complete System Architecture
- **Startup & Initialization**: Model loading, data file creation
- **Historical Data**: Training dataset
- **ML Model Core**: RandomForest model
- **Flask REST API**: All 14 endpoints
- **Data Persistence**: All CSV/JSON files
- **Admin Dashboard**: 4 tabs (Optimizer, Products, Analytics, Retrain)
- **Customer Store**: 5 page states
- **Optimization Flow**: Price optimization algorithm
- **Checkout Flow**: Order processing
- **Retraining Pipeline**: Model retraining steps
- **Background Retrain**: Threading & state management
- **Apply Price Flow**: Price update logic
- **serialize_product Helper**: AI field computation
- **Security**: Token protection
- **Testing**: Smoke tests
- **Logging & State**: State management

### Diagram 2: Data Flow Architecture
- Shows **left-to-right flow** from input to output
- **INPUT**: Historical data + product catalog
- **TRAINING**: Retrain pipeline
- **MODEL**: Deployed ML model
- **FLASK**: REST API endpoints
- **DATA**: CSV/JSON storage
- **UIs**: Admin and Customer frontends
- **OUTPUT**: Orders and sales history
- **FEEDBACK**: New data feeds back into training

### Diagram 3: Complete User Workflows
Three separate end-to-end flows:

#### A. Admin Workflow (18 steps)
1. Select product and enter parameters
2. Run AI optimizer
3. Model predicts 25 price points
4. Displays curve and metrics
5. Admin applies optimized price
6. Price updated in products.csv
7. Price change logged

#### B. Customer Workflow (33 steps)
1. Browse products
2. Search and filter
3. View product details
4. Add to cart
5. Checkout with validation
6. Create order record
7. Write to orders.csv
8. Write to sales_history.csv
9. Update inventory
10. Show success confirmation

#### C. Retrain Workflow (20 steps)
1. Admin triggers retraining
2. Background thread spawned
3. Load old historical data
4. Load new sales data
5. Merge and validate
6. Train RandomForest
7. Evaluate metrics
8. Compare with existing model
9. Save or keep existing
10. Show status to admin

## 🎨 Color Coding

Each component has a distinct color for easy identification:
- **Light Blue**: Startup
- **Light Orange**: Model & Training
- **Yellow**: Deployed model
- **Purple**: Flask API
- **Light Green**: Admin UI
- **Pink**: Customer UI
- **Light Green**: Data & Flows
- **Gray/Red**: Security & Testing

## 💡 Tips

- **For presentations**: Export to PNG (1920x1080 recommended)
- **For documentation**: Use SVG (scalable vector format)
- **For reports**: Screenshot from Mermaid Live with white background
- **For web**: Use SVG and embed in HTML

## 🔄 Updating Diagrams

If you modify the `.mmd` files, regenerate images using the same commands above.

---

**All diagrams are complete and ready for download/viewing!**
