import os
import requests
import random
import random
import time
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from MySQLdb.cursors import DictCursor
from flask_mail import Mail, Message
import config
import re

app = Flask(__name__)

# Secret Key
app.secret_key = config.SECRET_KEY

# -----------------------------
# MySQL Configuration
# -----------------------------
app.config["MYSQL_HOST"] = config.MYSQL_HOST
app.config["MYSQL_PORT"] = int(config.MYSQL_PORT)
app.config["MYSQL_USER"] = config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = config.MYSQL_DB
app.config["MYSQL_SSL"] = {
    "ca": config.MYSQL_SSL_CA
}
def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# Upload Folder
UPLOAD_FOLDER = "uploads/rooms"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed Image Extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

mysql = MySQL(app)
bcrypt = Bcrypt(app)
cloudinary.config(
    cloud_name=config.CLOUDINARY_CLOUD_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USERNAME"] = config.MAIL_USERNAME
app.config["MAIL_PASSWORD"] = config.MAIL_PASSWORD

mail = Mail(app)

# ==========================
# HOME PAGE
# ==========================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# REGISTER
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        password = request.form["password"]
        role = request.form["role"]

        # -------------------------
        # Full Name Validation
        # -------------------------
        if len(fullname) < 3:
            flash("Full name must be at least 3 characters.", "danger")
            return render_template("register.html", form=request.form)

        # -------------------------
        # Email Validation
        # -------------------------
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if not re.match(email_pattern, email):
            flash("Invalid email address!", "danger")
            return render_template("register.html", form=request.form)

        # -------------------------
        # Phone Validation
        # -------------------------
        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must contain exactly 10 digits.", "danger")
            return render_template("register.html", form=request.form)

        # -------------------------
        # Password Validation
        # -------------------------
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html", form=request.form)
        
        cursor = mysql.connection.cursor(DictCursor)

        # -------------------------
        # Duplicate Email Check
        # -------------------------
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            flash("Email already registered!", "danger")
            return render_template("register.html", form=request.form)

        # -------------------------
        # Encrypt Password
        # -------------------------
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # -------------------------
        # Insert User
        # -------------------------
        cursor.execute("""
            INSERT INTO users(fullname,email,phone,password,role)
            VALUES(%s,%s,%s,%s,%s)
        """, (
            fullname,
            email,
            phone,
            hashed_password,
            role
        ))

        mysql.connection.commit()
        cursor.close()

        flash("Registration Successful!", "success")

        return redirect("/login")

    return render_template("register.html", form=None)


# ==========================
# LOGIN
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor = mysql.connection.cursor(DictCursor)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()
        cursor.close()

        if user:

            if bcrypt.check_password_hash(user["password"], password):

                session["user_id"] = user["id"]
                session["fullname"] = user["fullname"]
                session["email"] = user["email"]
                session["role"] = user["role"]

                flash("Login Successful!", "success")

                if user["role"] == "admin":
                  return redirect("/admin")

                elif user["role"] == "owner":
                 return redirect("/owner")

                else:
                  return redirect("/tenant-dashboard")

        flash("Invalid Email or Password!", "danger")
        return render_template("login.html", form=request.form)

    return render_template("login.html", form=None)


# ==========================
# OWNER DASHBOARD
# ==========================
@app.route("/owner")
def owner():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    # Total rooms
    cursor.execute("""
        SELECT COUNT(*) AS total_rooms
        FROM rooms
        WHERE owner_id=%s
    """, (session["user_id"],))

    total_rooms = cursor.fetchone()["total_rooms"]

    # Total saved by users
    cursor.execute("""
        SELECT COUNT(*) AS total_saved
        FROM saved_rooms
        JOIN rooms
            ON saved_rooms.room_id = rooms.id
        WHERE rooms.owner_id=%s
    """, (session["user_id"],))

    total_saved = cursor.fetchone()["total_saved"]

    # Available rooms
    cursor.execute("""
        SELECT COUNT(*) AS available_rooms
        FROM rooms
        WHERE owner_id=%s
        AND status='Available'
    """, (session["user_id"],))

    available_rooms = cursor.fetchone()["available_rooms"]

    # Rented rooms
    cursor.execute("""
        SELECT COUNT(*) AS rented_rooms
        FROM rooms
        WHERE owner_id=%s
        AND status='Rented'
    """, (session["user_id"],))

    rented_rooms = cursor.fetchone()["rented_rooms"]

    cursor.close()

    return render_template(
        "owner.html",
        total_rooms=total_rooms,
        total_saved=total_saved,
        available_rooms=available_rooms,
        rented_rooms=rented_rooms
    )

# ==========================
# TENANT DASHBOARD
# ==========================

@app.route("/tenant-dashboard")
def tenant_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "").strip()

    cursor = mysql.connection.cursor(DictCursor)

    if search:

        cursor.execute("""
        SELECT
            rooms.*,
            (
                SELECT image_url
                FROM room_images
                WHERE room_id = rooms.id
                LIMIT 1
            ) AS image_url

        FROM rooms

        WHERE
            city LIKE %s
            OR state LIKE %s
            OR room_type LIKE %s
            OR title LIKE %s

        ORDER BY id DESC
        """,
        (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("""
        SELECT
            rooms.*,
            (
                SELECT image_url
                FROM room_images
                WHERE room_id = rooms.id
                LIMIT 1
            ) AS image_url

        FROM rooms

        ORDER BY id DESC
        """)

    rooms = cursor.fetchall()

    cursor.close()

    return render_template(
        "tenant_dashboard.html",
        rooms=rooms,
        search=search
    )

@app.route("/tenant")
def tenant():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect("/login")

    return render_template("tenant.html")


# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect("/")


@app.route("/add-room", methods=["GET", "POST"])
def add_room():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "owner":
        flash("Access Denied!", "danger")
        return redirect("/")

    if request.method == "POST":

        title = request.form["title"].strip()
        room_type = request.form["room_type"]
        rent = request.form["rent"]
        deposit = request.form["deposit"]
        address = request.form["address"].strip()
        city = request.form["city"].strip()
        state = request.form["state"].strip()
        pincode = request.form["pincode"].strip()
        contact = request.form["contact"].strip()
        description = request.form["description"].strip()

        facilities = ",".join(request.form.getlist("facilities"))

        cursor = mysql.connection.cursor(DictCursor)

        cursor.execute("""
            INSERT INTO rooms
            (
                owner_id,
                title,
                room_type,
                rent,
                deposit,
                address,
                city,
                state,
                pincode,
                contact,
                facilities,
                description
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session["user_id"],
            title,
            room_type,
            rent,
            deposit,
            address,
            city,
            state,
            pincode,
            contact,
            facilities,
            description
        ))

        mysql.connection.commit()
        room_id = cursor.lastrowid

        images = request.files.getlist("images")

        for image in images:

            if image and image.filename != "":

                if allowed_file(image.filename):

                    filename = secure_filename(image.filename)

                    try:
                        upload_result = cloudinary.uploader.upload(
                            image,
                            folder="roomfinder/rooms"
                        )
                    except Exception as e:
                        flash(f"Image upload failed: {e}", "danger")
                        continue

                    image_url = upload_result.get("secure_url")
                    public_id = upload_result.get("public_id")

                    cursor.execute("""
                        INSERT INTO room_images
                        (room_id, image_name, image_url, public_id)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        room_id,
                        filename,
                        image_url,
                        public_id
                    ))

                else:
                    flash(f"{image.filename} is not a valid image.", "danger")

        mysql.connection.commit()
        cursor.close()

        flash("Room Added Successfully!", "success")
        return redirect("/owner")

    return render_template("add_room.html")

@app.route("/my-rooms")
def my_rooms():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT
            rooms.*,
            (
                SELECT image_url
                FROM room_images
                WHERE room_id = rooms.id
                LIMIT 1
            ) AS image
        FROM rooms
        WHERE owner_id=%s
        ORDER BY id DESC
    """, (session["user_id"],))

    rooms = cursor.fetchall()

    cursor.close()

    return render_template(
        "my_rooms.html",
        rooms=rooms
    )

@app.route("/room/<int:room_id>")
def room_details(room_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute(
        "SELECT * FROM rooms WHERE id=%s",
        (room_id,)
    )

    room = cursor.fetchone()

    cursor.execute("""
        SELECT
            image_name,
            image_url,
            public_id
        FROM room_images
        WHERE room_id=%s
    """, (room_id,))

    images = cursor.fetchall()

    cursor.close()

    return render_template(
        "room_details.html",
        room=room,
        images=images
    )

@app.route("/edit-room/<int:room_id>", methods=["GET", "POST"])
def edit_room(room_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    if request.method == "POST":

        title = request.form["title"]
        rent = request.form["rent"]
        deposit = request.form["deposit"]
        city = request.form["city"]
        address = request.form["address"]
        description = request.form["description"]

        cursor.execute("""
            UPDATE rooms
            SET
                title=%s,
                rent=%s,
                deposit=%s,
                city=%s,
                address=%s,
                description=%s
            WHERE id=%s
        """,
        (
            title,
            rent,
            deposit,
            city,
            address,
            description,
            room_id
        ))

        images = request.files.getlist("images")

        if images and images[0].filename != "":

            # Delete old Cloudinary images
            cursor.execute("""
                SELECT public_id
                FROM room_images
                WHERE room_id=%s
            """, (room_id,))

            old_images = cursor.fetchall()

            for img in old_images:

                if img["public_id"]:
                    try:
                        cloudinary.uploader.destroy(img["public_id"])
                    except Exception as e:
                        print(e)

            # Remove old database records
            cursor.execute("""
                DELETE FROM room_images
                WHERE room_id=%s
            """, (room_id,))

            # Upload new images
            for image in images:

                if image and allowed_file(image.filename):

                    filename = secure_filename(image.filename)

                    upload_result = cloudinary.uploader.upload(
                        image,
                        folder="roomfinder/rooms"
                    )

                    cursor.execute("""
                        INSERT INTO room_images
                        (room_id,image_name,image_url,public_id)
                        VALUES(%s,%s,%s,%s)
                    """,
                    (
                        room_id,
                        filename,
                        upload_result["secure_url"],
                        upload_result["public_id"]
                    ))

        mysql.connection.commit()

        cursor.close()

        flash("Room Updated Successfully!", "success")

        return redirect("/my-rooms")

    cursor.execute(
        "SELECT * FROM rooms WHERE id=%s",
        (room_id,)
    )

    room = cursor.fetchone()

    cursor.close()

    return render_template(
        "edit_room.html",
        room=room
    )

@app.route("/delete-room/<int:room_id>")
def delete_room(room_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    # Get Cloudinary public IDs
    cursor.execute("""
        SELECT public_id
        FROM room_images
        WHERE room_id=%s
    """, (room_id,))

    images = cursor.fetchall()

    # Delete images from Cloudinary
    for image in images:

        if image["public_id"]:
            try:
                cloudinary.uploader.destroy(image["public_id"])
            except Exception as e:
                print("Cloudinary Delete Error:", e)

    # Delete image records
    cursor.execute("""
        DELETE FROM room_images
        WHERE room_id=%s
    """, (room_id,))

    # Delete room
    cursor.execute("""
        DELETE FROM rooms
        WHERE id=%s
    """, (room_id,))

    mysql.connection.commit()

    cursor.close()

    flash("Room deleted successfully!", "success")

    return redirect("/my-rooms")

from flask import send_from_directory

@app.route("/uploads/rooms/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

# =========================
# Forgot Password
# =========================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"].strip()

        cursor = mysql.connection.cursor(DictCursor)

        cursor.execute(
            "SELECT id, fullname, email FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()
        cursor.close()

        if not user:
            flash("Email not registered.", "danger")
            return render_template("forgot_password.html")

        # Prevent repeated OTP requests within 60 seconds
        last_sent = session.get("otp_time")
        if last_sent and time.time() - last_sent < 60:
            flash("Please wait before requesting another OTP.", "warning")
            return redirect("/verify-otp")

        # Clear previous reset session
        session.pop("otp_verified", None)
        session.pop("reset_otp", None)
        session.pop("otp_time", None)

        otp = random.randint(100000, 999999)

        session["reset_user_id"] = user["id"]
        session["reset_email"] = user["email"]
        session["reset_otp"] = str(otp)
        session["otp_time"] = time.time()

        msg = Message(
            subject="RoomFinder Password Reset OTP",
            sender=app.config["MAIL_USERNAME"],
            recipients=[user["email"]]
        )

        msg.body = f"""
Hello {user['fullname']},

Your RoomFinder OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this password reset, please ignore this email.

Regards,
RoomFinder Team
"""

        mail.send(msg)

        flash("OTP has been sent to your registered email.", "success")
        return redirect("/verify-otp")

    return render_template("forgot_password.html")


# =========================
# Verify OTP
# =========================

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    if "reset_user_id" not in session:
        flash("Please request an OTP first.", "warning")
        return redirect("/forgot-password")

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if "reset_otp" not in session:
            flash("OTP expired.", "danger")
            return redirect("/forgot-password")

        # OTP valid for 5 minutes
        if time.time() - session["otp_time"] > 300:

            session.pop("reset_otp", None)
            session.pop("otp_time", None)

            flash("OTP has expired. Please request a new OTP.", "danger")
            return redirect("/forgot-password")

        if entered_otp == session["reset_otp"]:

            session["otp_verified"] = True

            session.pop("reset_otp", None)
            session.pop("otp_time", None)

            flash("OTP verified successfully.", "success")
            return redirect("/reset-password")

        flash("Invalid OTP.", "danger")

    return render_template("verify_otp.html")


# =========================
# Resend OTP
# =========================

@app.route("/resend-otp")
def resend_otp():

    if "reset_user_id" not in session:
        return redirect("/forgot-password")

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute(
        "SELECT fullname, email FROM users WHERE id=%s",
        (session["reset_user_id"],)
    )

    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash("User not found.", "danger")
        return redirect("/forgot-password")

    otp = random.randint(100000, 999999)

    session["reset_otp"] = str(otp)
    session["otp_time"] = time.time()

    msg = Message(
        subject="RoomFinder Password Reset OTP",
        sender=app.config["MAIL_USERNAME"],
        recipients=[user["email"]]
    )

    msg.body = f"""
Hello {user['fullname']},

Your new RoomFinder OTP is:

{otp}

This OTP is valid for 5 minutes.

Regards,
RoomFinder Team
"""

    mail.send(msg)

    flash("A new OTP has been sent to your email.", "success")
    return redirect("/verify-otp")


# =========================
# Reset Password
# =========================

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    if "otp_verified" not in session:
        flash("Please verify OTP first.", "warning")
        return redirect("/forgot-password")

    if request.method == "POST":

        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("reset_password.html")

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        cursor = mysql.connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET password=%s
            WHERE id=%s
            """,
            (hashed_password, session["reset_user_id"])
        )

        mysql.connection.commit()
        cursor.close()

        # Clear all reset session data
        session.pop("reset_user_id", None)
        session.pop("reset_email", None)
        session.pop("reset_otp", None)
        session.pop("otp_time", None)
        session.pop("otp_verified", None)

        flash("Password updated successfully. Please login.", "success")
        return redirect("/login")

    return render_template("reset_password.html")

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()

    return render_template("profile.html", user=user)

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    if request.method == "POST":

        fullname = request.form["fullname"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()

        # Email Validation
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):
            flash("Invalid Email Address!", "danger")
            cursor.execute(
                "SELECT * FROM users WHERE id=%s",
                (session["user_id"],)
            )
            user = cursor.fetchone()
            cursor.close()
            return render_template("edit_profile.html", user=user)

        # Phone Validation
        if not re.match(r'^[6-9]\d{9}$', phone):
            flash("Invalid Phone Number!", "danger")
            cursor.execute(
                "SELECT * FROM users WHERE id=%s",
                (session["user_id"],)
            )
            user = cursor.fetchone()
            cursor.close()
            return render_template("edit_profile.html", user=user)

        # Check duplicate email
        cursor.execute("""
            SELECT id
            FROM users
            WHERE email=%s
            AND id!=%s
        """, (email, session["user_id"]))

        if cursor.fetchone():
            flash("Email already exists!", "danger")

            cursor.execute(
                "SELECT * FROM users WHERE id=%s",
                (session["user_id"],)
            )
            user = cursor.fetchone()
            cursor.close()

            return render_template("edit_profile.html", user=user)

        # Update profile
        cursor.execute("""
            UPDATE users
            SET fullname=%s,
                email=%s,
                phone=%s
            WHERE id=%s
        """, (
            fullname,
            email,
            phone,
            session["user_id"]
        ))

        mysql.connection.commit()

        # Update session
        session["fullname"] = fullname
        session["email"] = email

        flash("Profile Updated Successfully!", "success")

        cursor.close()

        return redirect("/profile")

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()

    return render_template("edit_profile.html", user=user)

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        cursor.execute(
            "SELECT password FROM users WHERE id=%s",
            (session["user_id"],)
        )

        user = cursor.fetchone()

        if not bcrypt.check_password_hash(
                user["password"],
                current_password):

            flash("Current password is incorrect.", "danger")

            cursor.close()

            return render_template("change_password.html")

        if len(new_password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "danger"
            )

            cursor.close()

            return render_template("change_password.html")

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            cursor.close()

            return render_template("change_password.html")

        if bcrypt.check_password_hash(
                user["password"],
                new_password):

            flash(
                "New password cannot be the same as the current password.",
                "danger"
            )

            cursor.close()

            return render_template("change_password.html")

        hashed = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        cursor.execute(
            """
            UPDATE users
            SET password=%s
            WHERE id=%s
            """,
            (
                hashed,
                session["user_id"]
            )
        )

        mysql.connection.commit()

        cursor.close()

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect("/profile")

    cursor.close()

    return render_template("change_password.html")

