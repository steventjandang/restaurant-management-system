import sqlite3 as sql
from datetime import datetime as dt

DATABASE = "restaurant.db"

TRUE = 1
FALSE = 0

def create_table():
    with sql.connect(DATABASE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS tables (table_id INTEGER, table_number INTEGER, table_capacity INTEGER, is_available INTEGER, PRIMARY KEY(table_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS reservations (reservation_id INTEGER, reserver_name TEXT NOT NULL, reservation_date NUMERIC, PRIMARY KEY(reservation_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS fnbs (fnb_id INTEGER, fnb_type TEXT NOT NULL, fnb_name TEXT NOT NULL, fnb_description TEXT NOT NULL, fnb_price Real, is_available INTEGER, PRIMARY KEY(fnb_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS orders (order_id INTEGER, reservation_id INTEGER, order_at NUMERIC, is_paid INTEGER, PRIMARY KEY(order_id), FOREIGN KEY(reservation_id) REFERENCES reservation(reservation_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS payments (payment_id INTEGER, order_id INTEGER, payment_type TEXT NOT NULL, total_price REAL, payment_date NUMERIC, PRIMARY KEY(payment_id), FOREIGN KEY(order_id) REFERENCES orders(order_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS table_reservation (table_reservation_id INTEGER, reservation_id INTEGER, table_id INTEGER, PRIMARY KEY(table_reservation_id), FOREIGN KEY(reservation_id) REFERENCES reservation(reservation_id), FOREIGN KEY(table_id) REFERENCES tables(table_id))")
        conn.execute("CREATE TABLE IF NOT EXISTS fnb_order (fnb_order_id INTEGER, order_id INTEGER, fnb_id INTEGER, fnb_quantity INTEGER, PRIMARY KEY(fnb_order_id), FOREIGN KEY(order_id) REFERENCES orders(order_id), FOREIGN KEY(fnb_id) REFERENCES fnbs(fnb_id))")

def add_table(table_number, table_capacity, is_available):
    with sql.connect(DATABASE) as conn:
        conn.execute("INSERT INTO tables (table_number, table_capacity, is_available) VALUES (?, ?, ?)", [table_number, table_capacity, is_available])

def edit_table(table_id, table_number, table_capacity, is_available):
    with sql.connect(DATABASE) as conn:
        conn.execute("UPDATE tables SET table_number=?, table_capacity=?, is_available=? WHERE table_id=?", [table_number, table_capacity, is_available, table_id])

def delete_table(table_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("DELETE FROM tables WHERE table_id=?", [table_id])

def add_fnb(fnb_type, fnb_name, fnb_description, fnb_price, is_available):
    with sql.connect(DATABASE) as conn:
        conn.execute("INSERT INTO fnbs (fnb_type, fnb_name, fnb_description, fnb_price, is_available) VALUES (?, ?, ?, ?, ?)", [fnb_type, fnb_name, fnb_description, fnb_price, is_available])

def edit_fnb(fnb_id, fnb_type, fnb_name, fnb_description, fnb_price, is_available):
    with sql.connect(DATABASE) as conn:
        conn.execute("UPDATE fnbs SET fnb_type=?, fnb_name=?, fnb_description=?, fnb_price=?, is_available=? WHERE fnb_id=?", [fnb_type, fnb_name, fnb_description, fnb_price, is_available, fnb_id])
        
def delete_fnb(fnb_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("DELETE FROM fnbs WHERE fnb_id=?", [fnb_id])

def edit_reservation(reservation_id, reserver_name, reservation_date):
    with sql.connect(DATABASE) as conn:
        conn.execute("UPDATE reservations SET reserver_name=?, reservation_date=? WEHERE reservation_id=?", [reserver_name, reservation_date, reservation_id])

def delete_reservation(reservation_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("DELETE FROM reservations WHERE reservation_id=?", [reservation_id])

def edit_order(order_id, reservation_id, order_at, is_paid):
    with sql.connect(DATABASE) as conn:
        conn.execute("UPDATE orders SET reservation_id=?, order_at=?, is_paid=? WHERE order_id=?", [reservation_id, get_datetime(), is_paid, order_id])

def delete_order(order_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("DELETE FROM orders WHERE order_id=?", [order_id])

def edit_payment(payment_id, order_id, payment_type, total_price, payment_date):
    with sql.connect(DATABASE) as conn:
        conn.execute("UPDATE payments SET order_id=?, payment_type=?, total_price=?, payment_date=? WHERE payment_id=?", [order_id, payment_type, total_price, payment_date, payment_id])

def edit_fnb_order(fnb_order_id, order_id, fnb_id, fnb_quantity):
    with sql.connect(DATABASE) as conn:
        conn.execute("UPDATE fnb_order SET order_id=?, fnb_id=?, fnb_quantity=? WHERE fnb_order_id=?", [order_id, fnb_id, fnb_quantity, fnb_order_id])

def delete_fnb_order(fnb_order_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("DELETE FROM fnb_order WHERE fnb_order_id=?", [fnb_order_id])

def edit_table_reservation(table_reservation_id, reservation_id, table_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("UPDATE table_reservation SET reservation_id=?, table_id=? WHERE table_reservation_id=?", [reservation_id, table_id, table_reservation_id])

def delete_table_reservation(table_reservation_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("DELETE FROM table_reservation WHERE table_reservation_id=?", table_reservation_id)

def get_tables():
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        tables = conn.execute("SElECT * FROM tables").fetchall()
        return tables

def get_fnbs():
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        fnbs = conn.execute("SELECT * FROM fnbs").fetchall()
        return fnbs

def get_reservations():
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        reservations = conn.execute("SELECT * FROM reservations").fetchall()
        data = []
        for reservation in reservations:
            data.append({
                "reservation": reservation,
                "tables": get_table_reservation(reservation["reservation_id"])
            })
            
        return data

def get_table_reservation(reservation_id):
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        table_reservation = conn.execute("SELECT * FROM table_reservation WHERE reservation_id=?", [reservation_id]).fetchall()
        return table_reservation

def get_orders():
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        orders = conn.execute("SELECT * FROM orders").fetchall()
        
        data = []
        for order in orders:
            temp = get_data(order["order_id"])
            data.append({
                "order": order,
                "reservation": temp["order"],
                "fnbs": temp["fnbs"]
            })
        return data

def get_fnb_order(order_id):
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        fnb_order = conn.execute("SELECT * FROM fnb_order WHERE order_id=?", [order_id]).fetchall()
        return fnb_order
        
def get_unpaid_orders():
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        unpaid_order_ids = conn.execute("SELECT order_id FROM orders WHERE is_paid=?", [FALSE]).fetchall()

        unpaid_orders = []
        for unpaid_order_id in unpaid_order_ids:
            unpaid_orders.append(get_data(unpaid_order_id["order_id"]))

        return unpaid_orders

def get_is_paid(order_id):
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        row = conn.execute("SELECT is_paid FROM orders WHERE order_id=?", [order_id]).fetchone()
        return row["is_paid"]

def create_reservation(reserver_name, reservation_date):
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        conn.execute("INSERT INTO reservations (reserver_name, reservation_date) VALUES (?, ?)", [reserver_name, reservation_date])
        row = conn.execute("SELECT reservation_id FROM reservations ORDER BY reservation_id DESC LIMIT 1").fetchone()
        return row["reservation_id"]

def save_table_reservation(reservation_id, table_id):
    with sql.connect(DATABASE) as conn:
        conn.execute("INSERT INTO table_reservation (reservation_id, table_id) VALUES(?, ?)", [reservation_id, table_id])
        conn.execute("UPDATE tables SET is_available=? WHERE table_id=?", [FALSE, table_id])

def create_order(reservation_id):
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        conn.execute("INSERT INTO orders (reservation_id, order_at, is_paid) VALUES (?, ?, ?)", [reservation_id, get_datetime(), FALSE])
        row = conn.execute("SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1").fetchone()
        return row["order_id"]

def save_fnb_order(order_id, fnb_id, fnb_quantity):
    with sql.connect(DATABASE) as conn:
        conn.execute("INSERT INTO fnb_order (order_id, fnb_id, fnb_quantity) VALUES (?, ?, ?)", [order_id, fnb_id, fnb_quantity])

def get_data(order_id):
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        tables = conn.execute("SELECT tables.table_number, tables.table_capacity FROM tables JOIN table_reservation ON tables.table_id=table_reservation.table_id WHERE table_reservation.reservation_id=(SELECT reservation_id FROM orders WHERE order_id=?)", [order_id]).fetchall()
        fnbs = conn.execute("SELECT fnbs.fnb_id, fnbs.fnb_type, fnbs.fnb_name, fnbs.fnb_price, fnb_order.fnb_quantity FROM fnbs JOIN fnb_order ON fnbs.fnb_id=fnb_order.fnb_id WHERE fnb_order.order_id=?", [order_id]).fetchall()
        order = conn.execute("SELECT reservations.reservation_id, reservations.reserver_name, reservations.reservation_date, orders.order_id, orders.order_at, orders.is_paid FROM reservations JOIN orders ON reservations.reservation_id=orders.reservation_id WHERE orders.order_id=?", [order_id]).fetchone()

        total_price = 0
        for fnb in fnbs:
            total_price += fnb["fnb_price"] * fnb["fnb_quantity"]

        data = {
            "tables": tables,
            "fnbs": fnbs,
            "order": order,
            "total_price": total_price,
        }

        return data

def payment(order_id, payment_type, total_price):
    with sql.connect(DATABASE) as conn:
        conn.row_factory = dict_factory
        conn.execute("INSERT INTO payments (order_id, payment_type, total_price, payment_date) VALUES (?, ?, ?, ?)", [order_id, payment_type, total_price, get_datetime()])
        conn.execute("UPDATE orders SET is_paid=? WHERE order_id=?", [TRUE, order_id])
        rows = conn.execute("SELECT tables.table_id FROM tables LEFT JOIN table_reservation ON tables.table_id=table_reservation.table_id WHERE table_reservation.reservation_id=(SELECT reservation_id FROM orders WHERE order_id=?)", [order_id]).fetchall()
        for row in rows:
            conn.execute("UPDATE tables SET is_available=? WHERE table_id=?", [TRUE, row["table_id"]])

def get_datetime():
    return dt.now().strftime('%Y/%m/%d %I:%M %p')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d