import streamlit as st
from sqlalchemy import Table, MetaData, create_engine, select
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database metadata setup
metadata = MetaData()

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='141926abhay',
            database='PLMS'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None

# Load tables
def load_tables():
    engine = create_engine("mysql+mysqlconnector://root:141926abhay@localhost:3306/PLMS")
    metadata.reflect(bind=engine)
    return (
        metadata.tables["User"],
        metadata.tables["Parking_Lot"],
        metadata.tables["Vehicle"],
        metadata.tables["Payment"],
        metadata.tables["Parking_Transaction"]
    )

# Retrieve tables
user_table, parking_lot_table,vehicle_table, payment_table, transaction_table = load_tables()

# Rest of your functions
def add_parking_transaction(vehicle_id, entry_time, exit_time):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        insert_statement = """
            INSERT INTO Parking_Transaction (Vehicle_ID, Entry_Time, Exit_Time)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_statement, (vehicle_id, entry_time, exit_time))
        connection.commit()  # Commit the transaction to ensure changes are saved
        connection.close()


def add_user(user_name, email, phone_number,password, user_type):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        insert_statement = f"""
            INSERT INTO User (User_Name, Email, Phone_Number, password,User_Type)
            VALUES (%s, %s, %s, %s,%s)
        """
        cursor.execute(insert_statement, (user_name, email, phone_number,password, user_type))
        connection.commit()

        cursor.execute("SELECT User_ID,User_Name, Email, Phone_Number, User_Type FROM User WHERE Email = %s", (email,))
        user_info = cursor.fetchone()
        connection.close()
        return user_info
        
def delete_user(user_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            delete_statement = """
                DELETE FROM User WHERE User_ID = %s;
            """
            cursor.execute(delete_statement, (user_id,))
            connection.commit()  # Commit the transaction
            connection.close()
            return True
        except Error as e:
            st.error(f"Error deleting user: {e}")
            connection.close()
            return False
    return False


def get_all_parking_transactions():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Parking_Transaction")
        result = cursor.fetchall()
        connection.close()
        return [dict(row) for row in result]

def get_all_operators():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("CALL GetAllOperators()")
        result = cursor.fetchall()
        connection.close()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in result]

def get_all_admins():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("CALL GetAllAdmins()")
        result = cursor.fetchall()
        connection.close()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in result]

def validate_login(user_ID, password, user_type):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Execute the stored procedure with only the input parameter
            cursor.execute("CALL GetUserCredentials(%s, %s)", (user_ID, user_type))
            user_info = cursor.fetchone()
            if user_info:
                user_name, db_password = user_info[0], user_info[1]
                if password == db_password:
                    return True, "Welcome "+user_name
                else:
                    return False, "Invalid credentials. Please check username, password, and user type."
            else:
                return False, "User not found."
        except Error as e:
            return False, f"Database error: {str(e)}"
        finally:
            connection.close()
    else:
        return False, "Unable to connect to the database."
    
def add_vehicle_entry(vehicle_type, license_plate_number):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        entry_time = datetime.now()  # Get current timestamp
    # Insert statement with %s placeholders
        insert_statement = """
            INSERT INTO Vehicle (Vehicle_Type, Entry_Time, Licence_Plate_Number)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_statement, (vehicle_type, entry_time, license_plate_number))
        connection.commit()  # Commit the transaction to save changes
        connection.close()

def get_vehicle_details(license_plate):
    connection = create_connection()
    if connection:
        cursor=connection.cursor()
        query = """
                    SELECT Vehicle_ID, Entry_Time 
                    FROM Vehicle 
                    WHERE Licence_Plate_Number = %s
                    """
        cursor.execute(query, (license_plate,))
        result = cursor.fetchone()
        connection.close()
    return result

def add_parking_lot_entry():
    connection = create_connection()
    if connection:
        cursor=connection.cursor()
        insert_parking_lot_statement = """
            INSERT INTO Parking_Lot (Available)
            VALUES (%s)
        """
        cursor.execute(insert_parking_lot_statement, (False,))
        connection.commit()
        connection.close() 

# Streamlit UI setup and other code remain unchanged
st.set_page_config(page_title="Parking Lot Management System")