@app.route("/save-room/<int:room_id>")
def save_room(room_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    # Check if already saved
    cursor.execute("""
        SELECT *
        FROM saved_rooms
        WHERE user_id=%s
        AND room_id=%s
    """, (
        session["user_id"],
        room_id
    ))

    existing = cursor.fetchone()

    if existing:
        flash("Room is already in your saved list.", "warning")
        cursor.close()
        return redirect("/tenant-dashboard")

    cursor.execute("""
        INSERT INTO saved_rooms(user_id, room_id)
        VALUES(%s,%s)
    """, (
        session["user_id"],
        room_id
    ))

    mysql.connection.commit()

    cursor.close()

    flash("Room saved successfully!", "success")

    return redirect("/tenant-dashboard")

@app.route("/saved-rooms")
def saved_rooms():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT
            rooms.*,
            (
                SELECT image_url
                FROM room_images
                WHERE room_id = rooms.id
                LIMIT 1
            ) AS image_url
        FROM saved_rooms
        JOIN rooms
            ON saved_rooms.room_id = rooms.id
        WHERE saved_rooms.user_id = %s
        ORDER BY saved_rooms.id DESC
    """, (session["user_id"],))

    rooms = cursor.fetchall()

    cursor.close()

    return render_template(
        "saved_rooms.html",
        rooms=rooms
    )

@app.route("/remove-saved/<int:room_id>")
def remove_saved(room_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM saved_rooms
        WHERE user_id=%s
        AND room_id=%s
    """, (
        session["user_id"],
        room_id
    ))

    mysql.connection.commit()

    cursor.close()

    flash("Room removed from saved list.", "success")

    return redirect("/saved-rooms")

