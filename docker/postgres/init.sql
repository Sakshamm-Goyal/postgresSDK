-- SourceSense PostgreSQL Sample Database
-- This script creates a comprehensive sample database for demonstrating
-- SourceSense's metadata extraction capabilities

-- Create schemas
CREATE SCHEMA IF NOT EXISTS ecommerce;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS reporting;

-- Set search path
SET search_path TO ecommerce, analytics, reporting, public;

-- Create custom types
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE user_role AS ENUM ('customer', 'admin', 'moderator');

-- Create tables in ecommerce schema
CREATE TABLE ecommerce.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role user_role DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE TABLE ecommerce.categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES ecommerce.categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE ecommerce.products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    sku VARCHAR(50) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    cost DECIMAL(10,2) CHECK (cost >= 0),
    category_id INTEGER REFERENCES ecommerce.categories(id),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    weight DECIMAL(8,2),
    dimensions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE ecommerce.orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES ecommerce.users(id) ON DELETE CASCADE,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    status order_status DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    tax_amount DECIMAL(10,2) DEFAULT 0 CHECK (tax_amount >= 0),
    shipping_amount DECIMAL(10,2) DEFAULT 0 CHECK (shipping_amount >= 0),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_date TIMESTAMP,
    delivered_date TIMESTAMP,
    notes TEXT
);

CREATE TABLE ecommerce.order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES ecommerce.orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES ecommerce.products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ecommerce.addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES ecommerce.users(id) ON DELETE CASCADE,
    type VARCHAR(20) DEFAULT 'shipping' CHECK (type IN ('shipping', 'billing')),
    street_address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50) NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tables in analytics schema
