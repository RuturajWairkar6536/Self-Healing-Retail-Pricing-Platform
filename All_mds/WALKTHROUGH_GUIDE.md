# 🚀 Complete Walkthrough: Admin & Customer Platform

---

## 📊 ADMIN DASHBOARD (Port 8503)
### http://localhost:8503

The admin dashboard has **4 main tabs**. Let's walk through each:

---

### **TAB 1: OPTIMIZER** ⚡ (Main AI Feature)
**What it does:** Uses AI to suggest the BEST PRICE for a product to maximize revenue

#### STEP 1: Select a Product
1. Look at **"Select Product"** dropdown
2. Click and choose any product (e.g., "Wireless Headphones")
3. This loads the product details

#### STEP 2: Set Current Market Conditions
Enter these values:
- **Current Price**: Current selling price (e.g., ₹3240)
- **Competitor Price**: What competitors charge (e.g., ₹3500)
- **Current Stock**: How many units you have (e.g., 50)
- **Day of Week**: Select from dropdown (Mon-Sun)
- **Month**: Select from dropdown (Jan-Dec)

**Why?** AI model learns: *"On Monday in January, if we price at ₹3240, customers demand X units"*

#### STEP 3: Click "Optimize Price"
System does this:
1. Tests 25 different prices (±20% range)
2. Predicts demand for each price using ML model
3. Calculates revenue = price × demand for each
4. Shows you a **CHART** with the profit curve
5. Highlights the BEST price in red

#### STEP 4: Read the Results
You'll see:
- **Graph**: X-axis = Price, Y-axis = Revenue (shows peak profit point)
- **Optimal Price**: AI recommendation
- **Predicted Demand**: How many units expected at optimal price
- **Revenue Gain %**: How much more money vs current price
- **AI Decision**: Why it recommends this (e.g., "Increase from ₹3240 to ₹3300")

#### STEP 5: Apply the Price
1. Click **"Apply Optimized Price"** button
2. Optimal price is NOW set in the system
3. Customer store will show this new price

**EXAMPLE OUTPUT:**
```
Current Price: ₹3240
Competitor Price: ₹3500
Stock: 50

AI Analysis:
- Testing 25 prices from ₹2592 to ₹3888
- Best revenue found at: ₹3300
- Predicted demand: 42 units
- Predicted revenue: ₹138,600
- Revenue gain: +15.2%
```

---

### **TAB 2: PRODUCTS** 📦
**What it does:** Manage your product catalog (view, add, update)

#### STEP 1: View All Products
1. Scroll down in this tab
2. You'll see a **TABLE** with all 15 products showing:
   - Product ID (P001-P015)
   - Product Name
   - Category
   - Current Price
   - **AI Recommended Price** (from optimizer)
   - **AI Predicted Demand** (expected sales)
   - **AI Decision** (why price changed)
   - Discount %
   - Stock

**Example Row:**
```
| P001 | Wireless Headphones | Electronics | ₹3240 | ₹3300 | 42 | Increase price | 10% | 88 |
```

#### STEP 2: Add a New Product (Optional)
If you want to add a new product:
1. Scroll to **"Add New Product"** form at bottom
2. Fill in:
   - Product Name: "New Product Name"
   - Category: Choose from dropdown
   - Price: ₹XXX
   - Description: "Product details"
   - Image URL: Paste image link (from Unsplash or any image site)
   - Stock: How many units

3. Click **"Add Product"** button
4. System saves it to products.csv
5. Product appears in store immediately

---

### **TAB 3: ANALYTICS** 📈
**What it does:** See sales trends, bestsellers, revenue metrics

#### STEP 1: View Key Metrics
At the top, see:
- **Total Revenue**: All money earned so far
- **Total Orders**: How many purchases
- **Average Order Value**: ₹X average per customer

#### STEP 2: Check Bestsellers
1. Look at **"Top 5 Bestselling Products"** chart
2. Shows which products sell the most
3. Use this to decide which products to optimize prices on

#### STEP 3: Check Monthly Sales
1. See **"Monthly Sales Trend"** graph
2. Shows revenue over time
3. Helps identify seasons (when sales spike)

#### STEP 4: Monitor Low Stock
1. Check **"Low Stock Alert"** section
2. Lists products with <20 units in stock
3. Action: Plan to reorder or increase price to reduce demand

#### STEP 5: Check Price History
1. See **"Price History"** of each product
2. Shows how AI changed prices over time
3. Validates if price optimization is working

---

### **TAB 4: RETRAINING** 🤖
**What it does:** Retrain the AI model with NEW sales data so it improves

#### Background (Why needed):
- Current model trained on OLD data (2009-2010)
- As customers buy, new data accumulates
- Retraining updates model with fresh customer behavior

#### STEP 1: Understand the Current Model
- Uses `clean_demand_data.csv` (historical baseline)
- Trained on: Price, day_of_week, month → predicts demand

#### STEP 2: Check if Retraining is Needed
1. Look at **"Retrain Status"** section
2. Shows:
   - Last model performance (MAE, R²)
   - If model was updated recently

