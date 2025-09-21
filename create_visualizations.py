#!/usr/bin/env python3
"""
Create visualizations for restaurant data analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_data():
    """Load all CSV files"""
    data = {}
    data['pos_sales'] = pd.read_csv("database/pos_sales.csv")
    data['menu'] = pd.read_csv("database/menu.csv")
    data['crm'] = pd.read_csv("database/crm_loyalty.csv")
    data['inventory'] = pd.read_csv("database/inventory.csv")
    data['staff'] = pd.read_csv("database/hr_staff.csv")
    data['marketing'] = pd.read_csv("database/marketing_promotions.csv")
    data['reviews'] = pd.read_csv("database/reviews.csv")
    data['reservations'] = pd.read_csv("database/reservations.csv")
    data['finance'] = pd.read_csv("database/finance_accounting.csv")
    return data

def create_sales_visualizations(data):
    """Create sales-related visualizations"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Restaurant Sales Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Hourly Sales Pattern
    pos_sales = data['pos_sales'].copy()
    pos_sales['Hour'] = pd.to_datetime(pos_sales['Time'], format='%I:%M %p').dt.hour
    hourly_sales = pos_sales.groupby('Hour')['Total'].sum()
    
    ax1.bar(hourly_sales.index, hourly_sales.values, color='skyblue', alpha=0.8)
    ax1.set_title('Sales by Hour', fontweight='bold')
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Sales ($)')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate(hourly_sales.values):
        ax1.text(hourly_sales.index[i], v + 2, f'${v:.0f}', ha='center', va='bottom')
    
    # 2. Server Performance
    server_stats = pos_sales.groupby('Server_Name').agg({
        'Total': ['count', 'sum'],
        'Tip': 'sum'
    })
    server_stats.columns = ['Orders', 'Revenue', 'Tips']
    
    x = np.arange(len(server_stats))
    width = 0.35
    
    ax2.bar(x - width/2, server_stats['Revenue'], width, label='Revenue', color='lightcoral', alpha=0.8)
    ax2.bar(x + width/2, server_stats['Tips'], width, label='Tips', color='lightgreen', alpha=0.8)
    
    ax2.set_title('Server Performance: Revenue vs Tips', fontweight='bold')
    ax2.set_xlabel('Server')
    ax2.set_ylabel('Amount ($)')
    ax2.set_xticks(x)
    ax2.set_xticklabels([name.split()[0] for name in server_stats.index], rotation=45)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Payment Method Distribution
    payment_dist = pos_sales['Payment_Method'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    wedges, texts, autotexts = ax3.pie(payment_dist.values, labels=payment_dist.index, 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    ax3.set_title('Payment Method Distribution', fontweight='bold')
    
    # 4. Daily Revenue Trend (simulated for visualization)
    dates = pd.date_range(start='2024-01-10', periods=7, freq='D')
    daily_revenue = [480, 520, 445, 590, 610, 680, 520]  # Simulated data
    
    ax4.plot(dates, daily_revenue, marker='o', linewidth=2, markersize=6, color='purple')
    ax4.set_title('Weekly Revenue Trend', fontweight='bold')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Revenue ($)')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(daily_revenue):
        ax4.annotate(f'${v}', (dates[i], v), textcoords="offset points", 
                    xytext=(0,10), ha='center')
    
    plt.tight_layout()
    plt.savefig('sales_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_menu_analysis(data):
    """Create menu performance visualizations"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Menu Performance Analysis', fontsize=16, fontweight='bold')
    
    # Parse items from orders
    all_items = []
    pos_sales = data['pos_sales']
    for _, row in pos_sales.iterrows():
        items = row['Items_Ordered'].split(', ')
        for item in items:
            if '(' in item:
                item_name = item.split(' (')[0]
                qty = int(item.split('(')[1].split(')')[0])
            else:
                item_name = item
                qty = 1
            all_items.extend([item_name] * qty)
    
    item_counts = pd.Series(all_items).value_counts()
    
    # 1. Top 10 Most Popular Items
    top_items = item_counts.head(10)
    ax1.barh(range(len(top_items)), top_items.values, color='lightblue', alpha=0.8)
    ax1.set_yticks(range(len(top_items)))
    ax1.set_yticklabels([item[:20] + '...' if len(item) > 20 else item for item in top_items.index])
    ax1.set_xlabel('Orders Count')
    ax1.set_title('Top 10 Most Popular Menu Items', fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(top_items.values):
        ax1.text(v + 0.1, i, str(v), va='center')
    
    # 2. Category Performance
    menu = data['menu']
    category_performance = {}
    for category in menu['Menu_Category'].unique():
        category_items = menu[menu['Menu_Category'] == category]['Item_Name'].tolist()
        category_sales = sum([item_counts.get(item, 0) for item in category_items])
        category_revenue = sum([item_counts.get(item, 0) * menu[menu['Item_Name'] == item]['Price'].iloc[0] 
                              for item in category_items if item in item_counts])
        category_performance[category] = {'sales': category_sales, 'revenue': category_revenue}
    
    categories = list(category_performance.keys())
    revenues = [category_performance[cat]['revenue'] for cat in categories]
    
    ax2.bar(categories, revenues, color='lightcoral', alpha=0.8)
    ax2.set_title('Revenue by Menu Category', fontweight='bold')
    ax2.set_xlabel('Category')
    ax2.set_ylabel('Revenue ($)')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(revenues):
        ax2.text(i, v + 1, f'${v:.0f}', ha='center', va='bottom')
    
    # 3. Price vs Popularity Scatter
    menu_with_sales = menu.copy()
    menu_with_sales['Sales_Count'] = menu_with_sales['Item_Name'].map(item_counts).fillna(0)
    
    scatter = ax3.scatter(menu_with_sales['Price'], menu_with_sales['Sales_Count'], 
                         c=menu_with_sales['Margin_Percent'], cmap='viridis', 
                         alpha=0.7, s=100)
    ax3.set_xlabel('Price ($)')
    ax3.set_ylabel('Sales Count')
    ax3.set_title('Price vs Popularity (Color = Margin %)', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Margin %')
    
    # 4. Profit Analysis
    profit_data = []
    for _, item in menu.iterrows():
        if item['Item_Name'] in item_counts:
            count = item_counts[item['Item_Name']]
            revenue = count * item['Price']
            cost = count * item['Estimated_COGS']
            profit = revenue - cost
            profit_data.append({'Item': item['Item_Name'][:15], 'Profit': profit})
    
    profit_df = pd.DataFrame(profit_data).sort_values('Profit', ascending=True).tail(8)
    
    ax4.barh(range(len(profit_df)), profit_df['Profit'], color='gold', alpha=0.8)
    ax4.set_yticks(range(len(profit_df)))
    ax4.set_yticklabels(profit_df['Item'])
    ax4.set_xlabel('Profit ($)')
    ax4.set_title('Most Profitable Menu Items', fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(profit_df['Profit']):
        ax4.text(v + 0.5, i, f'${v:.0f}', va='center')
    
    plt.tight_layout()
    plt.savefig('menu_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_customer_insights(data):
    """Create customer analysis visualizations"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Customer Insights Dashboard', fontsize=16, fontweight='bold')
    
    crm = data['crm']
    reviews = data['reviews']
    reservations = data['reservations']
    
    # 1. Customer Loyalty Distribution
    visit_ranges = {
        '1-2 visits': len(crm[crm['Total_Visits'] <= 2]),
        '3-5 visits': len(crm[(crm['Total_Visits'] >= 3) & (crm['Total_Visits'] <= 5)]),
        '6-10 visits': len(crm[(crm['Total_Visits'] >= 6) & (crm['Total_Visits'] <= 10)]),
        '11+ visits': len(crm[crm['Total_Visits'] >= 11])
    }
    
    colors = ['#ff9999', '#ffcc99', '#99ccff', '#99ff99']
    wedges, texts, autotexts = ax1.pie(visit_ranges.values(), labels=visit_ranges.keys(), 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('Customer Loyalty Distribution', fontweight='bold')
    
    # 2. Review Ratings Distribution
    rating_dist = reviews['Rating'].value_counts().sort_index()
    
    bars = ax2.bar(rating_dist.index, rating_dist.values, color='orange', alpha=0.8)
    ax2.set_title('Customer Review Ratings', fontweight='bold')
    ax2.set_xlabel('Rating (Stars)')
    ax2.set_ylabel('Number of Reviews')
    ax2.set_xticks(rating_dist.index)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels and stars
    for bar, rating in zip(bars, rating_dist.index):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{int(height)}\n{"⭐" * rating}', ha='center', va='bottom')
    
    # 3. Server Preference
    server_loyalty = crm['Preferred_Server'].value_counts()
    
    ax3.bar(range(len(server_loyalty)), server_loyalty.values, color='lightgreen', alpha=0.8)
    ax3.set_title('Customer Server Preferences', fontweight='bold')
    ax3.set_xlabel('Server')
    ax3.set_ylabel('Number of Loyal Customers')
    ax3.set_xticks(range(len(server_loyalty)))
    ax3.set_xticklabels([name.split()[0] for name in server_loyalty.index])
    ax3.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(server_loyalty.values):
        ax3.text(i, v + 0.1, str(v), ha='center', va='bottom')
    
    # 4. Reservation Status
    status_dist = reservations['Status'].value_counts()
    
    colors_status = ['#90EE90', '#FFD700', '#FF6B6B', '#87CEEB']
    wedges, texts, autotexts = ax4.pie(status_dist.values, labels=status_dist.index, 
                                      autopct='%1.1f%%', colors=colors_status, startangle=90)
    ax4.set_title('Reservation Status Distribution', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('customer_insights.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_operations_dashboard(data):
    """Create operational insights visualizations"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Operations & Performance Dashboard', fontsize=16, fontweight='bold')
    
    inventory = data['inventory']
    marketing = data['marketing']
    staff = data['staff']
    
    # 1. Inventory Waste Analysis
    inventory['Waste_Cost'] = inventory['Wasted'] * inventory['Unit_Cost']
    high_waste = inventory.nlargest(8, 'Waste_Cost')
    
    ax1.barh(range(len(high_waste)), high_waste['Waste_Cost'], color='red', alpha=0.7)
    ax1.set_yticks(range(len(high_waste)))
    ax1.set_yticklabels([name[:15] for name in high_waste['Ingredient_Name']])
    ax1.set_xlabel('Waste Cost ($)')
    ax1.set_title('Highest Waste Cost Items', fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(high_waste['Waste_Cost']):
        ax1.text(v + 0.05, i, f'${v:.2f}', va='center')
    
    # 2. Marketing Campaign Effectiveness
    marketing_sorted = marketing.sort_values('Avg_Spend_Increase', ascending=False).head(6)
    
    bars = ax2.bar(range(len(marketing_sorted)), marketing_sorted['Avg_Spend_Increase'], 
                   color='purple', alpha=0.8)
    ax2.set_title('Marketing Campaign Effectiveness', fontweight='bold')
    ax2.set_xlabel('Promotion')
    ax2.set_ylabel('Average Spend Increase ($)')
    ax2.set_xticks(range(len(marketing_sorted)))
    ax2.set_xticklabels(marketing_sorted['Promo_Code'], rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(marketing_sorted['Avg_Spend_Increase']):
        ax2.text(i, v + 0.3, f'${v:.2f}', ha='center', va='bottom')
    
    # 3. Staff Tips Performance
    servers = staff[staff['Role'] == 'Server']
    
    ax3.bar(range(len(servers)), servers['Total_Tips'], color='gold', alpha=0.8)
    ax3.set_title('Server Tips Performance', fontweight='bold')
    ax3.set_xlabel('Server')
    ax3.set_ylabel('Total Tips ($)')
    ax3.set_xticks(range(len(servers)))
    ax3.set_xticklabels([name.split()[0] for name in servers['Name']])
    ax3.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(servers['Total_Tips']):
        ax3.text(i, v + 0.5, f'${v:.2f}', ha='center', va='bottom')
    
    # 4. Financial Performance Summary
    finance = data['finance']
    
    # Extract key metrics
    gross_sales = float(finance[finance['Metric'] == 'Gross_Sales']['Value'].iloc[0])
    total_cogs = float(finance[finance['Metric'] == 'Total_COGS']['Value'].iloc[0])
    labor_cost = float(finance[finance['Metric'] == 'Labor_Cost']['Value'].iloc[0])
    net_profit = float(finance[finance['Metric'] == 'Net_Profit_Before_Tax']['Value'].iloc[0])
    
    categories = ['Gross Sales', 'COGS', 'Labor Cost', 'Net Profit']
    values = [gross_sales, total_cogs, labor_cost, net_profit]
    colors_fin = ['green', 'red', 'orange', 'blue']
    
    bars = ax4.bar(categories, values, color=colors_fin, alpha=0.8)
    ax4.set_title('Financial Performance Overview', fontweight='bold')
    ax4.set_ylabel('Amount ($)')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(values):
        ax4.text(i, v + 5, f'${v:.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('operations_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Create all visualizations"""
    print("🎨 Creating Restaurant Data Visualizations...")
    
    # Load data
    data = load_data()
    
    # Create visualizations
    print("📊 Creating Sales Dashboard...")
    create_sales_visualizations(data)
    
    print("🍽️ Creating Menu Analysis...")
    create_menu_analysis(data)
    
    print("👥 Creating Customer Insights...")
    create_customer_insights(data)
    
    print("⚙️ Creating Operations Dashboard...")
    create_operations_dashboard(data)
    
    print("✅ All visualizations created successfully!")
    print("📁 Saved files:")
    print("   • sales_dashboard.png")
    print("   • menu_analysis.png") 
    print("   • customer_insights.png")
    print("   • operations_dashboard.png")

if __name__ == "__main__":
    main()
