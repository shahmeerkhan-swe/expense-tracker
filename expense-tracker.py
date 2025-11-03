import argparse 
import json
from datetime import datetime
from tabulate import tabulate
import calendar
import csv
import pandas as pd 

def read_json_file(filetype: str): # read the current expenses file
    try: 
        if filetype == "expense":
            with open("data/expenses.json", "r") as file: 
                output_list = json.load(file)
        elif filetype == "budget":
            with open("data/budgets.json", "r") as file: 
                output_list = json.load(file)
    except FileNotFoundError:
        if filetype == "expense":
            output_list = []
            with open("data/expenses.json", "w") as file:
                json.dump(output_list, file, indent=2)
        elif filetype == "budget": 
            output_list = []
            with open("data/budgets.json", "w") as file: 
                json.dump(output_list, file, indent=2)
    return output_list


def save_to_json(data, target):
    if target == "expenses":
        with open("data/expenses.json", "w") as file: 
            json.dump(data, file, indent=2)
    elif target == "budgets":
        with open("data/budgets.json", "w") as file: 
            json.dump(data, file, indent=2)

def export_csv(inputFile):
    try: 
        with open(f"{inputFile}.json", "r") as file: 
            data = pd.read_json(file)

        data.to_csv(f'{inputFile}.csv', index=False)
        print(f"{inputFile}.csv has been created!")
    except FileNotFoundError:
        print(f"{inputFile}.json does not exist.")

def generate_next_id(expenses):
    try: 
        max_id = max(expense["id"] for expense in expenses)
    except ValueError:
        max_id = 0
    return max_id + 1

parser = argparse.ArgumentParser(prog="Expense Tracker CLI", description="A command line based tracker")
subparser = parser.add_subparsers(dest="command")

# Add expense
add_expense = subparser.add_parser("add", help="Add an expense")
add_expense.add_argument("--description", type=str, required=True, help="Expense description")
add_expense.add_argument("--amount", type=float, required=True, help="Expense amount")
add_expense.add_argument("--category", type=str, default="uncategorized", help="Expense category")

# Update expense
update_expense = subparser.add_parser("update", help="Update an expense")
update_expense.add_argument("--id", type=int, required=True, help="Provide expense id")
update_expense.add_argument("--amount", type=float, required=True, help="Provide new amount")
update_expense.add_argument("--category", type=str, help="Provide a category")

# Delete expense
delete_expense = subparser.add_parser("delete", help="Delete an expense")
delete_expense.add_argument("--id", type=int, required=True, help="Provide expense id")

# View summary
expense_summary = subparser.add_parser("summary", help="View summary of expenses")
expense_summary.add_argument("--month", type=int, choices=range(1, 13), help="Provide month of year as an integer")
expense_summary.add_argument("--category", type=str, help="Provide a category")

# List expenses
list_expense = subparser.add_parser("list", help="List expenses")
list_expense.add_argument("--category", type=str, help="Filter expenses by category")

# Set budget 
set_budget = subparser.add_parser("set-budget", help="Set a budget for a particular month")
set_budget.add_argument("--month", type=int, required=True, choices=range(1, 13), help="Provide a month for the budget")
set_budget.add_argument("--amount", type=float, required=True, help="Provide a budget amount")
set_budget.add_argument("--year", type=int, required=True, help="Provide a year")

# Check budget
check_budget = subparser.add_parser("check-budget", help="Check the budget for a particular month")
check_budget.add_argument("--month", type=int, required=True, choices=range(1, 13))
check_budget.add_argument("--year", required=True, type=int, help="Enter the year for budget")

# Export to CSV
export_file = subparser.add_parser("export", help="Export your expenses/budgets to CSV")
export_file.add_argument("--filename", required=True, type=str, help="Enter the filename (expenses/budgets)")

args = parser.parse_args()

# Add command logic
if args.command == "add":
    expenses = read_json_file("expense")
    new_id = generate_next_id(expenses)
    if args.amount <= 0.0: 
        print("Amount cannot be 0 or negative.")
    else:  
        new_expense = {"id": new_id, "date": datetime.utcnow().strftime("%Y-%m-%d"), "description": args.description, "amount": args.amount, "category": args.category}
        expenses.append(new_expense)
        save_to_json(expenses, "expenses")
        print(f"Expense successfully added (ID: {new_id})")

