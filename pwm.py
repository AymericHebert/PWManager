import argparse

from rich import print as printc
from rich.console import Console
from rich.table import Table

import arch.dbmanager as db




parser = argparse.ArgumentParser()
parser.add_argument('option', help='insert / get / generate')
parser.add_argument("-a", '--app', help='Application name')
parser.add_argument('--url', help='Url')
parser.add_argument("-u", '--user', help='Username / email')
parser.add_argument("-p", '--pwd', help='Password')
args = parser.parse_args()

console = Console()


def draw_table(rows):
    columns_names = db.get_column_names()
    
    table = Table(title='DB Entries')

    for column_name in columns_names:
        table.add_column(column_name, justify = 'left', no_wrap=True) 

    for row in rows:
        table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), "{hidden}", str(row[5]), str(row[6]))

    console.print(table)


def main():
    if args.option in ('insert', 'i'):
        if args.app == None:
            printc("[red][!][/red] Application name (-a) required")
            return


if __name__ == '__main__':
    main()