CREATE TABLE analytics.user_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES ecommerce.users(id),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analytics.product_views (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES ecommerce.products(id),
    user_id INTEGER REFERENCES ecommerce.users(id),
    view_duration INTEGER, -- in seconds
    referrer_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analytics.sales_summary (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_revenue DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_products_sold INTEGER NOT NULL DEFAULT 0,
    average_order_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- Create tables in reporting schema
CREATE TABLE reporting.daily_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(100)
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON ecommerce.users(email);
CREATE INDEX idx_users_username ON ecommerce.users(username);
CREATE INDEX idx_products_category ON ecommerce.products(category_id);
CREATE INDEX idx_products_sku ON ecommerce.products(sku);
CREATE INDEX idx_orders_user ON ecommerce.orders(user_id);
CREATE INDEX idx_orders_date ON ecommerce.orders(order_date);
CREATE INDEX idx_orders_status ON ecommerce.orders(status);
CREATE INDEX idx_order_items_order ON ecommerce.order_items(order_id);
CREATE INDEX idx_order_items_product ON ecommerce.order_items(product_id);
CREATE INDEX idx_user_events_user ON analytics.user_events(user_id);
CREATE INDEX idx_user_events_type ON analytics.user_events(event_type);
CREATE INDEX idx_user_events_created ON analytics.user_events(created_at);
CREATE INDEX idx_product_views_product ON analytics.product_views(product_id);
CREATE INDEX idx_product_views_user ON analytics.product_views(user_id);
CREATE INDEX idx_sales_summary_date ON analytics.sales_summary(date);

-- Create views for business intelligence
CREATE VIEW ecommerce.product_sales_summary AS
SELECT 
    p.id,
    p.name,
    p.sku,
    p.price,
    c.name as category_name,
    COUNT(oi.id) as total_orders,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as average_selling_price
FROM ecommerce.products p
LEFT JOIN ecommerce.order_items oi ON p.id = oi.product_id
LEFT JOIN ecommerce.categories c ON p.category_id = c.id
GROUP BY p.id, p.name, p.sku, p.price, c.name;

CREATE VIEW ecommerce.user_order_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as average_order_value,
    MAX(o.order_date) as last_order_date
FROM ecommerce.users u
LEFT JOIN ecommerce.orders o ON u.id = o.user_id
GROUP BY u.id, u.username, u.email, u.first_name, u.last_name;

-- Create materialized view for performance
CREATE MATERIALIZED VIEW analytics.daily_sales_mv AS
SELECT 
    DATE(o.order_date) as sale_date,
    COUNT(DISTINCT o.id) as order_count,
    COUNT(oi.id) as item_count,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.total_price) as average_order_value
FROM ecommerce.orders o
JOIN ecommerce.order_items oi ON o.id = oi.order_id
WHERE o.status != 'cancelled'
GROUP BY DATE(o.order_date)
ORDER BY sale_date;

-- Create refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_daily_sales()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW analytics.daily_sales_mv;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data
INSERT INTO ecommerce.categories (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Books', 'Books and educational materials'),
('Home & Garden', 'Home improvement and garden supplies');

INSERT INTO ecommerce.users (username, email, first_name, last_name, role) VALUES
('john_doe', 'john.doe@example.com', 'John', 'Doe', 'customer'),
('jane_smith', 'jane.smith@example.com', 'Jane', 'Smith', 'customer'),
('admin_user', 'admin@example.com', 'Admin', 'User', 'admin'),
('moderator1', 'mod@example.com', 'Mod', 'User', 'moderator');

INSERT INTO ecommerce.products (name, description, sku, price, cost, category_id, stock_quantity) VALUES
('Laptop Computer', 'High-performance laptop for business use', 'LAPTOP001', 1299.99, 800.00, 1, 50),
('Wireless Mouse', 'Ergonomic wireless mouse', 'MOUSE001', 29.99, 15.00, 1, 200),
('T-Shirt', 'Comfortable cotton t-shirt', 'TSHIRT001', 19.99, 8.00, 2, 100),
('Programming Book', 'Learn Python programming', 'BOOK001', 49.99, 25.00, 3, 75),
('Garden Tools Set', 'Complete garden maintenance kit', 'GARDEN001', 89.99, 45.00, 4, 30);

INSERT INTO ecommerce.orders (user_id, order_number, status, total_amount, tax_amount, shipping_amount) VALUES
(1, 'ORD-001', 'delivered', 1329.98, 106.40, 15.00),
(2, 'ORD-002', 'shipped', 69.98, 5.60, 10.00),
(1, 'ORD-003', 'processing', 89.99, 7.20, 12.00);

INSERT INTO ecommerce.order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
(2, 3, 2, 19.99),
(2, 4, 1, 49.99),
(3, 5, 1, 89.99);

-- Insert sample analytics data
INSERT INTO analytics.user_events (user_id, event_type, event_data, session_id) VALUES
(1, 'page_view', '{"page": "/products/laptop", "duration": 45}', 'sess_001'),
(1, 'add_to_cart', '{"product_id": 1, "quantity": 1}', 'sess_001'),
(2, 'page_view', '{"page": "/products/tshirt", "duration": 30}', 'sess_002'),
(2, 'purchase', '{"order_id": 2, "total": 69.98}', 'sess_002');

INSERT INTO analytics.product_views (product_id, user_id, view_duration, referrer_url) VALUES
(1, 1, 45, 'https://google.com'),
(2, 1, 20, 'https://google.com'),
(3, 2, 30, 'https://facebook.com'),
(4, 2, 25, 'https://facebook.com');

-- Insert sample reporting data
INSERT INTO reporting.daily_reports (report_date, report_type, data, generated_by) VALUES
(CURRENT_DATE, 'sales_summary', '{"total_orders": 3, "total_revenue": 1490.95, "top_product": "Laptop Computer"}', 'system'),
(CURRENT_DATE - INTERVAL '1 day', 'user_activity', '{"active_users": 2, "page_views": 15, "conversion_rate": 0.15}', 'system');

-- Add comments and descriptions for business context
COMMENT ON TABLE ecommerce.users IS 'Customer and user account information';
COMMENT ON TABLE ecommerce.products IS 'Product catalog with pricing and inventory';
COMMENT ON TABLE ecommerce.orders IS 'Customer orders and transaction records';
COMMENT ON TABLE ecommerce.order_items IS 'Individual items within each order';
COMMENT ON TABLE analytics.user_events IS 'User interaction and behavior tracking';
COMMENT ON TABLE analytics.product_views IS 'Product page view analytics';
COMMENT ON TABLE reporting.daily_reports IS 'Generated daily business reports';

COMMENT ON COLUMN ecommerce.users.email IS 'Primary contact email address';
COMMENT ON COLUMN ecommerce.products.price IS 'Selling price in USD';
COMMENT ON COLUMN ecommerce.orders.total_amount IS 'Total order value including tax and shipping';
COMMENT ON COLUMN analytics.user_events.event_data IS 'JSON payload containing event-specific data';

-- Create a function to demonstrate PostgreSQL features
CREATE OR REPLACE FUNCTION ecommerce.calculate_order_total(order_id INTEGER)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total DECIMAL(10,2);
BEGIN
    SELECT SUM(oi.total_price) INTO total
    FROM ecommerce.order_items oi
    WHERE oi.order_id = calculate_order_total.order_id;
    
    RETURN COALESCE(total, 0);
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT USAGE ON SCHEMA ecommerce, analytics, reporting TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ecommerce, analytics, reporting TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ecommerce, analytics, reporting TO postgres;