# Streamlit UI code as before

# Streamlit UI setup
st.title("Parking Lot Management System")

# Login page
st.header("Login")
user_type = st.radio("Select User Type", ("Operator", "Admin"))
user_ID = st.text_input("User_ID")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

if login_button:
    is_valid, message = validate_login(user_ID, password, user_type)
    if is_valid:
        if user_type == "Operator":
            st.success("Logged in as Operator")
            st.success(message)
            st.session_state['user_type'] = "Operator"
        elif user_type == "Admin":
            st.success("Logged in as Admin")
            st.success(message)
            st.session_state['user_type'] = "Admin"
    else:
        st.error(message)

# Only display functionalities after login
if 'user_type' in st.session_state:
    if st.session_state['user_type'] == "Operator":
        st.subheader("Vehicle Entry")
        vehicle_type = st.radio("Select Vehicle Type:", ("2-wheeler", "4-wheeler"))

        # License plate input
        license_plate_number = st.text_input("Enter License Plate Number:")
        if st.button("Add Vehicle"):
            if license_plate_number:
                add_vehicle_entry(vehicle_type, license_plate_number)
                st.success("Vehicle entry added successfully!")
                add_parking_lot_entry()
            else:
                st.error("Please enter a valid license plate number.")

        st.header("New Parking Transaction")
        license_plate_number = st.text_input("License Plate Number")
        
        if st.button("Generate Bill"):
            vehicle_details = get_vehicle_details(license_plate_number)
            if vehicle_details:
                vehicle_id, entry_time = vehicle_details
                exit_datetime = datetime.now()
            # Add transaction (payment amount is automatically calculated by the trigger)
                add_parking_transaction(vehicle_id, entry_time, exit_datetime)
                st.success("Bill Generated")

                connection = create_connection()
                cursor = connection.cursor()
                cursor.execute("""
                                    SELECT v.Licence_Plate_Number, pt.Entry_Time, pt.Exit_Time, pt.Payment_Amount
                                    FROM Parking_Transaction pt
                                    JOIN Vehicle v ON pt.Vehicle_ID = v.Vehicle_ID
                                    WHERE pt.Vehicle_ID = %s AND pt.Exit_Time = %s
                                """, (vehicle_id, exit_datetime))
                transaction = cursor.fetchone()
                if transaction:
                    license_plate, entry_time, exit_time, payment_amount = transaction
                    st.subheader("Bill Details")
                    st.write(f"License Plate: {license_plate}")
                    st.write(f"Entry Time: {entry_time}")
                    st.write(f"Exit Time: {exit_time}")
                    st.write(f"Payment Amount: ₹{payment_amount}")
        
                connection.close()
            else:
                st.error("Vehicle not found.")

    elif st.session_state['user_type'] == "Admin":
        st.header("Admin Dashboard")

        st.subheader("Add User")
        user_name = st.text_input("User Name")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        password=st.text_input("Create a Password",type="password")
        user_role = st.selectbox("User Type", ["Admin", "Operator"])

        if st.button("Add User"):
            user_info=add_user(user_name, email, phone_number, password,user_role)
            st.success("User added successfully!")
            if user_info:
        # Display user information excluding the password
                st.success("User added successfully!")
                st.write("### User Details")
                st.write(f"**User ID**: {user_info[0]}")
                st.write(f"**User Name**: {user_info[1]}")
                st.write(f"**Email**: {user_info[2]}")
                st.write(f"**Phone Number**: {user_info[3]}")
                st.write(f"**User Type**: {user_info[4]}")

        st.subheader("Delete User")
        delete_user_id = st.text_input("Enter User ID to delete")
        if st.button("Delete User"):
            if delete_user_id:
                is_deleted = delete_user(delete_user_id)
                if is_deleted:
                    st.success(f"User with ID {delete_user_id} has been deleted.")
                else:
                    st.error(f"User with ID {delete_user_id} not found.")
            else:
                st.error("Please enter a valid User ID.")
        
        st.subheader("View Users")
        if st.button("View All operators"):
            operators = get_all_operators()
            st.write(operators)

        if st.button("View All admins"):
            admins = get_all_admins()
            st.write(admins)