#### STEP 3: Trigger Retraining
1. Click **"Trigger Full Retraining"** button
2. System does this automatically:
   - Loads old training data (clean_demand_data.csv)
   - Loads new customer purchases (data/sales_history.csv)
   - Merges both datasets
   - Trains new RandomForest model
   - Compares: new model vs old model
   - If new is better → Saves new model ✅
   - If new is worse → Keeps old model ❌

#### STEP 4: Wait for Completion
- Processing happens in background
- Takes 5-30 seconds depending on data size
- Status updates automatically

#### STEP 5: Check Results
After retraining:
```
✅ Retraining Complete!
- Old Model MAE: 5.2 units
- New Model MAE: 4.8 units ← BETTER
- Old Model R²: 0.78
- New Model R²: 0.82 ← BETTER
→ New model saved! 🎉
```

**WHAT THIS MEANS:**
- Model now better predicts customer demand
- AI price recommendations will be more accurate
- Sales will likely improve

---

## 🛍️ CUSTOMER STORE (Port 8504)
### http://localhost:8504

Simple ecommerce store where customers see products and make purchases

---

### **PAGE 1: HOME** 🏠
**What it does:** Welcome page with featured products

#### STEP 1: View Featured Products
1. Page loads with 4 featured products displayed
2. Each product shows:
   - Product image
   - Product name
   - Category
   - **Current Price** (set by admin AI optimizer)
   - Discount % (if any)
   - "AI-updated store price" badge
   - Stock status

#### STEP 2: Explore Products
- Click **"Browse"** button in sidebar to see all 15 products
- OR click **"View"** button on any featured product

---

### **PAGE 2: BROWSE** 🔍
**What it does:** Search and filter all products

#### STEP 1: Search by Name
1. In search box, type product name (e.g., "Yoga Mat")
2. System filters and shows matching products
3. Results update instantly

#### STEP 2: Filter by Category
1. Click **"Category"** dropdown
2. Choose category (Electronics, Sports, Beauty, Kitchen, etc.)
3. Shows only products in that category

#### STEP 3: View Product Grid
- See all matching products in 3-column grid
- Each card shows name, price, discount, stock status

#### STEP 4: Take Action on Product
- Click **"View"** → Go to detail page for full info
- Click **"Add"** → Add to cart immediately (if in stock)

---

### **PAGE 3: PRODUCT DETAIL** 📖
**What it does:** See full product information

#### STEP 1: View Product Image
- Large high-quality product image at left
- Shows aspect ratio correctly (thanks to fix!)

#### STEP 2: Read Product Details
On right side, see:
- Product name
- Category
- **Current Price** (AI-optimized)
- Discount % badge
- Full description
- Stock quantity
- **AI Recommendation**: "₹3300 | Decision: Increase price"

#### STEP 3: Select Quantity
1. Use number input to choose quantity (1, 2, 3, etc.)
2. Max quantity = available stock
3. Button disabled if out of stock

#### STEP 4: Add to Cart
- Click **"Add to cart"** button
- Quantity added to your cart
- Success message appears
- Automatically updates cart total

---

### **PAGE 4: CART** 🛒
**What it does:** Review items before checkout

#### STEP 1: View Cart Items
- See all products you added
- For each item shows:
  - Product name
  - Quantity
  - Unit price
  - Total price (quantity × price)

#### STEP 2: Modify Cart
- **Increase Quantity**: Click + button
- **Decrease Quantity**: Click - button
- **Remove Item**: Click X or remove button
- Cart total updates automatically

#### STEP 3: Check Cart Summary
- Subtotal: Sum of all items
- Number of items
- Total amount to pay

#### STEP 4: Proceed to Checkout
- Click **"Proceed to Checkout"** button
- Moves to final checkout page

---

### **PAGE 5: CHECKOUT** 💳
**What it does:** Complete the purchase

#### STEP 1: Review Order
- See final order summary:
  - All products with quantities
  - Unit prices
  - Total price

#### STEP 2: Enter Shipping Details
Fill in:
- Name
- Email
- Address
- City/State
- Postal Code

#### STEP 3: Complete Purchase
- Click **"Complete Purchase"** button
- System does this:
  1. Validates all information
  2. Checks if items still in stock
  3. Creates order record
  4. Decreases stock in inventory
  5. Records sale to sales_history.csv
  6. Updates price history
  7. Clears your cart
  8. Shows confirmation

#### STEP 4: See Confirmation
```
✅ Order Placed Successfully!
Order ID: 2024-05-13-001
Products: 3 items
Total: ₹8,499

Your order data is now:
- Saved to orders.csv (admin can see)
- Added to sales_history.csv (used for model retraining)
- Stock updated automatically
```

#### STEP 5: Repeat
- Cart is cleared
- Ready to shop again
- Return to **"Home"** or **"Browse"**

---

## 🔄 FULL WORKFLOW EXAMPLE

### **Complete End-to-End Scenario:**

