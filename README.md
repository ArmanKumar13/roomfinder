# RoomFinder

RoomFinder is a Flask-based room and flat listing web application where **owners** can add properties with photos and details, and **tenants** can search, save, and view rooms near their location.

## Features

- User registration and login
- Role-based access for Admin, Owner, and Tenant
- OTP-based forgot password flow through email
- Owner dashboard to add, edit, delete, and manage rooms
- Image upload and storage using Cloudinary
- Tenant dashboard with room search
- Save / remove saved rooms
- Profile management
- Password change and reset functionality

## Tech Stack

- **Frontend:** HTML, Bootstrap, Bootstrap Icons, Jinja2
- **Backend:** Python, Flask
- **Database:** MySQL
- **Authentication:** Flask-Bcrypt, Flask session
- **Email OTP:** Flask-Mail + Gmail SMTP
- **Image Storage:** Cloudinary

## Project Structure

```text
RoomFinder/
├── app.py
├── config.py
├── Procfile
├── requirements.txt
├── .env
├── templates/
├── static/
├── uploads/
├── routes/
├── models/
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/roomfinder.git
cd roomfinder
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Create a file named `.env` in the project root and add:

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

### 5. Create the database

Create a MySQL database named `roomfinder` and import your SQL tables.

### 6. Run the app

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Deployment

This project is designed to be deployed on **Render**.

### Render settings

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

Add the same environment variables from your `.env` file in the Render dashboard.

## Environment Variables

Required variables:

- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DB`
- `SECRET_KEY`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Main Pages

- Home
- Register
- Login
- Tenant Dashboard
- Owner Dashboard
- Add Room
- Edit Room
- Room Details
- Saved Rooms
- Profile
- Forgot Password / OTP Reset

## Notes

- Uploaded room images are stored in Cloudinary for deployment safety.
- Local `.env`, `venv/`, and cache files are ignored from GitHub using `.gitignore`.
- Do not commit any secret values to public repositories.

## License

This project is created for learning, academic, and portfolio purposes.