# Update command logic
if args.command == "update":
    expenses = read_json_file("expense")
    found = False
    for expense in expenses:
        if expense["id"] == args.id:
            if args.amount <= 0.0:
                print("Amount cannot be 0 or a negative.")
            else:
                expense["amount"] = args.amount 
                if args.category:
                    expense["category"] = args.category.lower().strip()
                found = True
    if found: 
        save_to_json(expenses, "expenses")
        print(f"Expense updated (ID: {expense["id"]})")
    else:
        print(f"Could not find expense with ID: {args.id}")

# Delete command logic
if args.command == "delete":
    expenses = read_json_file("expense")
    found = False
    for expense in expenses: 
        if expense["id"] == args.id:
            expenses.remove(expense)
            found = True
        
    if found:
        save_to_json(expenses, "expenses")
        print("Expense deleted successfully")
    else: 
        print(f"Expense with ID: {args.id} could not be found.")

# List command logic
if args.command == "list":
    expenses = read_json_file("expense")
    if args.category: 
        filtered_expenses = []
        for expense in expenses:
            try: 
                if expense["category"] == args.category.lower().strip():
                    filtered_expenses.append(expense)
            except KeyError:
                expense["category"] = "uncategorized"
                continue 
        print(tabulate(filtered_expenses, headers="keys"))
        save_to_json(expenses, "expenses")
    else: 
        print(tabulate(expenses, headers="keys"))
        

# Summary command logic
if args.command == "summary":
    expenses = read_json_file("expense")
    total_all = sum(expense["amount"] for expense in expenses)
    filtered_expenses = []

    if args.month and args.category:
        category = args.category.lower().strip()
        month_name = calendar.month_name[args.month]
        for expense in expenses:
            date = datetime.strptime(expense["date"], "%Y-%m-%d")
            if args.month == date.month and expense["category"] == category:
                filtered_expenses.append(expense)
            
        total = sum(expense["amount"] for expense in filtered_expenses)
        print(f"Total expenses for {month_name} and in {category}: ${total}")
    elif args.month: 
        for expense in expenses: 
            date = datetime.strptime(expense["date"], "%Y-%m-%d")
            if args.month == date.month: 
                filtered_expenses.append(expense)

        total = sum(expense["amount"] for expense in filtered_expenses)
        month_name = calendar.month_name[args.month]
        print(f"Total expenses for {month_name}: ${total}")
    elif args.category:
        category = args.category.lower().strip()
        for expense in expenses: 
            if expense["category"] == category:
                filtered_expenses.append(expense)
        total = sum(e["amount"] for e in filtered_expenses)
        print(f"Total expenses for {category}: ${total}")
    else: 
        print(f"Total expenses: ${total_all}")

# Set budget logic
if args.command == "set-budget":
    budgets = read_json_file("budget")
    amount = args.amount
    month_name = calendar.month_name[args.month]
    date_string = f"{args.year}-{args.month:02d}"
    budget = {"date": date_string, "amount": amount}
    budgets.append(budget)
    save_to_json(budgets, "budgets")
    print(f"Budget set for {month_name} --> ${amount}")

if args.command == "check-budget": 
    budgets = read_json_file("budget")
    expenses = read_json_file("expense")
    month_name = calendar.month_name[args.month]
    date_string = f"{args.year}-{args.month:02d}"
    budget_amount = 0
    month_amount = 0
    
    for budget in budgets: 
        if budget["date"] == date_string: 
            budget_amount = budget["amount"]
        else: 
            continue 

    for expense in expenses: 
        date = datetime.strptime(expense["date"], "%Y-%m-%d")
        if args.month == date.month and args.year == date.year: 
            month_amount += expense["amount"]
        else: 
            continue

    if month_amount > budget_amount:
        print(f"Budget for {month_name} exceeded!")
    else:
        remaining = budget_amount - month_amount
        print(f"Total budget remaining for {month_name}: {remaining}")

if args.command == "export":
    filename = args.filename.lower().strip()
    export_csv(filename)



