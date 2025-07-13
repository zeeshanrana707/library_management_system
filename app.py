# File: app.py
import streamlit as st
from library_record import LibraryRecord
from modules.book import Book
from modules.user_record import UserRecord
from modules.borrow_return import BorrowReturn
from modules.receipt_generator import generate_receipt
from datetime import datetime, timedelta
import base64

ADMIN_CREDENTIALS = {'student_id': 'admin', 'password': 'admin123'}

library = LibraryRecord()
users = UserRecord()
borrow_system = BorrowReturn()

st.set_page_config(page_title="Superior University Library", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f0f2f6;}
    .stButton>button {color: white; background: #2c3e50; border-radius: 10px;}
    .stTextInput>div>div>input {border-radius: 5px;}
    .login-box {padding: 2rem; background-color: #fff; border-radius: 10px; box-shadow: 0 0 10px #ccc;}
    </style>
""", unsafe_allow_html=True)

st.title("📚 Superior University Library")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title("User Authentication")
    role = st.sidebar.radio("Login As", ["Student", "Admin"])

    if role == "Admin":
        st.subheader("🔐 Admin Login")
        admin_id = st.text_input("Admin ID")
        admin_pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_id == ADMIN_CREDENTIALS['student_id'] and admin_pw == ADMIN_CREDENTIALS['password']:
                st.session_state.logged_in = True
                st.session_state.user = {'username': 'Administrator', 'role': 'admin', 'student_id': 'admin'}
                st.success("Admin logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid admin credentials.")

    else:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("🧑‍🎓 Student Login / Signup")
        auth_choice = st.radio("Choose Option", ["Login", "Signup"])

        if auth_choice == "Signup":
            sid = st.text_input("Student ID")
            uname = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.button("Signup"):
                success, msg = users.signup_user(sid, uname, pwd, "student")
                st.success(msg) if success else st.error(msg)

        else:
            sid = st.text_input("Student ID")
            pwd = st.text_input("Password", type="password")
            if st.button("Login"):
                user = users.authenticate_user(sid, pwd)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid student credentials.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# Authenticated Section
user = st.session_state.user
st.sidebar.markdown(f"👋 Welcome, **{user['username']}** ({user['role']})")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

if user['role'] == 'admin':
    admin_page = st.sidebar.radio("📂 Admin Menu", ["Dashboard", "Add Book", "View Books", "Manage Users", "Activity Log"])

    if admin_page == "Dashboard":
        st.markdown("### 📊 Library Overview")
        stats1, stats2 = st.columns(2)
        stats1.metric("Total Books", len(library.get_all_books()))
        stats2.metric("Total Users", len(users.df))

    elif admin_page == "Add Book":
        st.header("➕ Add New Book")
        with st.form("add_book"):
            isbn = st.text_input("ISBN")
            title = st.text_input("Title")
            author = st.text_input("Author")
            price = st.number_input("Price", min_value=0.0)
            qty = st.number_input("Quantity", min_value=1, value=1)
            submit = st.form_submit_button("Add Book")
            if submit:
                b = Book(isbn.strip(), title, author, int(qty), price)
                ok, msg = library.add_book(b)
                st.success(msg) if ok else st.error(msg)

    elif admin_page == "View Books":
        st.header("📚 All Books")
        search_option = st.selectbox("Search By", ["All", "Title", "Author", "ISBN"])
        search_query = st.text_input("Search Query")
        books = library.get_all_books()
        if search_option != "All" and search_query:
            books = books[books[search_option.lower()].str.contains(search_query, case=False, na=False)]
        st.dataframe(books, use_container_width=True)

    elif admin_page == "Manage Users":
        st.header("🧑‍💻 Manage Users")
        all_users = users.df[users.df['role'] == 'student']
        st.dataframe(all_users[['student_id', 'username']], use_container_width=True)

        del_id = st.text_input("Enter Student ID to Delete")
        if st.button("Delete User"):
            ok, msg = users.delete_user(del_id.strip())
            st.success(msg) if ok else st.error(msg)

    elif admin_page == "Activity Log":
        st.header("📑 Admin Activity Log")
        st.dataframe(borrow_system.df, use_container_width=True)

else:
    student_page = st.sidebar.radio("📘 Student Menu", ["My Borrowed Books", "Borrow Book", "Return Book"])

    if student_page == "My Borrowed Books":
        st.header("📘 Your Borrow History")
        history = borrow_system.df[borrow_system.df['student_id'] == user['student_id']]
        st.dataframe(history, use_container_width=True)

    elif student_page == "Borrow Book":
        st.header("📖 Borrow a Book")
        search_option = st.selectbox("Search By", ["ISBN", "Title", "Author"])
        search_query = st.text_input("Search Query")

        if st.button("Search Book"):
            book = library.find_book(search_query.strip(), search_by=search_option.lower())
            if book:
                st.session_state['selected_book'] = book  # Store in session state
            else:
                st.warning("Book not found.")

        # Display selected book info
        if 'selected_book' in st.session_state:
            book = st.session_state['selected_book']
            st.write(f"**Title:** {book['title']} | **Author:** {book['author']} | **Available:** {book['quantity']}")

            if st.button("Borrow Book"):
                already_borrowed = borrow_system.df[
                    (borrow_system.df['student_id'] == user['student_id']) &
                    (borrow_system.df['isbn'].astype(str).str.strip() == book['isbn']) &
                    (borrow_system.df['return_date'] == '')
            ]
                if not already_borrowed.empty:
                    st.warning("You already borrowed this book and haven't returned it.")
                elif book['quantity'] > 0:
                    borrow_system.borrow_book(user['student_id'], book['isbn'], book['price'], book['title'])
                    library.update_book(book['isbn'], {'quantity': book['quantity'] - 1})
                    due_date = datetime.today() + timedelta(days=7)
                    st.success(f"Book borrowed successfully. Due date: {due_date.strftime('%Y-%m-%d')}")
                    del st.session_state['selected_book']  # Optional: clear session state after borrow
                else:
                    st.warning("No copies available.")


    elif student_page == "Return Book":
        st.header("📤 Return a Book")

        borrowed = borrow_system.df[
            (borrow_system.df['student_id'].astype(str) == str(user['student_id'])) &
            ((borrow_system.df['return_date'] == '') | (borrow_system.df['return_date'].isna()))
        ]

        if borrowed.empty:
            st.info("You have no borrowed books pending return.")
        else:
            st.dataframe(borrowed[['isbn', 'book_name', 'borrow_date']], use_container_width=True)

            isbn = st.text_input("Enter ISBN to Return").strip()
            damaged = st.checkbox("Book is Damaged (20% fine)")

            if st.button("Return Book"):
                result = borrow_system.return_book(user['student_id'], isbn, 'yes' if damaged else 'no')

                if result:
                    book = library.find_book(isbn.strip(), search_by="isbn")
                    if book:
                        library.update_book(isbn, {'quantity': book['quantity'] + 1})

                    receipt = generate_receipt(result)
                    b64 = base64.b64encode(receipt.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="receipt.txt">📄 Download Receipt</a>'
                    st.success("Return successful. Here is your receipt:")
                    st.code(receipt)
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error("No borrowed record found for the entered ISBN.")