@app.route("/change-status/<int:room_id>/<status>")
def change_status(room_id, status):

    if "user_id" not in session:
        return redirect("/login")

    if status not in ["Available", "Rented"]:
        flash("Invalid room status.", "danger")
        return redirect("/my-rooms")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE rooms
        SET status=%s
        WHERE id=%s
        AND owner_id=%s
    """, (
        status,
        room_id,
        session["user_id"]
    ))

    mysql.connection.commit()

    cursor.close()

    flash("Room status updated successfully!", "success")

    return redirect("/my-rooms")

@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    # Total users
    cursor.execute("""
        SELECT COUNT(*) AS total_users
        FROM users
    """)
    total_users = cursor.fetchone()["total_users"]

    # Total owners
    cursor.execute("""
        SELECT COUNT(*) AS total_owners
        FROM users
        WHERE role='owner'
    """)
    total_owners = cursor.fetchone()["total_owners"]

    # Total tenants
    cursor.execute("""
        SELECT COUNT(*) AS total_tenants
        FROM users
        WHERE role='tenant'
    """)
    total_tenants = cursor.fetchone()["total_tenants"]

    # Total rooms
    cursor.execute("""
        SELECT COUNT(*) AS total_rooms
        FROM rooms
    """)
    total_rooms = cursor.fetchone()["total_rooms"]

    # Available rooms
    cursor.execute("""
        SELECT COUNT(*) AS available_rooms
        FROM rooms
        WHERE status='Available'
    """)
    available_rooms = cursor.fetchone()["available_rooms"]

    # Rented rooms
    cursor.execute("""
        SELECT COUNT(*) AS rented_rooms
        FROM rooms
        WHERE status='Rented'
    """)
    rented_rooms = cursor.fetchone()["rented_rooms"]

    cursor.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_owners=total_owners,
        total_tenants=total_tenants,
        total_rooms=total_rooms,
        available_rooms=available_rooms,
        rented_rooms=rented_rooms
    )

@app.route("/admin/users")
def admin_users():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT id,
               fullname,
               email,
               phone,
               role
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_users.html",
        users=users
    )

@app.route("/admin/delete-user/<int:user_id>")
def admin_delete_user(user_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect("/login")

    # Prevent admin from deleting their own account
    if user_id == session["user_id"]:
        flash("You cannot delete your own admin account.", "danger")
        return redirect("/admin/users")

    cursor = mysql.connection.cursor(DictCursor)

    # Check whether user exists
    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        cursor.close()
        flash("User not found.", "danger")
        return redirect("/admin/users")

    # Delete user's rooms and their images
    cursor.execute(
        "SELECT id FROM rooms WHERE owner_id=%s",
        (user_id,)
    )

    rooms = cursor.fetchall()

    for room in rooms:

        room_id = room["id"]

        # Get images
        cursor.execute(
            "SELECT image_name FROM room_images WHERE room_id=%s",
            (room_id,)
        )

        images = cursor.fetchall()

        # Delete image files
        for image in images:

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                image["image_name"]
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete room images
        cursor.execute(
            "DELETE FROM room_images WHERE room_id=%s",
            (room_id,)
        )

        # Delete saved room records
        cursor.execute(
            "DELETE FROM saved_rooms WHERE room_id=%s",
            (room_id,)
        )

        # Delete room
        cursor.execute(
            "DELETE FROM rooms WHERE id=%s",
            (room_id,)
        )

    # Delete saved rooms belonging to this user
    cursor.execute(
        "DELETE FROM saved_rooms WHERE user_id=%s",
        (user_id,)
    )

    # Finally delete user
    cursor.execute(
        "DELETE FROM users WHERE id=%s",
        (user_id,)
    )

    mysql.connection.commit()

    cursor.close()

    flash("User deleted successfully!", "success")

    return redirect("/admin/users")

@app.route("/admin/rooms")
def admin_rooms():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT
            rooms.id,
            rooms.title,
            rooms.rent,
            rooms.room_type,
            rooms.city,
            rooms.state,
            rooms.status,
            users.fullname AS owner_name
        FROM rooms
        JOIN users
            ON rooms.owner_id = users.id
        ORDER BY rooms.id DESC
    """)

    rooms = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_rooms.html",
        rooms=rooms
    )

@app.route("/admin/delete-room/<int:room_id>")
def admin_delete_room(room_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect("/login")

    cursor = mysql.connection.cursor(DictCursor)

    # Get room images
    cursor.execute(
        "SELECT image_name FROM room_images WHERE room_id=%s",
        (room_id,)
    )

    images = cursor.fetchall()

    # Delete image files
    for image in images:

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            image["image_name"]
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete image records
    cursor.execute(
        "DELETE FROM room_images WHERE room_id=%s",
        (room_id,)
    )

    # Delete saved-room records
    cursor.execute(
        "DELETE FROM saved_rooms WHERE room_id=%s",
        (room_id,)
    )

    # Delete room
    cursor.execute(
        "DELETE FROM rooms WHERE id=%s",
        (room_id,)
    )

    mysql.connection.commit()

    cursor.close()

    flash("Room deleted successfully!", "success")

    return redirect("/admin/rooms")

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
    owner