#### ADMIN SIDE (Setup):
```
1. Start Admin Dashboard (streamlit_app.py port 8503)
2. Go to OPTIMIZER tab
3. Select "Wireless Headphones"
4. Enter: Price ₹3240, Competitor ₹3500, Stock 50, Monday, January
5. Click "Optimize Price"
6. See chart → Optimal price is ₹3300 (+15% revenue)
7. Click "Apply Optimized Price"
8. Go to PRODUCTS tab → See new price in table
9. Go to ANALYTICS tab → Monitor revenue
10. Go to RETRAINING tab → Trigger retraining
11. Wait for "New model saved!" message
```

#### CUSTOMER SIDE (Purchase):
```
1. Start Customer Store (streamlit_customer.py port 8504)
2. See featured products on HOME page
3. Click BROWSE → Search "Yoga Mat" → Filter by "Sports"
4. Click "View" on Yoga Mat
5. See detail page with NEW AI-optimized price
6. Enter quantity: 2
7. Click "Add to cart"
8. Continue shopping → Add more products
9. Click "Cart (3)" in sidebar
10. See all 3 items with total
11. Click "Proceed to Checkout"
12. Fill name, email, address
13. Click "Complete Purchase"
14. ✅ Order confirmed! Stock updated, sale recorded
```

#### Back to ADMIN:
```
1. Go to ANALYTICS tab
2. See new order in "Monthly Sales Trend"
3. See "Yoga Mat" in "Top 5 Bestsellers"
4. Stock decreased in PRODUCTS tab
5. Later: Trigger RETRAINING again (with new sales data)
6. Model gets better at predicting demand
7. Recommendations improve 🎯
```

---

## 🎯 KEY FUNCTIONS SUMMARY

### **ADMIN CAN:**
✅ Select products to optimize
✅ Set market conditions (competitor prices, stock, timing)
✅ Run AI optimizer (see profit curve, revenue gain %)
✅ Apply recommended prices
✅ View all products with AI decisions
✅ Add new products
✅ Monitor sales metrics and bestsellers
✅ Check low stock alerts
✅ View price history
✅ Retrain AI model with new sales data
✅ Check model improvement metrics (MAE, R²)

### **CUSTOMER CAN:**
✅ Browse all products
✅ Search by name
✅ Filter by category
✅ View product details
✅ Add items to cart
✅ Modify cart (quantity, remove items)
✅ Checkout with shipping details
✅ Confirm purchase
✅ See order confirmation
✅ See AI-optimized prices in real-time

### **SYSTEM DOES AUTOMATICALLY:**
✅ Updates prices based on admin's AI decisions
✅ Records every sale to sales_history.csv
✅ Updates stock after each order
✅ Uses sales data to retrain model
✅ Improves AI recommendations over time
✅ Calculates revenue metrics

---

## 🧪 THINGS TO TRY (In Order)

### **First Run:**
1. ✅ Admin Optimizer: Optimize "Wireless Headphones"
2. ✅ Admin Products: Check new price in table
3. ✅ Customer Store: See new price on detail page
4. ✅ Admin Analytics: View current metrics
5. ✅ Customer Store: Add product to cart
6. ✅ Customer Store: Checkout and complete order
7. ✅ Admin Analytics: See sale recorded in metrics
8. ✅ Admin Products: Stock decreased

### **Advanced Features:**
9. ✅ Admin: Add new product in PRODUCTS tab
10. ✅ Customer: See new product in store
11. ✅ Admin: Optimize new product's price
12. ✅ Customer: Purchase new product
13. ✅ Admin: Trigger RETRAINING
14. ✅ Check "New model saved" message
15. ✅ Repeat purchases to build sales history
16. ✅ Retrain again (model improves each time)

---

## 💡 TIPS & TRICKS

**Admin Tips:**
- **Best time to optimize**: After several customer purchases (more data = better decisions)
- **Monitor bestsellers**: Optimize high-selling products for max impact
- **Stock alerts**: When stock is low, increase price to reduce demand
- **Retraining**: Run after every 5-10 sales for model improvements

**Customer Tips:**
- **Check categories**: Browse by category if looking for specific items
- **Use search**: Faster to search than scroll through grid
- **Compare prices**: View multiple products before deciding
- **Add to cart**: No commitment - review before checkout

**General Tips:**
- **Refresh page**: If something looks wrong, reload the page
- **Both terminals running**: Keep both streamlit apps running in separate terminals
- **Clear cache**: If prices don't update, refresh browser (Ctrl+Shift+R)

---

## ⚠️ COMMON QUESTIONS

**Q: Why are product prices changing?**
A: Admin used AI Optimizer to set new prices. Changes appear immediately in customer store.

**Q: What happens to my order after checkout?**
A: System saves it to `orders.csv`, deducts stock, and records sale for ML retraining.

**Q: How does AI improve over time?**
A: Each customer purchase = new data. Retraining learns patterns and makes better predictions.

**Q: Can I retrain model manually?**
A: Yes! RETRAINING tab → "Trigger Full Retraining" → Wait for "New model saved!"

**Q: Why do I need competitor price?**
A: AI learns: "When competitors are expensive, customers prefer us → demand goes up"

**Q: What does "Revenue Gain %" mean?**
A: How much more money you'll make with AI price vs current price.

---

That's it! 🚀 Now go try it out step-by-step!
