import pymysql
from tkinter import messagebox, ttk
import pandas as pd
import tkinter as tk
from tksheet import Sheet

# Function to authenticate user
def authenticate_user(username, password):
    try:
        # Connect to MySQL database
        connection = pymysql.connect(host='localhost',
                                     user=username,
                                     password= password,
                                     database='Orgdb',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection:
            # Create cursor object
            with connection.cursor() as cursor:
                # Execute SQL query to check user credentials
                sql = "SELECT USER();"
                cursor.execute(sql)
                user = cursor.fetchone()
                print(user)
                if user:
                    return True, user['USER()'].split('@')[0]
                else:
                    return False, None

    except pymysql.Error as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Database error: {e}")
        return False, None
    
# Function to get table names from database
def get_table_names(username, password):
    connection = pymysql.connect(host='localhost',
                                     user=username,
                                     password= password,
                                     database='Orgdb',
                                     cursorclass=pymysql.cursors.DictCursor)
    if connection:
        table_names = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print(tables)
                for table in tables:
                    table_names.append(table['Tables_in_orgdb'])  
            connection.close()
        except pymysql.Error as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"Error getting table names: {e}")
        return table_names
    else:
        return None


# Function to execute SQL query
def execute_query(username, password, table_name, query):
    connection = pymysql.connect(host='localhost',
                                     user=username,
                                     password= password,
                                     database='Orgdb',
                                     cursorclass=pymysql.cursors.DictCursor)
    if connection:
        try:
            with connection.cursor() as cursor:
                if 'select' in query.lower():
                    cursor.execute(query)
                    result = cursor.fetchall()
                    return result
                elif 'insert' in query.lower() or 'update' in query.lower():
                    try:
                        cursor.execute(query)
                        connection.commit()  # Commit changes to the database
                        return "Query executed successfully"  
                    except Exception as e:
                        connection.rollback()  # Rollback changes if an error occurs
                        return f"Error executing query: {e}"
            connection.close()
        except pymysql.Error as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"Error executing query: {e}")
    else:
        return None


def display_table_result(data, username, password, selected_table):
    if type(data) is str:
        if 'error' in data.lower():
            messagebox.showerror("Error", data)
        else:
            messagebox.showinfo("Information", data)
    else:
        df= pd.DataFrame(data)
        column_names = df.columns.to_list()
        popup = tk.Toplevel()
        popup.title("Query Results")
        
        # Create a tksheet object
        sheet = Sheet(popup)
        sheet.grid()

        # Convert the data to a list of lists
        data_list = df.values.tolist()

        # Insert data into the tksheet object
        sheet.set_sheet_data(data_list)

        # Configure the sheet with column names
        sheet.headers(column_names)

        # Enable bindings
        sheet.enable_bindings(("single",
                                         "drag_select",
                                         "column_drag_and_drop",
                                         "row_drag_and_drop",
                                         "column_select",
                                         "row_select",
                                         "column_width_resize",
                                         "double_click_column_resize",
                                         "row_width_resize",
                                         "column_height_resize",
                                         "arrowkeys",
                                         "row_height_resize",
                                         "double_click_row_resize",
                                         "right_click_popup_menu",
                                         "rc_insert_column",
                                         "rc_delete_column",
                                         "rc_insert_row",
                                         "rc_delete_row",
                                         "copy",
                                         "cut",
                                         "paste",
                                         "delete",
                                         "undo",
                                         "edit_cell"))
        
        def update_data():
            # Get the sheet data when the update button is clicked
            updated_data = sheet.get_sheet_data()
            updated_df = pd.DataFrame(updated_data, columns=column_names)
            changes = df.compare(updated_df)

            if not changes.empty:
                updt_db_with_chngs(username=username, password=password, selected_table=selected_table, changes=changes)

        # Insert, Update, Delete buttons
        update_button = tk.Button(popup, text="update database", command=update_data)

        update_button.grid(row=1, column=0, pady=5)

        popup.mainloop()


def updt_db_with_chngs(username, password, selected_table, changes):
    try:
        connection = pymysql.connect(host='localhost',
                                     user=username,
                                     password=password,
                                     database='orgdb',
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        for index, change in changes.iterrows():
            set_values = ', '.join([f"`{column[0]}` = '{value}'" for column, value in change.items() if pd.notnull(value)])
            # set_values =  ', '.join([f"{col} = %s" for col in change.index])
            if set_values:
                sql = f"UPDATE {selected_table} SET {set_values} WHERE id = {index+1}"
                try:
                    # Convert change values to a list, including the index as the last value
                    values = list(change.values) + [index+1]
                    print(f"Executing SQL: {sql}")  # Debugging statement

                    cursor.execute(sql)
                    connection.commit()
                    messagebox.showinfo("Success", "Database updated successfully")
                except Exception as e:
                    connection.rollback()
                    messagebox.showerror("Error", f"Failed to update database: {e}")
    finally:
        connection.close()
