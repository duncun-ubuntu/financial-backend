import os
import django
from decimal import Decimal
from datetime import datetime, date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ea_marketing_backend.settings')
django.setup()

from django.contrib.auth.models import User
from financial_manager.models import UserProfile, CompanyEarning, CompanyExpense, Budget, Investment, Transaction, CompanyDocument, Invoice

# Create a user and profile
user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'password': 'pbkdf2_sha256$1000000$FYvKkMhltUkTz2d6AAj80v$eNa67iQ8XzKGVERJRDEs6cwJW267+LV+TF0RoXFwsPM=',
        'is_active': True,
        'date_joined': datetime.strptime('2025-05-06 08:39:58.770041', '%Y-%m-%d %H:%M:%S.%f')
    }
)
if not user.has_usable_password():
    user.set_password('admin123')  # Fallback for local testing
    user.save()

if not hasattr(user, 'userprofile'):
    UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'name': 'eee',
            'email': 'john.doe@example.com',
            'phone': '+1 234 567 8900',
            'address': '1234 Elm Street, Springfield, IL 62704',
            'date_of_birth': datetime.strptime('1990-05-15', '%Y-%m-%d').date(),
            'account_created': datetime.strptime('2025-05-06', '%Y-%m-%d').date(),
            'language': 'English',
            'theme': 'Light',
            'profile_picture': 'https://via.placeholder.com/150'
        }
    )

# Seed Budgets (must be created before expenses due to foreign key)
budgets = [
    {'category': 'Marketing', 'allocated': 50000000.00, 'spent': 42500.00},  # Adjusted to cover expenses
    {'category': 'Development', 'allocated': 20000000.00, 'spent': 17000.00},  # Adjusted to cover potential expenses
    {'category': 'Operations', 'allocated': 8000000.00, 'spent': 6000.00},
    {'category': 'Research', 'allocated': 7000000.00, 'spent': 5200.00},
    {'category': 'mradi sunbeam', 'allocated': 30000000.00, 'spent': 14000.00},
    {'category': 'water bills', 'allocated': 40000000.00, 'spent': 28000.00},
    {'category': 'Test Budget', 'allocated': 1000000.00, 'spent': 200.00},
]
budget_map = {}  # To store category-to-budget mapping for expenses
for budget in budgets:
    obj, _ = Budget.objects.get_or_create(
        user=user,
        category=budget['category'],
        defaults={
            'allocated': Decimal(budget['allocated']),
            'spent': Decimal(budget['spent'])
        }
    )
    budget_map[budget['category']] = obj

