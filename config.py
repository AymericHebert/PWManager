import sys
import string
import random
import hashlib
import os
import argparse 
from getpass import getpass

from rich import print as printc
from rich.console import Console 
from dotenv import dotenv_values

from test import DBManager



# parser = argparse.ArgumentParser()
# parser.add_argument('option', help='make / delete / remake')
# args = parser.parse_args()

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
config = dotenv_values('.env')
print(config)

config = {
     **config,
     'raise_on_warnings' : True
}

console = Console()
db = DBManager(db_name='pwm', config=config)


def generate_device_secret(length=10) -> str:
    """ Generate a random device secret. """
    device_secret = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return device_secret


def make() -> None:
    ''' Create 'pwm' database if it doesn't exist. '''

    if db.db_exists():
        printc("[red][!] Already Configured!")
        return

    printc("[green][+] Creating new config")


    # Create database
    db = dbmanager.connect()
    cursor = db.cursor()

    try:
        cursor.execute("CREATE DATABASE pwm;")
    except Exception as error:
        console.print_exception()
        printc("[red][!] An error occurred while trying to create db. Check if database with name 'pwm' already exists - if it does, delete it and try again.")
        sys.exit(0)

    printc("[green][+][/green] Database 'pwm' created!")


    # Create tables
    queries = (
        """
            CREATE TABLE pwm.secrets (
                masterkey_hash TEXT NOT NULL, 
                device_secret TEXT NOT NULL
            );
        """,
        """
            CREATE TABLE pwm.entries (
                password_id SERIAL PRIMARY KEY,
                application_name TEXT NOT NULL,
                url TEXT,
                email TEXT,
                username TEXT,
                password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
    )

    for query in queries:
        cursor.execute(query)

    printc("[green][+][/green] Tables created.")

    master_password = ""
    printc("[green][+] A [bold]MASTER PASSWORD[/bold] is the only password you will need to remember in-order to access all your other passwords. Choosing a strong [bold]MASTER PASSWORD[/bold] is essential because all your other passwords will be [bold]encrypted[/bold] with a key that is derived from your [bold]MASTER PASSWORD[/bold]. Therefore, please choose a strong one that has upper and lower case characters, numbers and also special characters. Remember your [bold]MASTER PASSWORD[/bold] because it won't be stored anywhere by this program, and you also cannot change it once chosen.\n")

    while 1:
        master_password = getpass("Choose a MASTER PASSWORD: ")
        if master_password == getpass("Re-type: ") and master_password != "":
            break
        printc("[yellow][-] Please try again.")

    # Hash the MASTER PASSWORD
    hashed_master_password = hashlib.sha256(master_password.encode()).hexdigest()
    printc("[green][+][/green] Generated hash of MASTER PASSWORD.")


    # Generate a device secret
    device_secret = generate_device_secret()
    printc("[green][+][/green] Device Secret generated.")

    # Add them to db
    query = """
        INSERT INTO pwm.secrets (
            masterkey_hash, 
            device_secret) 
            values (%s, %s) 
        """
    cursor.execute(query, (hashed_master_password, device_secret))
    db.commit()

    printc("[green][+][/green] Added to the database.")

    printc("[green][+] Configuration done!")

    db.close()


def delete() -> None:
    ''' Delete the 'pwm' database if it exists. '''
    
    printc("[red][-] Deleting a config clears the device secret and all your entries from the database. This means you will loose access to all your passwords that you have added into the password manager until now. Only do this if you truly want to 'destroy' all your entries. This action cannot be undone.")

    while 1:
        user_input = input("So are you sure you want to continue? (y/N): ")
        if user_input.upper() == "Y":
            break
        if user_input.upper() == "N" or user_input.upper == "":
            printc('Aborted.')
            sys.exit(0)
        else:
            continue

    printc("[green][-][/green] Deleting config")


    if not db_exists():
        printc("[yellow][-][/yellow] No configuration exists to delete!")
        return

    db = dbmanager.connect()
    cursor = db.cursor()
    query = "DROP DATABASE pwm"
    cursor.execute(query)
    db.commit()
    db.close()
    printc("[green][+] Config deleted!")


def remake() -> None:
    ''' Delete the current database and create a new one. '''

    printc("[green][+][/green] Remaking config")
    delete()
    make()


if __name__ == "__main__":

    make()
	# if args.option == "make":
	# 	make()
	# elif args.option == "delete":
	# 	delete()
	# elif args.option == "remake":
	# 	remake()
	# else:
	# 	print("Usage: python config.py <make/delete/remake>")


