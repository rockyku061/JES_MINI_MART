import csv
import os
import datetime
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

# ================= FILES =================
USERS_FILE = "users.csv"
PRODUCTS_FILE = "products.csv"
ORDERS_FILE = "orders.csv"

# ================= CREATE FILES =================
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "regdno", "email", "password"])

if not os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "price", "description", "image"])

if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "product_name", "price", "date"])

# ================= IMAGE UPLOAD =================
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cart = []

# ================= INDEX =================
@app.route("/")
def index():
    return render_template("index.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form["name"]
        regdno = request.form["regdno"]
        email = request.form["email"]
        password = request.form["password"]

        with open(USERS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([username, regdno, email, password])

        return redirect(url_for("login"))

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        regdno = request.form["regdno"].strip()
        password = request.form["password"].strip()

        with open(USERS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (
                    row["username"].strip() == username and
                    row["regdno"].strip() == regdno and
                    row["password"].strip() == password
                ):
                    session["username"] = username
                    return redirect("/student_dashboard")

        return "Invalid Credentials"

    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ================= STUDENT DASHBOARD =================
@app.route("/student_dashboard")
def student_dashboard():
    if "username" not in session:
        return redirect("/login")

    search_query = request.args.get("search", "").lower()
    products = []

    with open(PRODUCTS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if search_query in row["name"].lower():
                products.append(row)

    return render_template("studentDashboard.html", products=products)

# ================= PRODUCT DETAIL =================
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = None

    with open(PRODUCTS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["id"]) == product_id:
                product = row
                break

    if not product:
        return "Product not found"

    return render_template("productDetail.html", product=product)

@app.route("/mark_sold/<int:product_id>", methods=["POST"])
def mark_sold(product_id):

    updated_products = []

    with open(PRODUCTS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["id"]) != product_id:
                updated_products.append(row)

    with open(PRODUCTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id","name","price","description","image","seller"])
        writer.writeheader()
        writer.writerows(updated_products)

    return redirect(url_for("student_dashboard"))

# ================= ADD PRODUCT =================
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
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(filepath)
            image_path = "uploads/" + filename

        # generate new product id
        with open(PRODUCTS_FILE, "r") as f:
            reader = list(csv.reader(f))
            new_id = len(reader)

        # save seller name
        seller = session["username"]

        with open(PRODUCTS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([new_id, name, price, description, image_path, seller])

        return redirect("/student_dashboard")

    return render_template("addProduct.html")


# ================= PROFILE SETTING =================
@app.route("/profile_settings", methods=["GET","POST"])
def profile_settings():

    if "username" not in session:
        return redirect("/login")

    user = None

    with open(USERS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == session["username"]:
                user = row
                break

    if request.method == "POST":

        new_name = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]

        users = []

        with open(USERS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == session["username"]:
                    row["username"] = new_name
                    row["email"] = new_email
                    row["password"] = new_password
                    session["username"] = new_name
                users.append(row)

        with open(USERS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["username","regdno","email","password"])
            writer.writeheader()
            writer.writerows(users)

        return redirect("/student_dashboard")

    return render_template("profilesettings.html", user=user)

# ================= CART =================
@app.route("/cart", methods=["GET", "POST"])
def cart_page():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        product_id = request.form["product_id"]

        with open(PRODUCTS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["id"] == product_id:
                    cart.append(row)
                    break

        # stay on dashboard after adding
        return redirect("/student_dashboard")

    return render_template("cart.html", cart=cart)

# ================= ADD TO CART =================
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    if "username" not in session:
        return redirect("/login")

    product_id = request.form["product_id"]

    with open(PRODUCTS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == product_id:
                cart.append(row)
                break

    # stay on dashboard
    return redirect(url_for("student_dashboard"))

# ================= CHECKOUT =================
@app.route("/checkout", methods=["POST"])
def checkout():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in cart:
        with open(ORDERS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([username, item["name"], item["price"], now])

    cart.clear()
    return redirect("/purchaseHistory")

# ================= PURCHASE HISTORY =================
@app.route("/purchaseHistory")
def purchase_history_page():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    history = []

    with open(ORDERS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                history.append(row)

    return render_template("purchaseHistory.html", history=history)

# ================= CHAT  =================
@app.route("/chat/<product_name>", methods=["GET", "POST"])
def chat_page(product_name):
    if "username" not in session:
        return redirect("/login")

    if "chat_messages" not in session:
        session["chat_messages"] = []

    if request.method == "POST":
        message = request.form["message"]

        session["chat_messages"].append({
            "text": message,
            "type": "sent"
        })

        session.modified = True

    return render_template("chat.html",
                           product_name=product_name,
                           messages=session["chat_messages"])
    
# ================= FEEDBACK PAGE =================
FEEDBACK_FILE = "feedback.csv"

if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "rating", "comment"])

@app.route("/feedback", methods=["GET", "POST"])
def feedback_page():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        rating = request.form["rating"]
        comment = request.form["comment"]
        username = session["username"]

        with open(FEEDBACK_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([username, rating, comment])

        return redirect("/student_dashboard")

    return render_template("feedback.html")

    
    
    
# ================= OTHER PAGES =================
@app.route("/contact")
def contact_page():
    return render_template("contact.html")


@app.route("/faq")
def faq_page():
    return render_template("faq.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)