# Seed Company Earnings
company_earnings = [
    {'project': 'Website Redesign', 'amount': 25000.00, 'date': '2025-04-10'},
    {'project': 'SEO Campaign', 'amount': 18000.00, 'date': '2025-03-15'},
    {'project': 'Social Media Marketing', 'amount': 12000.00, 'date': '2025-02-20'},
    {'project': 'E-commerce Development', 'amount': 30000.00, 'date': '2025-01-10'},
    {'project': 'Test Income', 'amount': 500.00, 'date': '2025-05-07'},
    {'project': 'utwanaa', 'amount': 4000.00, 'date': '2025-06-07'},
    {'project': 'water bills', 'amount': 30000.00, 'date': '2025-05-21'},
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
    {'category': 'Salaries', 'amount': 30000.00, 'date': '2025-04-01', 'budget_category': 'Marketing'},
    {'category': 'Office Rent', 'amount': 5000.00, 'date': '2025-04-05', 'budget_category': 'Marketing'},
    {'category': 'Utilities', 'amount': 2000.00, 'date': '2025-04-10', 'budget_category': 'Marketing'},
    {'category': 'Marketing Tools', 'amount': 4000.00, 'date': '2025-03-20', 'budget_category': 'Marketing'},
    {'category': 'Travel', 'amount': 1500.00, 'date': '2025-03-25', 'budget_category': 'Marketing'},
    {'category': 'water bills', 'amount': 5000.00, 'date': '2025-05-06', 'budget_category': 'Marketing'},
    {'category': 'electricity bill', 'amount': 15000.00, 'date': '2025-05-05', 'budget_category': 'Marketing'},
    {'category': 'systems', 'amount': 3000.00, 'date': '2025-05-07', 'budget_category': 'mradi sunbeam'},
    {'category': 'mab', 'amount': 2000.00, 'date': '2025-05-07', 'budget_category': 'mradi sunbeam'},
    {'category': 'mradi sunbeam', 'amount': 2000.00, 'date': '2025-05-07', 'budget_category': 'mradi sunbeam'},
    {'category': 'yuuu', 'amount': 3000.00, 'date': '2025-05-07', 'budget_category': 'mradi sunbeam'},
    {'category': 'water bills', 'amount': 20000.00, 'date': '2025-05-07', 'budget_category': 'water bills'},
    {'category': 'water billsttt', 'amount': 6000.00, 'date': '2025-05-09', 'budget_category': 'water bills'},
    {'category': 'water bills', 'amount': 1000.00, 'date': '2025-05-23', 'budget_category': 'water bills'},
    {'category': 'Test Expense', 'amount': 200.00, 'date': '2025-05-07', 'budget_category': 'Test Budget'},
    {'category': 'utwana', 'amount': 1000.00, 'date': '2025-05-30', 'budget_category': 'water bills'},
    {'category': 'water bills', 'amount': 2000.00, 'date': '2025-05-08', 'budget_category': 'mradi sunbeam'},
    {'category': 'suuy', 'amount': 2000.00, 'date': '2025-05-13', 'budget_category': 'mradi sunbeam'},
]
for expense in company_expenses:
    budget = budget_map.get(expense['budget_category'])
    if budget:
        CompanyExpense.objects.get_or_create(
            user=user,
            category=expense['category'],
            amount=Decimal(expense['amount']),
            date=datetime.strptime(expense['date'], '%Y-%m-%d').date(),
            budget=budget
        )

# Seed Investments
investments = [
    {'type': 'Stocks', 'amount': 5000.00},
    {'type': 'Bonds', 'amount': 3000.00},
    {'type': 'Real Estate', 'amount': 4000.00},
    {'type': 'Crypto', 'amount': 2500.00},
    {'type': 'transportation', 'amount': 5000.00},
    {'type': 'transportation', 'amount': 30000.00},
]
for inv in investments:
    Investment.objects.get_or_create(
        user=user,
        type=inv['type'],
        amount=Decimal(inv['amount'])
    )

