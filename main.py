import mysql.connector

# Connect to the MySQL database
db = mysql.connector.connect(
    host="<hostname>",
    user="<username>",
    password="<password>",
    database="<database_name>"
)
cursor = db.cursor()

# Create the products table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS products (id INT PRIMARY KEY, name VARCHAR(255), price DECIMAL(10, 2), qty INT)")

# Function to add a product to the database
def add_product():
    try:
        product_id = int(input("Enter product ID: "))
        name = input("Enter product name: ")
        price = float(input("Enter product price: "))
        qty = int(input("Enter product quantity: "))

        if product_id <= 0 or price <= 0 or qty <= 0:
            print("Invalid input. ID, price, and quantity should be numbers greater than zero.")
        else:
            cursor.execute("INSERT INTO products (id, name, price, qty) VALUES (%s, %s, %s, %s)", (product_id, name, price, qty))
            db.commit()
            print("Product added successfully.")
    except ValueError:
        print("Invalid input. ID, price, and qty should be numbers greater than zero.")
    except Exception:
        print("Duplicate ID. Try again.")

# Function to increase the quantity of a product
def increase_qty():
    try:
        product_id = int(input("Enter product ID: "))
        
        # Check if the product with the given ID exists
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            print("Product not found.")
        else:
            qty = int(input("Enter quantity to increase: "))

            if qty <= 0:
                print("Quantity should be greater than zero.")
            else:
                cursor.execute("UPDATE products SET qty = qty + %s WHERE id = %s", (qty, product_id))
                db.commit()
                print("Quantity updated successfully.")
    except ValueError:
        print("Invalid input. ID and quantity should be numbers greater than zero.")

# Function to search for a product by ID or name
def search_product():
    search_term = input("Enter product ID or name to search: ")

    cursor.execute("SELECT * FROM products WHERE id = %s OR name LIKE %s", (search_term, f"%{search_term}%"))
    products = cursor.fetchall()

    if not products:
        print("Product not found.")
    else:
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Quantity: {product[3]}")

# Function to delete a product by ID or name
def delete_product():
    search_term = input("Enter product name to search for products to delete: ")

    cursor.execute("SELECT * FROM products WHERE name LIKE %s", (f"%{search_term}%",))
    products = cursor.fetchall()

    if not products:
        print("Product not found.")
    else:
        print("Matching Products:")
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Quantity: {product[3]}")

        product_id_to_delete = int(input("Enter the ID of the product you want to delete: "))
        found = False

        for product in products:
            if product_id_to_delete == product[0]:
                found = True
                confirm = input("Do you want to delete this product? (y/n): ").lower()
                if confirm == "y":
                    cursor.execute("DELETE FROM products WHERE id = %s", (product_id_to_delete,))
                    db.commit()
                    print("Product deleted successfully.")
                elif confirm == "n":
                    print("Deletion cancelled.")
                else:
                    print("Invalid option.")
                break

        if not found:
            print("Product not found.")

# Function to view all products in the database
def view_all_products():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if not products:
        print("No products in the database.")
    else:
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Quantity: {product[3]}")

# Function to generate a bill for a customer
def generate_bill():
    total_price = 0
    bill = {}

    while True:
        try:
            product_id = int(input("Enter product ID to add to the bill (0 to finish): "))
            if product_id < 0:
                print("Invalid input. Product ID should be numbers greater than zero.")
            if product_id == 0:
                break

            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            if not product:
                print("Product not found.")
            else:
                qty = int(input(f"Enter quantity for {product[1]}: "))

                if qty <= 0:
                    print("Quantity should be greater than zero.")
                elif qty > product[3]:
                    print("Insufficient stock.")
                else:
                    if product_id in bill:
                        bill[product_id][1] += qty  # Update quantity if the product is already in the bill
                    else:
                        bill[product_id] = [product[1], qty, product[2]]  # Add the product to the bill

                    cursor.execute("UPDATE products SET qty = qty - %s WHERE id = %s", (qty, product_id))
                    db.commit()
        except ValueError:
            print("Invalid input. ID and quantity should be numbers greater than zero.")

    if not bill:
        print("No products selected. Bill generation cancelled.")
        return

    print("\n************ Invoice *************")
    for product_id, (product_name, qty, price) in bill.items():
        product_total = qty * price
        total_price += product_total
        print(f"{product_name} @ {price:.2f} x{qty} = {product_total:.2f}")

    print(f"Total Price: {total_price:.2f}")
    print("**********************************")

# Function to change the price of a product
def change_price():
    try:
        product_id = int(input("Enter product ID to change the price: "))
        
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            print("Product not found.")
        else:
            new_price = float(input(f"Enter the new price for {product[1]}: "))

            cursor.execute("UPDATE products SET price = %s WHERE id = %s", (new_price, product_id))
            db.commit()
            print("Price updated successfully.")
    except ValueError:
        print("Invalid input. Price should be numbers.")

# Main program loop
while True:
    print("\nRetail Shop Billing System")
    print("1. Add Product")
    print("2. Increase Quantity")
    print("3. Change Price")
    print("4. Search Product")
    print("5. Delete Product")
    print("6. View All Products")
    print("7. Generate Bill")
    print("8. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_product()
    elif choice == "2":
        increase_qty()
    elif choice == "3":
        change_price()
    elif choice == "4":
        search_product()
    elif choice == "5":
        delete_product()
    elif choice == "6":
        view_all_products()
    elif choice == "7":
        generate_bill()
    elif choice == "8":
        print("Thank you for using Retail Shop Billing System.")
        break
    else:
        print("Invalid choice. Please try again.")

# Close the database connection
db.close()
