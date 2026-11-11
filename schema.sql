-- יוצרים את מסד poc פעם אחת ב-pgAdmin, לפני הרצת הקובץ הזה.
-- הטבלאות משמשות רק לפרויקט POC. הפעלה חוזרת לא מוחקת הזמנות.
CREATE TABLE IF NOT EXISTS products (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price > 0),
    icon TEXT NOT NULL DEFAULT 'cake',
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price > 0),
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 20),
    fulfillment TEXT NOT NULL CHECK (fulfillment IN ('delivery', 'pickup')),
    address VARCHAR(300) NOT NULL DEFAULT '',
    due_date DATE NOT NULL,
    notes VARCHAR(500) NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN
        ('new','preparing','ready','out_for_delivery','delivered','collected','cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (fulfillment <> 'delivery' OR LENGTH(TRIM(address)) > 0),
    CHECK (fulfillment <> 'pickup' OR status NOT IN ('out_for_delivery', 'delivered')),
    CHECK (fulfillment <> 'delivery' OR status <> 'collected')
);

INSERT INTO products (name, description, price, icon) VALUES
('עוגת שוקולד', 'עוגת שוקולד עשירה בציפוי גנאש. קוטר 24 ס״מ.', 140, 'chocolate'),
('עוגת גבינה', 'עוגת גבינה אפויה עם בסיס פריך. קוטר 24 ס״מ.', 160, 'cheese'),
('עוגת תותים', 'עוגת וניל, קצפת ותותים. קוטר 24 ס״מ.', 180, 'strawberry')
ON CONFLICT (name) DO NOTHING;
