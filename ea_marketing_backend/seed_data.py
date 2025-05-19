# ea_marketing_backend/seed_data.py
import os
import django
from decimal import Decimal
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ea_marketing_backend.settings')
django.setup()

from django.contrib.auth.models import User
from financial_manager.models import UserProfile, CompanyEarning, CompanyExpense, Budget, Investment, Transaction

# Create a user and profile
user, _ = User.objects.get_or_create(username='admin', defaults={'password': 'admin123'})
if not user.has_usable_password():
    user.set_password('admin123')
    user.save()

if not hasattr(user, 'userprofile'):
    UserProfile.objects.create(
        user=user,
        name='John Doe',
        email='john.doe@example.com',
        phone='+1 234 567 8900',
        address='1234 Elm Street, Springfield, IL 62704',
        date_of_birth=datetime.strptime('1990-05-15', '%Y-%m-%d').date(),
        language='English',
        theme='Light'
    )

# Seed Company Earnings
company_earnings = [
    {'project': 'Website Redesign', 'amount': 25000, 'date': '2025-04-10'},
    {'project': 'SEO Campaign', 'amount': 18000, 'date': '2025-03-15'},
    {'project': 'Social Media Marketing', 'amount': 12000, 'date': '2025-02-20'},
    {'project': 'E-commerce Development', 'amount': 30000, 'date': '2025-01-10'},
]
for earning in company_earnings:
    CompanyEarning.objects.get_or_create(
        user=user,
        project=earning['project'],
        amount=Decimal(earning['amount']),
        date=datetime.strptime(earning['date'], '%Y-%m-%d').date()
    )

# Seed Company Expenses
company_expenses = [
    {'category': 'Salaries', 'amount': 30000, 'date': '2025-04-01'},
    {'category': 'Office Rent', 'amount': 5000, 'date': '2025-04-05'},
    {'category': 'Utilities', 'amount': 2000, 'date': '2025-04-10'},
    {'category': 'Marketing Tools', 'amount': 4000, 'date': '2025-03-20'},
    {'category': 'Travel', 'amount': 1500, 'date': '2025-03-25'},
]
for expense in company_expenses:
    CompanyExpense.objects.get_or_create(
        user=user,
        category=expense['category'],
        amount=Decimal(expense['amount']),
        date=datetime.strptime(expense['date'], '%Y-%m-%d').date()
    )

# Seed Budgets
budgets = [
    {'category': 'Marketing', 'allocated': 10000, 'spent': 8500},
    {'category': 'Development', 'allocated': 15000, 'spent': 17000},
    {'category': 'Operations', 'allocated': 8000, 'spent': 6000},
    {'category': 'Research', 'allocated': 5000, 'spent': 5200},
]
for budget in budgets:
    Budget.objects.get_or_create(
        user=user,
        category=budget['category'],
        allocated=Decimal(budget['allocated']),
        spent=Decimal(budget['spent'])
    )

# Seed Investments
investments = [
    {'type': 'Stocks', 'amount': 5000},
    {'type': 'Bonds', 'amount': 3000},
    {'type': 'Real Estate', 'amount': 4000},
    {'type': 'Crypto', 'amount': 2500},
]
for inv in investments:
    Investment.objects.get_or_create(
        user=user,
        type=inv['type'],
        amount=Decimal(inv['amount'])
    )

# Seed Transactions
transactions = [
    {'date': '2025-04-15', 'description': 'Client Payment', 'category': 'Income', 'amount': 5000, 'type': 'Income'},
    {'date': '2025-04-14', 'description': 'Office Supplies', 'category': 'Office', 'amount': -250, 'type': 'Expense'},
    {'date': '2025-04-13', 'description': 'Freelancer Payment', 'category': 'Freelance', 'amount': -800, 'type': 'Expense'},
    {'date': '2025-04-12', 'description': 'Ad Revenue', 'category': 'Income', 'amount': 1200, 'type': 'Income'},
    {'date': '2025-04-11', 'description': 'Software Subscription', 'category': 'Software', 'amount': -150, 'type': 'Expense'},
]
for txn in transactions:
    Transaction.objects.get_or_create(
        user=user,
        date=datetime.strptime(txn['date'], '%Y-%m-%d').date(),
        description=txn['description'],
        category=txn['category'],
        amount=Decimal(txn['amount']),
        type=txn['type']
    )

print("Data seeded successfully!")