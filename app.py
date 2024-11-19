import streamlit as st
from sqlalchemy import Table, MetaData, create_engine, select
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

# Database metadata setup
metadata = MetaData()

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Aka789sh',
            database='PLMS'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None

# Load tables
def load_tables():
    engine = create_engine("mysql+mysqlconnector://root:Aka789sh@localhost:3306/PLMS")
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

def add_user(user_name, email, phone_number,password, user_type):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        # Reset the auto-increment value
        reset_auto_increment = """
            ALTER TABLE User AUTO_INCREMENT = 1;
        """
        cursor.execute(reset_auto_increment)
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
            # Reset the auto-increment value
            reset_auto_increment = """
                ALTER TABLE User AUTO_INCREMENT = 1;
            """
            cursor.execute(reset_auto_increment)
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

def get_all_admins():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("CALL GetAllAdmins()")
        result = cursor.fetchall()
        connection.close()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in result]
    
def get_vehicles_in_parking_lot():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                SELECT v.Vehicle_ID, v.License_Plate_Number, v.Vehicle_Type
                FROM Vehicle v
            """
            cursor.execute(query)
            vehicles = cursor.fetchall()
            return [
                {
                    "Vehicle ID": vehicle[0],
                    "License Plate": vehicle[1],
                    "Vehicle Type": vehicle[2],
                }
                for vehicle in vehicles
            ]
        except Error as e:
            st.error(f"Error fetching vehicles: {e}")
        finally:
            connection.close()
    return []

def get_all_operators():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("CALL GetAllOperators()")
        result = cursor.fetchall()
        connection.close()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in result]


def get_revenue_summary(time_period):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            if time_period == "daily":
                query = """
                    SELECT DATE(Entry_Time) AS Date, COUNT(*) AS Total_Transactions, SUM(Payment_Amount) AS Total_Revenue
                    FROM Parking_Transaction
                    WHERE DATE(Entry_Time) = CURDATE()
                    GROUP BY DATE(Entry_Time)
                """
            elif time_period == "monthly":
                query = """
                    SELECT MONTH(Entry_Time) AS Month, YEAR(Entry_Time) AS Year, COUNT(*) AS Total_Transactions, SUM(Payment_Amount) AS Total_Revenue
                    FROM Parking_Transaction
                    WHERE MONTH(Entry_Time) = MONTH(CURDATE()) AND YEAR(Entry_Time) = YEAR(CURDATE())
                    GROUP BY YEAR(Entry_Time), MONTH(Entry_Time)
                """
            cursor.execute(query)
            result = cursor.fetchall()
            connection.close()
            return result
        except Error as e:
            st.error(f"Error fetching revenue summary: {e}")
        finally:
            connection.close()
    return []

 # Nested function to get the last 5 transactions for a user
def get_last_5_transactions_for_user(user_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                SELECT *
                FROM Parking_Transaction
                WHERE Transaction_ID = (
                    SELECT MAX(Transaction_ID)
                    FROM Parking_Transaction
                    WHERE Vehicle_ID IN (
                        SELECT Vehicle_ID
                        FROM Vehicle
                        WHERE User_ID = %s
                    )
                    ORDER BY Entry_Time DESC
                    LIMIT 5
                )
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            connection.close()
            return result
        except Error as e:
            st.error(f"Error fetching last transaction: {e}")
        finally:
            connection.close()
    return None     

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
        # Reset the auto-increment value
        reset_auto_increment = """
            ALTER TABLE Vehicle AUTO_INCREMENT = 1;
        """
        cursor.execute(reset_auto_increment)
        entry_time = datetime.now()  # Get current timestamp
    # Insert statement with %s placeholders
        insert_statement = """
            INSERT INTO Vehicle (Vehicle_Type, Entry_Time, License_Plate_Number)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_statement, (vehicle_type, entry_time, license_plate_number))
        connection.commit()  # Commit the transaction to save changes
        connection.close()

def add_parking_lot_entry():
    connection = create_connection()
    if connection:
        cursor=connection.cursor()
        insert_parking_lot_statement = """
            INSERT INTO Parking_Lot (Available)
            VALUES (%s)
        """
        cursor.execute(insert_parking_lot_statement, ('No',))
        connection.commit()
        connection.close() 

