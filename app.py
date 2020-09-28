from peewee import *
from collections import OrderedDict
import datetime
import csv
import os
import sys

db = SqliteDatabase('inventory.db')

class Product(Model):
    # Used http://docs.peewee-orm.com/en/latest/peewee/models.html#creating-model-tables to help with Peewee documentation
    product_id = AutoField()
    product_name = CharField(max_length=200, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateTimeField()

    class Meta:
        database = db

def read_inventory():
    with open('inventory.csv', newline='') as file:
        inv_reader = csv.DictReader(file, delimiter="," )
        rows = list(inv_reader)
        for row in rows:
            row['product_quantity'] = int(row['product_quantity'])
            row['product_price'] = int(row['product_price'].replace('$', '').replace('.', ''))
            row['date_updated'] = datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y')
        for row in rows:
            try:
                Product.create(
                    product_name = row['product_name'],
                    product_quantity = row['product_quantity'],
                    product_price = row['product_price'],
                    date_updated = row['date_updated']
                ).save()
            except:
                # If item already exists, it updates the item with current information. 
                updated = Product.get(product_name = row['product_name'])
                updated.product_quantity = row['product_quantity']
                updated.product_price = row['product_price']
                updated.date_updated = row['date_updated']
                updated.save()



def menu_loop():
    """Show The Menu"""
    choice = None
    while choice != 'q':
        clear()
        print('='* len("menu options"))
        print("Menu Options")
        print('='* len("menu options"))
        print("\nEnter 'q' to quit")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        
        while True:
            try:
                choice = input('Action: ').lower().strip()
                if choice in menu.keys():
                    menu[choice]()
                    break
                elif choice == 'q':
                    sys.exit()
                else:
                    raise ValueError
            except ValueError:
                print("Please select a valid action [v/a/b]")

def clear():
    os.system('cls' if os.name =='nt' else 'clear')


def view_product():
    """View a single product"""
    clear()
    while True:
        search_query = input("\nPlease enter the product id: ")
        try:
            search_query = int(search_query)
            selected_product = Product.select()
            selected_product = selected_product.where(Product.product_id == search_query)
            if selected_product:
                break
            else:
                clear()
                print("That Product ID does not exist.")
                raise ValueError      
            break
        except ValueError as err:
            print("Please enter a valid product #")
    if selected_product:
        for product in selected_product:
            clear()
            print("Product name: {}".format(product.product_name))
            print("Product price: ${}".format(product.product_price * .01))
            print("Product quantity: {}".format(product.product_quantity))
            print("Date updated: {}".format(product.date_updated))
            print('\ns) Search another product')
            print('q) return to main menu')
            
            next_action = input('Action: [s/q] ').lower().strip()
            while True:
                if next_action =='q':
                    break
                elif next_action =='s':
                    view_product()
                    break
                else:
                    next_action = input('Please select a valid Action: [s/q] ').lower().strip()


def add_product():
    """Add/Update a product"""
    clear()
    new_product_name = input("Enter the name of the product: ")
    while True:
        new_product_quantity = input("What is the quantity of this product? ")
        try:
            new_product_quantity = int(new_product_quantity)
            break
        except ValueError:
            print("\nplease enter a number")
    while True:
        new_product_price = input("Please enter the price of this product: $")
        try:
            new_product_price = float(new_product_price)
            new_product_price = int(new_product_price/.01)
        except ValueError:
            print("\nplease enter a number")
        else:
            try:
                Product.create(
                    product_name = new_product_name,
                    product_quantity = new_product_quantity,
                    product_price = new_product_price,
                    date_updated = datetime.datetime.now()
                ).save()
                print("\nInventory item added!")
            except IntegrityError:
                update = Product.get(product_name=new_product_name)
                update.product_quantity = new_product_quantity
                update.product_price = new_product_price
                update.date_updated = datetime.datetime.now()
                update.save()
                print('\nInventory item updated!')
                   
            
            print("\na) Add/Update another product")
            print('q) Return to main menu')
            
            next_action = input('Action: [a/q] ').lower().strip()
            while True:
                if next_action =='q':
                    menu_loop()
                elif next_action =='a':
                    add_product()
                    break
                else:
                    next_action = input('Please select a valid Action: [s/q] ').lower().strip()

def backup_inventory():
    """Backup the inventory to a csv"""
    clear()
    with open('Inventory_Backup.csv', 'w', newline='') as backupfile:
        fieldnames = ['product_id', 'product_name', 'product_quantity', 'product_price', 'date_updated']
        writer = csv.DictWriter(backupfile, fieldnames=fieldnames)
        inventory = Product.select()
        writer.writeheader()
        for item in inventory:
            writer.writerow({
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_quantity': item.product_quantity,
                'product_price': (item.product_price *.01),
                'date_updated': item.date_updated
            })
    print("Your Inventory was saved sucsefully!")
    print("\nPress q to return to main menu")
    next_action = input('Action: [q] ').lower().strip()
    while True:
        if next_action =='q':
            break
        else:
            next_action = input("Please press 'q' to return to main menu ").lower().strip()

menu = OrderedDict([
    ('v', view_product),
    ('a', add_product),
    ('b', backup_inventory)
])
if __name__ == "__main__":
    db.connect()
    db.create_tables([Product], safe=True)
    read_inventory()
    menu_loop()