# Seed Transactions
transactions = [
    {'date': '2025-04-15', 'description': 'Client Payment', 'category': 'Income', 'amount': 5000.00, 'type': 'Income'},
    {'date': '2025-04-14', 'description': 'Office Supplies', 'category': 'Office', 'amount': -250.00, 'type': 'Expense'},
    {'date': '2025-04-13', 'description': 'Freelancer Payment', 'category': 'Freelance', 'amount': -800.00, 'type': 'Expense'},
    {'date': '2025-04-12', 'description': 'Ad Revenue', 'category': 'Income', 'amount': 1200.00, 'type': 'Income'},
    {'date': '2025-04-11', 'description': 'Software Subscription', 'category': 'Software', 'amount': -150.00, 'type': 'Expense'},
    {'date': '2025-05-05', 'description': 'fuel', 'category': 'car fuels', 'amount': 5000.00, 'type': 'Expense'},
    {'date': '2025-05-07', 'description': 'wia people wazururaji', 'category': 'wia project', 'amount': 8000.00, 'type': 'Expense'},
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

# Seed Company Documents
company_documents = [
    {
        'title': 'yaas',
        'file': 'documents/1/weekly_report_pdf_1_eNcf7Qq.pdf',
        'file_type': 'pdf',
        'uploaded_at': datetime.strptime('2025-05-08 06:28:30.087872', '%Y-%m-%d %H:%M:%S.%f')
    },
    {
        'title': 'testing word',
        'file': 'documents/1/Document1_O9QTS7D.docx',
        'file_type': 'docx',
        'uploaded_at': datetime.strptime('2025-05-08 06:50:22.889222', '%Y-%m-%d %H:%M:%S.%f')
    },
    {
        'title': 'dinye records for wia project',
        'file': 'documents/1/weekly_report_pdf_1_HWrE86S.pdf',
        'file_type': 'pdf',
        'uploaded_at': datetime.strptime('2025-05-08 08:51:15.886292', '%Y-%m-%d %H:%M:%S.%f')
    },
]
for doc in company_documents:
    CompanyDocument.objects.get_or_create(
        user=user,
        title=doc['title'],
        file=doc['file'],
        file_type=doc['file_type'],
        uploaded_at=doc['uploaded_at']
    )

# Seed Invoices
invoices = [
    {
        'invoice_number': 'INV-3A9B5C4C',
        'client_name': 'bd',
        'client_email': 'rrr@gmail.com',
        'date': '2025-05-09',
        'items': [
            {"quantity": 4, "unit_price": 2000, "description": "sok"},
            {"quantity": 3, "unit_price": 1000, "description": "miwan"}
        ],
        'total_amount': 12105.5,
        'client_location': 'dffb',
        'client_tin': '34253',
        'include_days': False,
        'vat_rate': 10.0,
        'client_address': 'dfdfb',
        'heading': 'Tax Invoice',
        'subtitle': 'rr',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-09 10:51:49.789862', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': None
    },
    {
        'invoice_number': 'INV-03E11ED5',
        'client_name': 'malima',
        'client_email': 'haa@gmail.co.tz',
        'date': '2025-05-09',
        'items': [
            {"quantity": 2, "unit_price": 4000, "description": "yaas"},
            {"quantity": 3, "unit_price": 2000, "description": "mix"}
        ],
        'total_amount': 14000.0,
        'client_location': 'daresalaam',
        'client_tin': '7324563',
        'include_days': False,
        'vat_rate': 0.0,
        'client_address': 'p.o.b 223344',
        'heading': 'Performance Invoice',
        'subtitle': 'april car',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-09 11:01:03.890257', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': None
    },
    {
        'invoice_number': 'BD.2025.002',
        'client_name': 'bd',
        'client_email': 'rrr@gmail.com',
        'date': '2025-05-09',
        'items': [
            {"quantity": 2, "unit_price": 2000, "description": "wee"}
        ],
        'total_amount': 4000.0,
        'client_location': 'dffb',
        'client_tin': '34253',
        'include_days': False,
        'vat_rate': 0.0,
        'client_address': 'dfdfb',
        'heading': 'Tax Invoice',
        'subtitle': 'yuuu',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-09 11:50:13.254677', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': None
    },
    {
        'invoice_number': 'MAL.2025.002',
        'client_name': 'malima',
        'client_email': 'haa@gmail.co.tz',
        'date': '2025-05-09',
        'items': [
            {"quantity": 2, "unit_price": 1000, "description": "YEES"},
            {"quantity": 4, "unit_price": 200, "description": "NOO"},
            {"quantity": 6, "unit_price": 3700, "description": "WEE"},
            {"quantity": 4, "unit_price": 2300, "description": "REES"}
        ],
        'total_amount': 35920.5,
        'client_location': 'daresalaam',
        'client_tin': '7324563',
        'include_days': False,
        'vat_rate': 5.0,
        'client_address': 'p.o.b 223344',
        'heading': 'Tax Invoice',
        'subtitle': 'YEES',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-09 12:15:06.167112', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': None
    },
    {
        'invoice_number': 'MAL.2025.003',
        'client_name': 'malima',
        'client_email': 'haa@gmail.co.tz',
        'date': '2025-05-09',
        'items': [
            {"quantity": 1, "unit_price": 1000, "description": "WEE"}
        ],
        'total_amount': 1052.1,
        'client_location': 'daresalaam',
        'client_tin': '7324563',
        'include_days': False,
        'vat_rate': 5.0,
        'client_address': 'p.o.b 223344',
        'heading': 'Performance Invoice',
        'subtitle': 'TT',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-09 12:22:12.723152', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': None
    },
    {
        'invoice_number': 'MAL.2025.004',
        'client_name': 'malima',
        'client_email': 'haa@gmail.co.tz',
        'date': '2025-05-09',
        'items': [
            {"quantity": 2, "unit_price": 1000, "description": "rrr"}
        ],
        'total_amount': 2106.3,
        'client_location': 'daresalaam',
        'client_tin': '7324563',
        'include_days': False,
        'vat_rate': 5.0,
        'client_address': 'p.o.b 223344',
        'heading': 'Tax Invoice',
        'subtitle': 'dddd',
        'agent_fee': 6.0,
        'include_agent_fee': True,
        'created_at': datetime.strptime('2025-05-09 12:34:58.052982', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': None
    },
    {
        'invoice_number': 'MAL.2025.005',
        'client_name': 'malima',
        'client_email': 'haa@gmail.co.tz',
        'date': '2025-05-09',
        'items': [
            {"quantity": 3, "unit_price": 2000, "description": "weeee"},
            {"quantity": 4, "unit_price": 3000, "description": "wrrr"},
            {"quantity": 5, "unit_price": 2500, "description": "dee"},
            {"quantity": 3, "unit_price": 4000, "description": "faa"}
        ],
        'total_amount': 44635.5,
        'client_location': 'daresalaam',
        'client_tin': '7324563',
        'include_days': False,
        'vat_rate': 5.0,
        'client_address': 'p.o.b 223344',
        'heading': 'Tax Invoice',
        'subtitle': 'hh',
        'agent_fee': 10.0,
        'include_agent_fee': True,
        'created_at': datetime.strptime('2025-05-09 12:39:07.726906', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': None
    },
    {
        'invoice_number': 'BD.2025.003',
        'client_name': 'bd',
        'client_email': 'rrr@gmail.com',
        'date': '2025-05-12',
        'items': [
            {"quantity": 2, "unit_price": 2000, "description": "eeee"}
        ],
        'total_amount': 4000.0,
        'client_location': 'dffb',
        'client_tin': '34253',
        'include_days': False,
        'vat_rate': 0.0,
        'client_address': 'dfdfb',
        'heading': 'Tax Invoice',
        'subtitle': 'jjjjjjjj',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-12 10:08:27.052971', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': 'siza'
    },
    {
        'invoice_number': 'MAL.2025.006',
        'client_name': 'malima',
        'client_email': 'haa@gmail.co.tz',
        'date': '2025-05-12',
        'items': [
            {"quantity": 3, "unit_price": 2000, "description": "eee"}
        ],
        'total_amount': 6000.0,
        'client_location': 'daresalaam',
        'client_tin': '7324563',
        'include_days': False,
        'vat_rate': 0.0,
        'client_address': 'p.o.b 223344',
        'heading': 'Performance Invoice',
        'subtitle': 'yyyy',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-12 11:40:16.723051', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': 'elisha'
    },
    {
        'invoice_number': 'MAL.2025.007',
        'client_name': 'malima',
        'client_email': 'haa@gmail.co.tz',
        'date': '2025-05-12',
        'items': [
            {"quantity": 5, "unit_price": 2500, "description": "weee"}
        ],
        'total_amount': 12500.0,
        'client_location': 'daresalaam',
        'client_tin': '7324563',
        'include_days': False,
        'vat_rate': 0.0,
        'client_address': 'p.o.b 223344',
        'heading': 'Purchase Order',
        'subtitle': 'iiiiibbbb',
        'agent_fee': 0.0,
        'include_agent_fee': False,
        'created_at': datetime.strptime('2025-05-12 11:41:19.324580', '%Y-%m-%d %H:%M:%S.%f'),
        'signature_choice': 'ginye'
    },
]
for inv in invoices:
    Invoice.objects.get_or_create(
        user=user,
        invoice_number=inv['invoice_number'],
        defaults={
            'client_name': inv['client_name'],
            'client_email': inv['client_email'],
            'date': datetime.strptime(inv['date'], '%Y-%m-%d').date(),
            'items': inv['items'],  # Django ORM handles JSONB conversion
            'total_amount': inv['total_amount'],
            'client_location': inv['client_location'],
            'client_tin': inv['client_tin'],
            'include_days': inv['include_days'],
            'vat_rate': inv['vat_rate'],
            'client_address': inv['client_address'],
            'heading': inv['heading'],
            'subtitle': inv['subtitle'],
            'agent_fee': inv['agent_fee'],
            'include_agent_fee': inv['include_agent_fee'],
            'created_at': inv['created_at'],
            'signature_choice': inv['signature_choice']
        }
    )

print("Data seeded successfully!")