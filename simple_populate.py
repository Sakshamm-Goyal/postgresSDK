#!/usr/bin/env python3
"""
Simple script to populate the PostgreSQL database with 10,000+ records for an impressive demo.
This script adds data without clearing existing data to avoid foreign key constraint issues.
"""

import psycopg2
import random
import uuid
from datetime import datetime, timedelta
import json

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "sample_db"
}

def get_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)

def add_users():
    """Add users to the database."""
    print("👥 Adding 500 users...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        users_data = []
        for i in range(500):
            users_data.append((
                f"user{i+1:04d}",  # username
                f"user{i+1:04d}@example.com",  # email
                f"User{i+1:04d}",  # first_name
                f"LastName{i+1:04d}",  # last_name
                random.choice(['customer', 'admin', 'moderator']),  # role
                datetime.now() - timedelta(days=random.randint(0, 1000))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO ecommerce.users (username, email, first_name, last_name, role, created_at) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
            users_data
        )
        
        conn.commit()
        print("  ✅ Users added successfully!")
        
    except Exception as e:
        print(f"  ❌ Error adding users: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_categories():
    """Add categories to the database."""
    print("📂 Adding 50 categories...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        category_names = [
            'Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports',
            'Beauty', 'Toys', 'Automotive', 'Health', 'Food & Beverage',
            'Jewelry', 'Furniture', 'Office Supplies', 'Pet Supplies', 'Travel',
            'Music', 'Movies', 'Gaming', 'Art & Crafts', 'Baby & Kids',
            'Tools', 'Outdoor', 'Kitchen', 'Bathroom', 'Bedroom',
            'Living Room', 'Dining', 'Lighting', 'Storage', 'Decor',
            'Garden Tools', 'Seeds', 'Plants', 'Fertilizers', 'Pest Control',
            'Fitness', 'Yoga', 'Running', 'Cycling', 'Swimming',
            'Team Sports', 'Individual Sports', 'Water Sports', 'Winter Sports', 'Adventure',
            'Makeup', 'Skincare', 'Hair Care', 'Fragrance', 'Personal Care'
        ]
        
        categories_data = []
        for name in category_names:
            categories_data.append((
                name,  # name
                f"Description for {name} category",  # description
                datetime.now() - timedelta(days=random.randint(0, 1000))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO ecommerce.categories (name, description, created_at) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            categories_data
        )
        
        conn.commit()
        print("  ✅ Categories added successfully!")
        
    except Exception as e:
        print(f"  ❌ Error adding categories: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_products():
    """Add products to the database."""
    print("🛍️ Adding 2,000 products...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get category IDs
        cursor.execute("SELECT id FROM ecommerce.categories")
        category_ids = [row[0] for row in cursor.fetchall()]
        
        if not category_ids:
            print("  ⚠️ No categories found, creating a default category...")
            cursor.execute("INSERT INTO ecommerce.categories (name, description, created_at) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                         ('Default Category', 'Default category for products', datetime.now()))
            cursor.execute("SELECT id FROM ecommerce.categories WHERE name = 'Default Category'")
            category_ids = [cursor.fetchone()[0]]
        
        products_data = []
        for i in range(2000):
            products_data.append((
                f"Product {i+1}",  # name
                f"High-quality {random.choice(['premium', 'standard', 'deluxe', 'basic'])} product {i+1}",  # description
                f"SKU-{i+1:08d}",  # sku
                round(random.uniform(5.0, 500.0), 2),  # price
                round(random.uniform(2.0, 250.0), 2),  # cost
                random.choice(category_ids),  # category_id
                random.randint(0, 1000),  # stock_quantity
                round(random.uniform(0.1, 5.0), 2),  # weight
                datetime.now() - timedelta(days=random.randint(0, 1000))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO ecommerce.products (name, description, sku, price, cost, category_id, stock_quantity, weight, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (sku) DO NOTHING",
            products_data
        )
        
        conn.commit()
        print("  ✅ Products added successfully!")
        
    except Exception as e:
        print(f"  ❌ Error adding products: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_addresses():
    """Add addresses to the database."""
    print("🏠 Adding 1,000 addresses...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user IDs
        cursor.execute("SELECT id FROM ecommerce.users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not user_ids:
            print("  ⚠️ No users found, creating a default user...")
            cursor.execute("INSERT INTO ecommerce.users (username, email, first_name, last_name, role, created_at) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING", 
                         ('defaultuser', 'default@example.com', 'Default', 'User', 'customer', datetime.now()))
            cursor.execute("SELECT id FROM ecommerce.users WHERE username = 'defaultuser'")
            user_ids = [cursor.fetchone()[0]]
        
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
        states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA']
        
        addresses_data = []
        for i in range(1000):
            city_idx = random.randint(0, len(cities)-1)
            addresses_data.append((
                random.choice(user_ids),  # user_id
                f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Maple', 'Cedar', 'Birch', 'Willow'])} St",  # street_address
                cities[city_idx],  # city
                states[city_idx],  # state
                f"{random.randint(10000, 99999)}",  # zip_code
                random.choice(['US', 'CA', 'MX', 'UK', 'DE', 'FR', 'IT', 'ES', 'AU', 'JP']),  # country
                datetime.now() - timedelta(days=random.randint(0, 1000))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO ecommerce.addresses (user_id, street_address, city, state, zip_code, country, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            addresses_data
        )
        
        conn.commit()
        print("  ✅ Addresses added successfully!")
        
    except Exception as e:
        print(f"  ❌ Error adding addresses: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_orders():
    """Add orders to the database."""
    print("📦 Adding 1,500 orders...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user and address IDs
        cursor.execute("SELECT id FROM ecommerce.users")
        user_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM ecommerce.addresses")
        address_ids = [row[0] for row in cursor.fetchall()]
        
        orders_data = []
        for i in range(1500):
            orders_data.append((
                random.choice(user_ids),  # user_id
                random.choice(address_ids),  # shipping_address_id
                random.choice(address_ids),  # billing_address_id
                round(random.uniform(10.0, 2000.0), 2),  # total_amount
                random.choice(['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']),  # status
                random.choice(['Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery']),  # payment_method
                datetime.now() - timedelta(days=random.randint(0, 365))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO ecommerce.orders (user_id, shipping_address_id, billing_address_id, total_amount, status, payment_method, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            orders_data
        )
        
        conn.commit()
        print("  ✅ Orders added successfully!")
        
    except Exception as e:
        print(f"  ❌ Error adding orders: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_order_items():
    """Add order items to the database."""
    print("🛒 Adding 3,000 order items...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get order and product IDs
        cursor.execute("SELECT id FROM ecommerce.orders")
        order_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM ecommerce.products")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        order_items_data = []
        for i in range(3000):
            order_items_data.append((
                random.choice(order_ids),  # order_id
                random.choice(product_ids),  # product_id
                random.randint(1, 10),  # quantity
                round(random.uniform(5.0, 500.0), 2),  # unit_price
                round(random.uniform(0.0, 0.2), 3),  # discount_rate
                datetime.now() - timedelta(days=random.randint(0, 365))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO ecommerce.order_items (order_id, product_id, quantity, unit_price, discount_rate, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            order_items_data
        )
        
        conn.commit()
        print("  ✅ Order items added successfully!")
        
    except Exception as e:
        print(f"  ❌ Error adding order items: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_analytics_data():
    """Add analytics data to the database."""
    print("📊 Adding analytics data...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user and product IDs
        cursor.execute("SELECT id FROM ecommerce.users")
        user_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM ecommerce.products")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        # Add product views (5,000 records)
        print("  📈 Adding 5,000 product views...")
        product_views_data = []
        for i in range(5000):
            product_views_data.append((
                random.choice(product_ids),  # product_id
                random.choice(user_ids),   # user_id
                random.randint(1, 300),   # view_duration
                f"https://example.com/product/{random.randint(1, 1000)}",  # referrer_url
                datetime.now() - timedelta(days=random.randint(0, 365))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO analytics.product_views (product_id, user_id, view_duration, referrer_url, created_at) VALUES (%s, %s, %s, %s, %s)",
            product_views_data
        )
        
        # Add user events (3,000 records)
        print("  🎯 Adding 3,000 user events...")
        event_types = ['page_view', 'click', 'scroll', 'hover', 'purchase', 'add_to_cart', 'search']
        user_events_data = []
        for i in range(3000):
            user_events_data.append((
                random.choice(user_ids),   # user_id
                random.choice(event_types),  # event_type
                json.dumps({
                    'page': f'/product/{random.randint(1, 1000)}',
                    'session_id': str(uuid.uuid4()),
                    'device': random.choice(['desktop', 'mobile', 'tablet']),
                    'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
                }),  # event_data
                datetime.now() - timedelta(days=random.randint(0, 365))  # created_at
            ))
        
        cursor.executemany(
            "INSERT INTO analytics.user_events (user_id, event_type, event_data, created_at) VALUES (%s, %s, %s, %s)",
            user_events_data
        )
        
        # Add sales summary (2,000 records)
        print("  💰 Adding 2,000 sales summaries...")
        sales_summary_data = []
        for i in range(2000):
            sales_summary_data.append((
                f"SUM-{i+1:06d}",  # summary_id
                random.choice(product_ids),  # product_id
                random.randint(1, 100),   # total_quantity
                round(random.uniform(10.0, 1000.0), 2),  # total_revenue
                random.randint(1, 50),    # unique_customers
                datetime.now() - timedelta(days=random.randint(0, 30))  # summary_date
            ))
        
        cursor.executemany(
            "INSERT INTO analytics.sales_summary (summary_id, product_id, total_quantity, total_revenue, unique_customers, summary_date) VALUES (%s, %s, %s, %s, %s, %s)",
            sales_summary_data
        )
        
        conn.commit()
        print("  ✅ Analytics data added successfully!")
        
    except Exception as e:
        print(f"  ❌ Error adding analytics data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_table_counts():
    """Get current table counts."""
    print("\n📊 Current Database Statistics:")
    print("-" * 40)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    tables = [
        ('ecommerce.users', 'Users'),
        ('ecommerce.categories', 'Categories'),
        ('ecommerce.products', 'Products'),
        ('ecommerce.addresses', 'Addresses'),
        ('ecommerce.orders', 'Orders'),
        ('ecommerce.order_items', 'Order Items'),
        ('analytics.product_views', 'Product Views'),
        ('analytics.user_events', 'User Events'),
        ('analytics.sales_summary', 'Sales Summary')
    ]
    
    for table, name in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {name}: {count:,} records")
        except Exception as e:
            print(f"  {name}: Error - {e}")
    
    cursor.close()
    conn.close()

def main():
    """Main function to populate the database."""
    print("🚀 Populating Database with 10,000+ Records for Impressive Demo")
    print("=" * 70)
    
    try:
        # Add data in the correct order to respect foreign key constraints
        add_users()
        add_categories()
        add_products()
        add_addresses()
        add_orders()
        add_order_items()
        add_analytics_data()
        
        # Show final statistics
        get_table_counts()
        
        print("\n✅ Database population completed successfully!")
        print("🎉 Ready for an impressive metadata extraction demo!")
        
    except Exception as e:
        print(f"\n❌ Error during database population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
