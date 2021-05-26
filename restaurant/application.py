import util

from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from waitress import serve

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    if not session.get("is_paid"):
        return render_template("index.html")

    if session["is_paid"] == util.TRUE:
        return redirect("/payment")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            session["admin"] = True
            session["order_id"] = None
            session["reservation_id"] = None
            session["is_paid"] = None
            return redirect("/")

    if session.get("admin") or session.get("reservation_id"):
        return redirect("/")

    return render_template("login.html")

@app.route("/table", methods=["GET", "POST"])
def table():
    if not session.get("admin"):
        return redirect("/")
    
    if request.method == "POST":
        table_id = request.form.get("table_id")
        table_number = request.form.get("table_number")
        table_capacity = request.form.get("table_capacity")
        if request.form.get("is_available"):
            is_available = util.TRUE
        else:
            is_available = util.FALSE

        submit = request.form.get("submit")
        if submit == "Add":
            util.add_table(table_number, table_capacity, is_available)
        elif submit == "Edit":
            util.edit_table(table_id, table_number, table_capacity, is_available)
        elif submit == "Delete":
            util.delete_table(table_id)

        return redirect("/table")
            
    return render_template("table.html", tables=util.get_tables())

@app.route("/fnb", methods=["GET", "POST"])
def fnb():
    if not session.get("admin"):
        return redirect("/")

    if request.method == "POST":
        fnb_id = request.form.get('fnb_id')
        fnb_type = request.form.get("fnb_type")
        fnb_name = request.form.get("fnb_name")
        fnb_description = request.form.get("fnb_description")
        fnb_price = request.form.get("fnb_price")

        if request.form.get("is_available"):
            is_available = util.TRUE
        else:
            is_available = util.FALSE

        submit = request.form.get("submit")
        if submit == "Add":
            util.add_fnb(fnb_type, fnb_name, fnb_description, fnb_price, is_available)
        elif submit == "Edit":
            util.edit_fnb(fnb_id, fnb_type, fnb_name, fnb_description, fnb_price, is_available)
        elif submit == "Delete":
            util.delete_fnb(fnb_id)

        return redirect("/fnb")

    return render_template("fnb.html", fnbs=util.get_fnbs())

@app.route("/reservation", methods=["GET", "POST"])
def reservation():
    if request.method == "POST":
        if not session.get("admin"):
            reserver_name = request.form.get("reserver_name")
            reservation_date = request.form.get("reservation_date")
            session["reservation_id"] = util.create_reservation(reserver_name, reservation_date)
            table_ids = request.form.getlist("table_ids")

            for table_id in table_ids:
                util.save_table_reservation(session["reservation_id"], table_id)

        else:
            reservation_id = request.form.get("reservation_id")
            reserver_name = request.form.get("reserver_name")
            reservation_date = request.form.get("reservation_date")
            table_ids = request.form.get("table_ids")
            
            submit = request.form.get("submit")
            if submit == "Add":
                reservation_id = util.create_reservation(reserver_name, reservation_date)
                for table_id in table_ids:
                    util.save_table_reservation(reservation_id, table_id)

            elif submit == "Edit":
                util.edit_reservation(reservation_id, reserver_name, reservation_date)
                table_reservations = util.get_table_reservation(reservation_id)

                for table_reservation in table_reservations:
                    table_id = table_reservation["table_id"]
                    table_reservation_id = table_reservations["table_reservation_id"]
                    if not table_id in table_ids:
                        util.delete_table_reservation(table_reservation_id)

                for table_id in table_ids:
                    for table_reservation in table_reservations:
                        if table_reservation["table_id"] == table_id:
                            break
                    
                    util.save_table_reservation(reservation_id, table_id)

            elif submit == "Delete":
                util.delete_reservation(reservation_id)

            return redirect("/reservation")
    
    if not session.get("admin"):
        if session.get("reservation_id"):
            return redirect("/order")

        return render_template("reservation.html", tables=util.get_tables())
    
    return render_template("reservation.html", reservations=util.get_reservations(), tables=util.get_tables())

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        if not session.get("admin"):
            session["order_id"] = util.create_order(session["reservation_id"])
            fnb_ids = request.form.getlist("fnb_ids")
            quantities = request.form.getlist("quantity")

            fnbs = []
            for idx, fnb_id in enumerate(fnb_ids):
                if not int(quantities[idx]) == 0:
                    fnbs.append({"fnb_id": fnb_id, "fnb_quantity": quantities[idx]})

            for fnb in fnbs:
                util.save_fnb_order(session["order_id"], fnb["fnb_id"], fnb["fnb_quantity"])

            session["is_paid"] = util.get_is_paid(session["order_id"])

        else:
            order_id = request.form.get("order_id")
            reservation_id = request.form.get("reservation_id")
            order_at = request.form.get("order_at")

            if request.form.get("is_paid"):
                is_paid = util.TRUE
            else:
                is_paid = util.FALSE    

            fnb_ids = request.form.getlist("fnb_ids")
            quantities = request.form.getlist("quantity")

            fnbs = []
            for idx, fnb_id in enumerate(fnb_ids):
                fnbs.append({"fnb_id": fnb_id, "fnb_quantity": quantities[idx]})

            submit = request.form.get("submit")
            if submit == "Add":
                order_id = util.create_order(reservation_id)
                for fnb in fnbs:
                    util.save_fnb_order(order_id, fnb["fnb_id"], fnb["fnb_quantity"])
            elif submit == "Edit":
                util.edit_order(order_id, reservation_id, order_at, is_paid)
                fnb_orders = util.get_fnb_order(order_id)

                for fnb in fnbs:
                    fnb_id = fnb["fnb_id"]
                    fnb_quantity = fnb["fnb_quantity"]
                    for fnb_order in fnb_orders:
                        if fnb_order["fnb_id"] == fnb_id:
                            fnb_order_id = fnb_order["fnb_order_id"]
                            fnb_order_quantity = fnb_order["fnb_quantity"]

                            if fnb_quantity == 0:
                                util.delete_fnb_order(fnb_order_id)
                            elif not fnb_quantity == fnb_order_quantity:
                                util.edit_fnb_order(fnb_order_id, order_id, fnb_id, fnb_quantity)
                            break
                    
                    util.save_fnb_order(order_id, fnb_id, fnb_quantity)

            elif submit == "Delete":
                util.delete_order(order_id)

            return redirect("/order")

    if not session.get("admin"):
        if not session.get("reservation_id"):
            return redirect("/reservation")

        if session.get("order_id"):
            return redirect("/payment")

        return render_template("order.html", fnbs=util.get_fnbs())
        
    return render_template("order.html", orders=util.get_orders(), fnbs=util.get_fnbs())

@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        if not session.get('admin'):
            payment_type = request.form.get("payment_type")
            total_price = request.form.get("total_price")
            util.payment(session["order_id"], payment_type, total_price)
            session["is_paid"] = util.get_is_paid(session["order_id"])
        
        else:
            order_id = request.form.get("order_id")
            payment_type = request.form.get("payment_type")
            total_price = request.form.get("total_price")
            util.payment(order_id, payment_type, total_price)

    if not session.get("admin"):
        if not session.get("reservation_id"):
            return redirect("/reservation")

        if not session.get("order_id"):
            return redirect("/order")

        return render_template("payment.html", data=util.get_data(session["order_id"]))

    return render_template("payment.html", unpaid_orders=util.get_unpaid_orders())

if __name__ == "__main__":
    util.create_table()
    serve(app)