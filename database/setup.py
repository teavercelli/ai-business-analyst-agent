import sqlite3
import random
from datetime import datetime, timedelta


# =========================================================
# CONFIGURAZIONE
# =========================================================

# Rende il dataset riproducibile:
# ogni volta che eseguiamo setup.py otteniamo gli stessi dati.
random.seed(42)

DB_PATH = "database/business.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


# =========================================================
# CREAZIONE TABELLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    country TEXT,
    segment TEXT,
    signup_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_cost REAL,
    unit_price REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    channel TEXT,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    unit_cost REAL,
    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS investigations (
    investigation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    country TEXT,
    metric TEXT,
    previous_value REAL,
    current_value REAL,
    change REAL,
    report TEXT,
    status TEXT
)
""")


# =========================================================
# PULIZIA DATI PRECEDENTI
# =========================================================

cursor.execute("DELETE FROM order_items")
cursor.execute("DELETE FROM orders")
cursor.execute("DELETE FROM customers")
cursor.execute("DELETE FROM products")
cursor.execute("DELETE FROM investigations")


# =========================================================
# PRODOTTI
# =========================================================

products = [
    (1, "Laptop Pro", "Computers", 700, 1100),
    (2, "Laptop Air", "Computers", 500, 800),
    (3, "Smartphone Pro", "Phones", 420, 700),
    (4, "Smartphone Lite", "Phones", 220, 400),
    (5, "Tablet", "Tablets", 300, 500),
    (6, "Wireless Headphones", "Accessories", 60, 130),
    (7, "Smartwatch", "Wearables", 110, 250),
    (8, "Wireless Mouse", "Accessories", 15, 45)
]

cursor.executemany("""
INSERT INTO products (
    product_id,
    product_name,
    category,
    unit_cost,
    unit_price
)
VALUES (?, ?, ?, ?, ?)
""", products)


# =========================================================
# CLIENTI
# =========================================================

countries = [
    "Italy",
    "Spain",
    "France",
    "Germany",
    "United Kingdom"
]

segments = [
    "Consumer",
    "Small Business",
    "Enterprise"
]

customers = []

for customer_id in range(1, 1001):

    country = random.choice(countries)
    segment = random.choice(segments)

    signup_date = (
        datetime(2024, 1, 1)
        + timedelta(days=random.randint(0, 900))
    ).date()

    customers.append(
        (
            customer_id,
            country,
            segment,
            str(signup_date)
        )
    )


cursor.executemany("""
INSERT INTO customers (
    customer_id,
    country,
    segment,
    signup_date
)
VALUES (?, ?, ?, ?)
""", customers)


# =========================================================
# ORDINI
# =========================================================

channels = [
    "Website",
    "Marketplace",
    "Sales Team"
]

orders = []
order_items = []

start_date = datetime(2025, 1, 1)


# =========================================================
# GENERAZIONE 10.000 ORDINI
# =========================================================

for order_id in range(1, 10001):

    customer_id = random.randint(1, 1000)

    order_date = (
        start_date
        + timedelta(days=random.randint(0, 635))
    ).date()

    channel = random.choice(channels)

    # Recuperiamo informazioni sul cliente originale
    customer_country = customers[customer_id - 1][1]
    customer_segment = customers[customer_id - 1][2]


    # -----------------------------------------------------
    # ANOMALIA 2
    #
    # GERMANY MARKETPLACE SLOWDOWN
    #
    # Da luglio 2026, circa il 65% degli ordini tedeschi
    # che sarebbero arrivati tramite Marketplace vengono
    # spostati su Website.
    #
    # Risultato atteso:
    # Marketplace Germany ↓
    # Website Germany ↑
    # -----------------------------------------------------

    if (
        customer_country == "Germany"
        and channel == "Marketplace"
        and order_date >= datetime(2026, 7, 1).date()
    ):
        if random.random() < 0.65:
            channel = "Website"


    # -----------------------------------------------------
    # ANOMALIA 3
    #
    # UK ENTERPRISE SLOWDOWN
    #
    # Da luglio 2026, circa il 60% degli ordini che
    # appartengono al segmento Enterprise UK viene
    # riassegnato a clienti UK non-Enterprise.
    #
    # Risultato atteso:
    # UK Enterprise orders ↓
    # UK Enterprise active customers ↓
    # -----------------------------------------------------

    if (
        customer_country == "United Kingdom"
        and customer_segment == "Enterprise"
        and order_date >= datetime(2026, 7, 1).date()
    ):

        if random.random() < 0.60:

            eligible_customers = [
                customer[0]
                for customer in customers
                if customer[1] == "United Kingdom"
                and customer[2] != "Enterprise"
            ]

            customer_id = random.choice(
                eligible_customers
            )

            # Aggiorniamo le informazioni del cliente
            # dopo aver cambiato customer_id.
            customer_country = customers[customer_id - 1][1]
            customer_segment = customers[customer_id - 1][2]


    # -----------------------------------------------------
    # SALVIAMO L'ORDINE
    # -----------------------------------------------------

    orders.append(
        (
            order_id,
            customer_id,
            str(order_date),
            channel
        )
    )


    # =====================================================
    # PRODOTTI CONTENUTI NELL'ORDINE
    # =====================================================

    number_items = random.randint(1, 4)

    for _ in range(number_items):

        product = random.choice(products)

        product_id = product[0]
        unit_cost = product[3]
        unit_price = product[4]

        quantity = random.randint(1, 3)


        # -------------------------------------------------
        # ANOMALIA 1
        #
        # SPAIN — LAPTOP PRO COST INCREASE
        #
        # Da luglio 2026 il costo del Laptop Pro
        # venduto in Spagna aumenta del 45%.
        #
        # €700 → €1.015
        #
        # Il prezzo rimane €1.100.
        #
        # Risultato atteso:
        # gross margin Laptop Pro Spain ↓
        # -------------------------------------------------

        if (
            customer_country == "Spain"
            and product_id == 1
            and order_date >= datetime(2026, 7, 1).date()
        ):
            unit_cost = unit_cost * 1.45


        # -------------------------------------------------
        # AGGIUNGIAMO IL PRODOTTO ALL'ORDINE
        # -------------------------------------------------

        order_items.append(
            (
                order_id,
                product_id,
                quantity,
                unit_price,
                unit_cost
            )
        )


# =========================================================
# INSERIMENTO ORDINI NEL DATABASE
# =========================================================

cursor.executemany("""
INSERT INTO orders (
    order_id,
    customer_id,
    order_date,
    channel
)
VALUES (?, ?, ?, ?)
""", orders)


# =========================================================
# INSERIMENTO ORDER ITEMS
# =========================================================

cursor.executemany("""
INSERT INTO order_items (
    order_id,
    product_id,
    quantity,
    unit_price,
    unit_cost
)
VALUES (?, ?, ?, ?, ?)
""", order_items)


# =========================================================
# SALVATAGGIO
# =========================================================

conn.commit()
conn.close()


# =========================================================
# CONTROLLO
# =========================================================

print("Database creato con successo!")
print("Clienti:", len(customers))
print("Ordini:", len(orders))
print("Righe ordine:", len(order_items))

print("\nAnomalie nascoste inserite:")
print("1. Spain -> Laptop Pro -> unit cost +45%")
print("2. Germany -> Marketplace -> slowdown")
print("3. United Kingdom -> Enterprise -> slowdown")