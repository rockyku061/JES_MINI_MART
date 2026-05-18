from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "jes_mini_mart_secret"

# =========================
# FILES
# =========================

USERS_FILE = "users.csv"
PRODUCTS_FILE = "products.csv"
CART_FILE = "cart.csv"
PURCHASE_FILE = "purchase_history.csv"

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# =========================
# CREATE FILES IF NOT EXISTS
# =========================

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "username",
            "regdno",
            "email",
            "password",
            "phone",
            "college"
        ])

if not os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id",
            "name",
            "price",
            "description",
            "image",
            "seller"
        ])

if not os.path.exists(CART_FILE):
    with open(CART_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "username",
            "product_id",
            "name",
            "price",
            "description",
            "image",
            "seller"
        ])

if not os.path.exists(PURCHASE_FILE):
    with open(PURCHASE_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "username",
            "name",
            "price",
            "image"
        ])

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")


@app.route("/feedback")
def feedback_page():
    return render_template("feedback.html")


@app.route("/faq")
def faq_page():
    return render_template("faq.html")


@app.route("/about")
def about_page():
    return render_template("about.html")

# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register_page():

    if request.method == "POST":

        username = request.form["name"]
        regdno = request.form["regdno"]
        email = request.form["email"]
        password = request.form["password"]

        phone = ""
        college = ""

        with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            writer.writerow([
                username,
                regdno,
                email,
                password,
                phone,
                college
            ])

        return redirect(url_for("login"))

    return render_template("register.html")

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        regdno = request.form["regdno"].strip()
        password = request.form["password"].strip()

        with open(USERS_FILE, "r", encoding="utf-8") as f:

            reader = csv.reader(f)

            next(reader, None)

            for row in reader:

                if len(row) < 6:
                    continue

                if (
                    row[0] == username and
                    row[1] == regdno and
                    row[3] == password
                ):

                    session["username"] = row[0]
                    session["regdno"] = row[1]
                    session["email"] = row[2]
                    session["phone"] = row[4]
                    session["college"] = row[5]

                    return redirect("/student_dashboard")

        return "Invalid Credentials"

    return render_template("login.html")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# DASHBOARD
# =========================

@app.route("/student_dashboard")
def student_dashboard():

    if "username" not in session:
        return redirect("/login")

    products = []

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:
            products.append(row)

    return render_template(
        "studentDashboard.html",
        products=products,
        username=session["username"]
    )

# =========================
# ADD PRODUCT
# =========================

