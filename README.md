# 🍽️ Restaurant Operations Dashboard

A comprehensive Streamlit dashboard for viewing restaurant operations data across all key modules.

## 📊 Features

- **Dashboard Overview**: Key metrics and quick data preview
- **Detailed Tables**: Interactive view of all 10 data modules
- **Search Functionality**: Search across all table data
- **Download Options**: Export any table as CSV
- **Responsive Design**: Works on desktop and mobile

## 📁 Data Modules

The dashboard displays data from 10 key restaurant operations areas:

1. **Menu** - Items, pricing, COGS, and ingredients
2. **Inventory** - Ingredient tracking and usage
3. **POS Sales** - Transaction data with servers and payments
4. **Reservations** - Table management and booking sources
5. **Reviews** - Customer feedback with sentiment analysis
6. **HR & Staff** - Employee shifts and performance
7. **Vendor & Supply** - Supplier relationships and deliveries
8. **CRM & Loyalty** - Customer profiles and preferences
9. **Finance & Accounting** - Key financial metrics and KPIs
10. **Marketing & Promotions** - Campaign results and effectiveness

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key (for AI analysis features)

### Installation

1. **Install dependencies:**
   ```bash
   pip install streamlit pandas pathlib2 openai
   ```

2. **Set up OpenAI API key (required for AI features):**
   
   **Option 1: System Environment Variable**
   Set the API key in your system environment variables:
   - Windows: `setx OPENAI_API_KEY "your_api_key_here"`
   - Mac/Linux: `export OPENAI_API_KEY="your_api_key_here"`
   
   **Option 2: Streamlit Secrets (Recommended for Cloud)**
   Create `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
   
   **Get your API key from:** https://platform.openai.com/api-keys

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```

4. **Open your browser:**
   The app will automatically open at `http://localhost:8501`

### Alternative Installation
```bash
pip install -r requirements.txt
streamlit run main.py
```

## 💡 Usage

### Pages Available:
1. **Home**: AI-powered analysis with OpenAI integration
   - Start/end analysis sessions
   - Upload restaurant data to AI assistant
   - Ask natural language questions about your data
2. **Dashboard**: Overview with key metrics and data summaries
3. **Individual Table Pages**: 
   - Select any table from the sidebar
   - Use the search box to filter data
   - Download tables as CSV files
   - View table statistics

### AI Analysis Features:
- **Natural Language Queries**: Ask questions like "What are the top-selling items?" or "Analyze customer satisfaction"
- **Code Interpreter**: AI can analyze data, create charts, and provide insights
- **Session Management**: Upload data once per session for multiple analyses

## 🔧 Features

- **Real-time Data**: All tables are loaded dynamically
- **Interactive Filtering**: Search across all columns
- **Currency Formatting**: Automatic formatting for financial data
- **Responsive Layout**: Adapts to different screen sizes
- **Error Handling**: Graceful handling of missing files

## 📈 Key Metrics Displayed

- Total Orders
- Total Sales Revenue
- Average Ticket Size  
- Total Cost of Goods Sold (COGS)

## ☁️ Streamlit Cloud Deployment

### Setting up API Key in Streamlit Cloud:

1. **Deploy your app** to Streamlit Cloud
2. **Go to your app dashboard** and click on your app
3. **Navigate to Settings** → **Secrets**
4. **Add your secrets** in TOML format:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
5. **Save and redeploy** your app

### Important Notes:
- Use **Streamlit Secrets** for Streamlit Cloud deployment
- Use **System Environment Variables** for local development
- The app will automatically detect and use available API key sources

## 🎯 Use Cases

- Restaurant management and operations monitoring
- Financial analysis and reporting
- Staff performance tracking
- Inventory management
- Customer relationship management
- Marketing campaign analysis

## 📊 Data Integration

All data modules are fully integrated:
- Menu items match POS sales
- Inventory usage aligns with orders
- Servers appear across multiple modules
- Financial metrics calculated from actual transactions

---

**Built with ❤️ using Streamlit and Pandas**
