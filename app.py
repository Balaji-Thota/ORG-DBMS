import tkinter as tk
from tkinter import messagebox, ttk
from db_op import authenticate_user, get_table_names, execute_query, display_table_result

# global variables to store the login values
usrnm = None
pswd = None

# Function to handle login button press
def on_login_button_pressed():
    username = entry_username.get()
    password = entry_password.get()
    usrnm, pswd = username, password

    success, user = authenticate_user(username, password)

    if success:
        root.withdraw()  # Hide login window
        show_home_page(usrnm, pswd, user)
    else:
        messagebox.showerror("Login", "Invalid credentials")

# Function to display home page
def show_home_page(usrnm, pswd, user):
    home_page = tk.Toplevel(root)
    home_page.title(f"Welcome {user}")

    # Create dropdown to select tables
    table_label = tk.Label(home_page, text="Select Table:")
    table_label.grid(row=0, column=0, padx=10, pady=10)

    table_names = get_table_names(usrnm, pswd)
    selected_table = tk.StringVar()
    table_dropdown = ttk.Combobox(home_page, textvariable=selected_table, values=table_names)
    table_dropdown.grid(row=0, column=1, padx=10, pady=10)

     # Function to update table data based on selection
    def update_table_data(event):
        selected_table_name = selected_table.get()
        query_text.delete('1.0', tk.END)  # Clear the query text area
        query_text.insert(tk.END, f"SELECT * FROM {selected_table_name};")

    # Bind the update_table_data function to the table dropdown selection event
    table_dropdown.bind("<<ComboboxSelected>>", update_table_data)

    # Create text area for SQL query
    query_label = tk.Label(home_page, text="Enter SQL Query:")
    query_label.grid(row=1, column=0, padx=10, pady=10)

    query_text = tk.Text(home_page, height=5, width=50)
    query_text.grid(row=1, column=1, padx=10, pady=10)

    # Function to execute SQL query and display results
    def execute_and_display():
        query_result = execute_query(usrnm, pswd, selected_table.get(), query_text.get("1.0", tk.END))
        if query_result:
            display_table_result(query_result, username=usrnm, password=pswd, selected_table=selected_table.get())

    # Create button to execute SQL query
    execute_button = tk.Button(home_page, text="Execute Query", command=execute_and_display)
    execute_button.grid(row=2, column=0, columnspan=2, pady=10)

    home_page.grid_rowconfigure(1, weight=1)
    home_page.grid_columnconfigure(0, weight=1)


# Create tkinter window
root = tk.Tk()
root.title("Login Page")
root.geometry("300x200")

# Create username label and entry
label_username = tk.Label(root, text="Username:")
label_username.grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=5, pady=5)

# Create password label and entry
label_password = tk.Label(root, text="Password:")
label_password.grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

# Create login button
button_login = tk.Button(root, text="Login", command=on_login_button_pressed)
button_login.grid(row=2, column=0, columnspan=2, pady=10)

# Run tkinter main loop
root.mainloop()