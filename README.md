# 🏠 RoomFinder

A modern **Flask-based Room & Flat Rental Platform** that connects **property owners** with **tenants**. Owners can publish room listings with images, pricing, and facilities, while tenants can search, view, and save rooms that match their needs.

---

## ✨ Features

### 🔐 Authentication
- User Registration
- Secure Login
- Role-based Access (Admin, Owner, Tenant)
- Email OTP-based Password Reset
- Change Password
- Profile Management

### 🏡 Owner Features
- Add New Room Listings
- Upload Multiple Room Images using Cloudinary
- Edit Room Details
- Delete Room Listings
- View All Uploaded Rooms

### 👤 Tenant Features
- Search Rooms by City, State, or Room Type
- View Complete Room Details
- Save Favourite Rooms
- Remove Saved Rooms

### 👨‍💼 Admin Features
- Manage Users
- Manage Room Listings

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Python, Flask |
| Frontend | HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Jinja2 |
| Database | MySQL |
| Authentication | Flask-Bcrypt, Flask Sessions |
| Email Service | Flask-Mail (Gmail SMTP) |
| Image Storage | Cloudinary |
| Deployment | Render |

---

## 📁 Project Structure

```text
RoomFinder/
│
├── app.py
├── config.py
├── Procfile
├── requirements.txt
├── README.md
├── .gitignore
├── routes/
├── models/
├── static/
└── templates/
```

---

## 🚀 Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ArmanKumar13/roomfinder.git
cd roomfinder
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` File

Create a `.env` file in the project root directory and add:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=roomfinder

SECRET_KEY=your_secret_key

MAIL_USERNAME=your_gmail_address
MAIL_PASSWORD=your_gmail_app_password

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### 6. Create the Database

Create a MySQL database named:

```text
roomfinder
```

Import your SQL tables into the database.

### 7. Run the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

---

## ☁️ Deployment (Render)

### Build Command

```text
pip install -r requirements.txt
```

### Start Command

```text
gunicorn app:app --bind 0.0.0.0:$PORT
```

### Environment Variables

Configure the following environment variables in your Render Web Service:

```text
MYSQL_HOST
MYSQL_USER
MYSQL_PASSWORD
MYSQL_DB

SECRET_KEY

MAIL_USERNAME
MAIL_PASSWORD

CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
```

---

## 📸 Screenshots

Add screenshots of your application after deployment.

### 🏠 Home Page

*(Add Screenshot)*

### 🔐 Login Page

*(Add Screenshot)*

### 📝 Registration Page

*(Add Screenshot)*

### 👨‍💼 Owner Dashboard

*(Add Screenshot)*

### 👤 Tenant Dashboard

*(Add Screenshot)*

### ➕ Add Room

*(Add Screenshot)*

### 🏡 My Rooms

*(Add Screenshot)*

### 📄 Room Details

*(Add Screenshot)*

### ❤️ Saved Rooms

*(Add Screenshot)*

### 👤 Profile Page

*(Add Screenshot)*

---

## 📌 Key Features

- ✔ Secure User Authentication
- ✔ Role-Based Access Control
- ✔ Email OTP Password Recovery
- ✔ Cloudinary Image Storage
- ✔ Room Search by Location
- ✔ Save Favourite Rooms
- ✔ Responsive Bootstrap 5 Interface
- ✔ Owner Room Management
- ✔ MySQL Database Integration
- ✔ Ready for Render Deployment

---

## 🔒 Security

- Passwords are securely hashed using **Flask-Bcrypt**.
- Sensitive information is stored in a local `.env` file.
- Secret keys and credentials are **never committed** to GitHub.
- Uploaded room images are securely stored using **Cloudinary**.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

## 📄 License

This project is created for **learning, academic, and portfolio** purposes.

---

## 👨‍💻 Author

**Arman Kumar**

- GitHub: https://github.com/ArmanKumar13

---

⭐ If you found this project useful, please consider giving it a **Star** on GitHub!