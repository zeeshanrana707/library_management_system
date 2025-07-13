# 📚 Superior University Library Management System

An interactive, elegant, and scalable **Library Management System** built with **Streamlit**, designed for both students and administrators to manage library operations efficiently.

---

## 🚀 Features

### 👩‍💼 Admin Panel
- Add, view, update, and delete books
- Manage registered users
- Monitor real-time activity logs
- Dashboard with live statistics

### 🎓 Student Panel
- Signup/Login with credentials
- Browse and borrow books by ISBN, title, or author
- Return books with optional damage flag
- Automatically generated borrowing receipts

### 📊 Tech Stack
- **Frontend:** Streamlit with responsive, styled UI components
- **Backend:** Python, Pandas for in-memory and persistent data storage
- **Storage:** CSV-based persistent records
- **Utilities:** Base64 receipt generation, dynamic state handling with `st.session_state`

---

## 🧱 System Modules

- `app.py` – The core interactive GUI and routing logic for both students and admin
- `library_record.py` – Handles book CRUD operations and persistent storage
- `modules/` – Includes supporting modules:
  - `book.py` – Book class blueprint
  - `user_record.py` – User signup/login logic
  - `borrow_return.py` – Book lending/return functionality
  - `receipt_generator.py` – Dynamic receipt creator for returns

---

## 🧪 How to Run

1. 📦 Install dependencies:

   ```bash
   pip install streamlit pandas