@app.route("/addProduct", methods=["GET", "POST"])
def add_product():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["productName"]
        price = request.form["productPrice"]
        description = request.form["productDescription"]

        image_file = request.files["productImage"]

        image_path = ""

        if image_file and image_file.filename != "":

            filename = secure_filename(image_file.filename)

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            image_file.save(filepath)

            image_path = "uploads/" + filename

        rows = []

        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        new_id = len(rows)

        with open(PRODUCTS_FILE, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            writer.writerow([
                new_id,
                name,
                price,
                description,
                image_path,
                session["username"]
            ])

        return redirect("/student_dashboard")

    return render_template("addProduct.html")

# =========================
# PRODUCT DETAILS
# =========================

@app.route("/product/<int:product_id>")
def product_detail(product_id):

    product = None

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            try:
                if int(row["id"]) == product_id:
                    product = row
                    break
            except:
                pass

    if not product:
        return "Product not found"

    return render_template(
        "productdetail.html",
        product=product
    )
    
# =========================
# CHAT PAGE
# =========================

@app.route("/chat/<seller>/<product_name>",
           methods=["GET", "POST"])
def chat_page(seller, product_name):

    if "username" not in session:
        return redirect("/login")

    current_user = session["username"]

    # CREATE FILE
    if not os.path.exists("messages.csv"):

        with open(
            "messages.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "sender",
                "seller",
                "product",
                "message"
            ])

    # SEND MESSAGE
    if request.method == "POST":

        message = request.form.get(
            "message",
            ""
        ).strip()

        if message != "":

            with open(
                "messages.csv",
                "a",
                newline="",
                encoding="utf-8"
            ) as f:

                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "sender",
                        "seller",
                        "product",
                        "message"
                    ]
                )

                writer.writerow({
                    "sender": current_user,
                    "seller": seller,
                    "product": product_name,
                    "message": message
                })

        return redirect(
            url_for(
                "chat_page",
                seller=seller,
                product_name=product_name
            )
        )

    messages = []

    # LOAD MESSAGES
    with open(
        "messages.csv",
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            if (
                row["seller"] == seller and
                row["product"] == product_name
            ):

                messages.append({
                    "sender": row["sender"],
                    "message": row["message"]
                })

    return render_template(
        "chat.html",
        messages=messages,
        seller=seller,
        product_name=product_name,
        current_user=current_user
    )
    
@app.route("/mark_sold/<int:product_id>", methods=["POST"])
def mark_sold(product_id):

    rows = []

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:

        reader = csv.reader(f)

        for row in reader:

            if row[0] == "id":
                rows.append(row)
                continue

            if int(row[0]) != product_id:
                rows.append(row)

    with open(PRODUCTS_FILE, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)
        writer.writerows(rows)

    return redirect(url_for("student_dashboard"))

   
# =========================
# SELLER CHATS
# =========================

@app.route("/seller_chats")
def seller_chats():

    if "username" not in session:
        return redirect("/login")

    seller = session["username"]

    chats = []

    if not os.path.exists("messages.csv"):
        return render_template(
            "sellerChats.html",
            chats=[]
        )

    with open(
        "messages.csv",
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            if row.get("seller") == seller:

                already_exists = False

                for chat in chats:

                    if (
                        chat["buyer"] == row["buyer"]
                        and
                        chat["product"] == row["product"]
                    ):

                        already_exists = True
                        break

                if not already_exists:

                    chats.append({
                        "buyer": row.get("buyer", ""),
                        "seller": row.get("seller", ""),
                        "product": row.get("product", "")
                    })

    return render_template(
        "sellerChats.html",
        chats=chats
    )


# =========================
# ADD TO CART
# =========================

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    if "username" not in session:
        return redirect("/login")

    product = None

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            try:
                if int(row["id"]) == product_id:
                    product = row
                    break
            except:
                pass

    if not product:
        return "Product not found"

    with open(CART_FILE, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            session["username"],
            product["id"],
            product["name"],
            product["price"],
            product["description"],
            product["image"],
            product["seller"]
        ])

    return redirect(url_for("cart_page"))

# =========================
# CART PAGE
# =========================

@app.route("/cart")
def cart_page():

    if "username" not in session:
        return redirect("/login")

    cart_items = []

    with open(CART_FILE, "r", encoding="utf-8") as f:

        reader = csv.reader(f)

        next(reader, None)

        for row in reader:

            if len(row) < 7:
                continue

            if row[0] == session["username"]:

                cart_items.append({
                    "username": row[0],
                    "product_id": row[1],
                    "name": row[2],
                    "price": row[3],
                    "description": row[4],
                    "image": row[5],
                    "seller": row[6]
                })

    return render_template(
        "cart.html",
        cart_items=cart_items
    )
# =========================
# REMOVE CART ITEM
# =========================

@app.route("/remove_from_cart/<product_id>", methods=["POST"])
def remove_from_cart(product_id):

    if "username" not in session:
        return redirect("/login")

    rows = []

    removed = False

    with open(CART_FILE, "r", encoding="utf-8") as f:

        reader = csv.reader(f)

        for row in reader:

            if row[0] == "username":
                rows.append(row)
                continue

            if (
                not removed and
                row[0] == session["username"] and
                row[1] == product_id
            ):
                removed = True
                continue

            rows.append(row)

    with open(CART_FILE, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)
        writer.writerows(rows)

    return redirect(url_for("cart_page"))

# =========================
# CHECKOUT
# =========================

@app.route("/checkout", methods=["POST"])
def checkout():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    cart_items = []
    remaining_rows = []

    with open(CART_FILE, "r", encoding="utf-8") as f:

        reader = csv.reader(f)

        for row in reader:

            if row[0] == "username":
                remaining_rows.append(row)
                continue

            if row[0] == username:
                cart_items.append(row)
            else:
                remaining_rows.append(row)

    with open(PURCHASE_FILE, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        for item in cart_items:

            writer.writerow([
                username,
                item[2],
                item[3],
                item[5]
            ])

    with open(CART_FILE, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)
        writer.writerows(remaining_rows)

    return redirect(url_for("purchase_history"))

# =========================
# PURCHASE HISTORY
# =========================

@app.route("/purchase_history")
def purchase_history():

    if "username" not in session:
        return redirect("/login")

    orders = []

    with open(PURCHASE_FILE, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            if row["username"] == session["username"]:
                orders.append(row)

    return render_template(
        "purchaseHistory.html",
        orders=orders
    )

# =========================
# PROFILE SETTINGS
# =========================

@app.route("/profile_settings", methods=["GET", "POST"])
def profile_settings():

    if "username" not in session:
        return redirect("/login")

    current_username = session["username"]

    if request.method == "POST":

        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]
        new_phone = request.form["phone"]
        new_college = request.form["college"]

        updated_rows = []

        with open(USERS_FILE, "r", encoding="utf-8") as f:

            reader = csv.reader(f)

            for row in reader:

                if row[0] == "username":
                    updated_rows.append(row)
                    continue

                if row[0] == current_username:

                    row = [
                        new_username,
                        row[1],
                        new_email,
                        new_password,
                        new_phone,
                        new_college
                    ]

                updated_rows.append(row)

        with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)
            writer.writerows(updated_rows)

        session["username"] = new_username
        session["email"] = new_email
        session["phone"] = new_phone
        session["college"] = new_college

        return redirect(url_for("profile_settings"))

    user = {
        "username": session.get("username", ""),
        "email": session.get("email", ""),
        "phone": session.get("phone", ""),
        "college": session.get("college", "")
    }

    return render_template(
        "profilesettings.html",
        user=user
    )

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)