def update_user_details(user_id, user_name, email, phone_number, user_type, password):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Call the SQL function
        cursor.execute(
            "SELECT update_user_details(%s, %s, %s, %s, %s, %s)",
            (user_id, user_name, email, phone_number, user_type, password)
        )
        result = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as e:
        return f"Error: {e}"
    
def calculate_payment(vehicle_type, entry_time, exit_time):
    base_rate = 20 if vehicle_type == '2-wheeler' else 30
    additional_rate = 10 if vehicle_type == '2-wheeler' else 20

    # Calculate total parked hours
    total_hours = max(0, (exit_time - entry_time).total_seconds() // 3600)


    # Calculate payment
    if total_hours <= 3:
        return base_rate
    else:
        additional_payment = ((total_hours - 3) / 3) * additional_rate
        return base_rate + additional_payment

# Function to add transaction
def add_parking_transaction(license_plate_number, exit_time):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch vehicle details
        cursor.execute(
            "SELECT Vehicle_Type, Vehicle_ID,Entry_Time FROM Vehicle WHERE License_Plate_Number = %s",
            (license_plate_number,)
        )
        vehicle = cursor.fetchone()
        if not vehicle:
            return "Vehicle not found!"

        # Calculate payment
        entry_time = vehicle['Entry_Time']
        vehicle_type = vehicle['Vehicle_Type']
        Vehicle_ID=vehicle['Vehicle_ID']
        payment_amount = calculate_payment(vehicle_type, entry_time, exit_time)

        # Insert transaction
        cursor.execute(
            "INSERT INTO Parking_Transaction (License_Plate_Number, Exit_Time, Payment_Amount,Entry_Time,Vehicle_ID) VALUES (%s, %s, %s,%s,%s)",
            (license_plate_number, exit_time, payment_amount,entry_time,Vehicle_ID)
        )
        conn.commit()
        return "Parking transaction added successfully!"
    except mysql.connector.Error as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

def showbill(license_plate_number):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                pt.Transaction_ID,
                pt.Vehicle_ID,
                pt.License_Plate_Number,
                pt.Entry_Time,
                pt.Exit_Time,
                pt.Payment_Amount
            FROM Parking_Transaction pt
            WHERE pt.License_Plate_Number = %s;
        """
        cursor.execute(query, (license_plate_number,))
        bill_details = cursor.fetchone()  # Fetch the result
        return bill_details
    
def add_payment(transaction_id, payment_method, payment_amount, payment_status):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            insert_statement = """
                INSERT INTO Payment (Transaction_ID, Payment_Method, Payment_Amount, Payment_Status)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_statement, (transaction_id, payment_method, payment_amount, payment_status))
            connection.commit()  # Commit the transaction to save changes
            st.success("Payment recorded successfully!")
        except Error as e:
            st.error(f"Error adding payment: {e}")
        finally:
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
        st.subheader("Vehicles Currently in Parking Lot")
        vehicles = get_vehicles_in_parking_lot()
        if vehicles:
            st.table(vehicles)  # Use a Streamlit table to display the vehicles
        else:
            st.info("No vehicles currently in the parking lot.")
        
        # Vehicle Entry Section
        st.subheader("Vehicle Entry")
        vehicle_type = st.radio("Select Vehicle Type:", ("2-wheeler", "4-wheeler"))

        license_plate_number = st.text_input("Enter License Plate Number:")
        if st.button("Add Vehicle"):
            if license_plate_number:
                add_vehicle_entry(vehicle_type, license_plate_number)
                st.success("Vehicle entry added successfully!")
                add_parking_lot_entry()
            else:
                st.error("Please enter a valid license plate number.")

        st.subheader("New Parking Transaction")
        license_plate_number = st.text_input("License Plate Number")
        if st.button("Generate Bill"):
            exit_datetime = datetime.now()
            message=add_parking_transaction(license_plate_number,exit_datetime)
            if(message):
                bill_details=showbill(license_plate_number)
                if bill_details:
                    st.write("### Bill Details:")
                    st.write(f"**Transaction ID**: {bill_details['Transaction_ID']}")
                    st.write(f"**Vehicle ID**: {bill_details['Vehicle_ID']}")
                    st.write(f"**License Plate**: {bill_details['License_Plate_Number']}")
                    st.write(f"**Entry Time**: {bill_details['Entry_Time']}")
                    st.write(f"**Exit Time**: {bill_details['Exit_Time']}")
                    st.write(f"**Payment Amount**: ₹{bill_details['Payment_Amount']}")
                else:
                    st.error("No bill details found for the given Transaction ID.")
                
                st.success(message)
        
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI"], key="payment_method")
        payment_status = st.selectbox("Payment Status", ["Pending", "Completed", "Failed"], key="payment_status")
        
        if st.button("Record Payment"):
            bill_details=showbill(license_plate_number)
            # Payment section
            add_payment(bill_details['Transaction_ID'], payment_method, bill_details['Payment_Amount'], payment_status)
            st.success("Payment recorded successfully!")


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

        st.subheader("Update User Details")
        # Input fields for updating user details
        user_id = st.number_input("User ID", min_value=1, step=1)
        user_name = st.text_input("User Name (Leave blank to skip)")
        email = st.text_input("Email (Leave blank to skip)")
        phone_number = st.text_input("Phone Number (Leave blank to skip)")
        user_type = st.text_input("User Type (Leave blank to skip)")
        password = st.text_input("Password (Leave blank to skip)")

        # Button to update details
        if st.button("Update User Details"):
            if user_id:
            #Pass None for fields that are left blank
                result = update_user_details(
                    user_id,
                    user_name if user_name.strip() else None,
                    email if email.strip() else None,
                    phone_number if phone_number.strip() else None,
                    user_type if user_type.strip() else None,
                    password if password.strip() else None
                )
                st.success(result)
            else:
                st.error("Please enter a valid User ID.")
        
        st.subheader("Last 5 Parking Transactions for User")
        user_id = st.text_input("Enter User ID to find last 5 transactions:")
        if st.button("Fetch Last 5 Transactions"):
            last_transactions = get_last_5_transactions_for_user(user_id)
            if last_transactions:
                st.write("### Last 5 Transactions")
                for transaction in last_transactions:
                    st.write(f"Transaction ID: {transaction[0]}")
                    st.write(f"Vehicle ID: {transaction[1]}")
                    st.write(f"Entry Time: {transaction[2]}")
                    st.write(f"Exit Time: {transaction[3]}")
                    st.write(f"Payment Amount: ₹{transaction[4]}")
                    st.write("---")  # Separator for readability
            else:
                st.info("No transactions found for this user.")


        st.subheader("Revenue Summary")
        if st.button("View Today's Summary"):
            daily_revenue = get_revenue_summary("daily")
            if daily_revenue:
                st.write("### Today's Summary")
                for record in daily_revenue:
                    st.write(f"Date: {record[0]}")
                    st.write(f"Total Transactions: {record[1]}")
                    st.write(f"Total Revenue: ₹{record[2]}")
            else:
                st.info("No transactions recorded for today.")

        if st.button("View This Month's Summary"):
            monthly_revenue = get_revenue_summary("monthly")
            if monthly_revenue:
                st.write("### This Month's Summary")
                for record in monthly_revenue:
                    st.write(f"Month: {record[0]}/{record[1]}")
                    st.write(f"Total Transactions: {record[2]}")
                    st.write(f"Total Revenue: ₹{record[3]}")
            else:
                st.info("No transactions recorded for this month.")


''' 
        st.subheader("New Parking Transaction")
        license_plate_number = st.text_input("License Plate Number")
        if st.button("Generate Bill"):
            exit_datetime = datetime.now()
            message=add_parking_transaction(license_plate_number,exit_datetime)
            if(message):
                bill_details=showbill(license_plate_number)
                if bill_details:
                    st.write("### Bill Details:")
                    st.write(f"**Transaction ID**: {bill_details['Transaction_ID']}")
                    st.write(f"**Vehicle ID**: {bill_details['Vehicle_ID']}")
                    st.write(f"**License Plate**: {bill_details['License_Plate_Number']}")
                    st.write(f"**Entry Time**: {bill_details['Entry_Time']}")
                    st.write(f"**Exit Time**: {bill_details['Exit_Time']}")
                    st.write(f"**Payment Amount**: ₹{bill_details['Payment_Amount']}")
                else:
                    st.error("No bill details found for the given Transaction ID.")
                st.success(message)
'''