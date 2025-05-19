# financial_manager/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from .models import UserProfile, CompanyEarning, CompanyExpense, Budget, Investment, Transaction
from .serializers import (
    UserProfileSerializer, CompanyEarningSerializer, CompanyExpenseSerializer,
    BudgetSerializer, InvestmentSerializer, TransactionSerializer
)
import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import matplotlib.pyplot as plt
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Debug print to confirm view is loaded
print("Loading financial_manager views.py")

# User Profile CRUD
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

# Company Earnings CRUD
class CompanyEarningListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        earnings = CompanyEarning.objects.filter(user=request.user)
        serializer = CompanyEarningSerializer(earnings, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CompanyEarningSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyEarningDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return CompanyEarning.objects.get(pk=pk, user=user)
        except CompanyEarning.DoesNotExist:
            return None

    def get(self, request, pk):
        earning = self.get_object(pk, request.user)
        if not earning:
            return Response({"error": "Earning not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyEarningSerializer(earning)
        return Response(serializer.data)

    def put(self, request, pk):
        earning = self.get_object(pk, request.user)
        if not earning:
            return Response({"error": "Earning not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyEarningSerializer(earning, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        earning = self.get_object(pk, request.user)
        if not earning:
            return Response({"error": "Earning not found"}, status=status.HTTP_404_NOT_FOUND)
        earning.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Company Expenses CRUD
class CompanyExpenseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = CompanyExpense.objects.filter(user=request.user)
        serializer = CompanyExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CompanyExpenseSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return CompanyExpense.objects.get(pk=pk, user=user)
        except CompanyExpense.DoesNotExist:
            return None

    def get(self, request, pk):
        expense = self.get_object(pk, request.user)
        if not expense:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyExpenseSerializer(expense)
        return Response(serializer.data)

    def put(self, request, pk):
        expense = self.get_object(pk, request.user)
        if not expense:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(pk, request.user)
        if not expense:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        budget = expense.budget
        expense.delete()
        # Update budget spent amount after deletion
        budget.spent = sum(float(exp.amount) for exp in budget.expenses.all())
        budget.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Budgets CRUD
class BudgetListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        budgets = Budget.objects.filter(user=request.user)
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = BudgetSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BudgetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Budget.objects.get(pk=pk, user=user)
        except Budget.DoesNotExist:
            return None

    def get(self, request, pk):
        budget = self.get_object(pk, request.user)
        if not budget:
            return Response({"error": "Budget not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BudgetSerializer(budget)
        return Response(serializer.data)

    def put(self, request, pk):
        budget = self.get_object(pk, request.user)
        if not budget:
            return Response({"error": "Budget not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        budget = self.get_object(pk, request.user)
        if not budget:
            return Response({"error": "Budget not found"}, status=status.HTTP_404_NOT_FOUND)
        budget.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Investments CRUD
class InvestmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        investments = Investment.objects.filter(user=request.user)
        serializer = InvestmentSerializer(investments, many=True)
        total = sum(float(inv.amount) for inv in investments)
        return Response({
            'total': total,
            'breakdown': serializer.data
        })

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = InvestmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Investment.objects.get(pk=pk, user=user)
        except Investment.DoesNotExist:
            return None

    def get(self, request, pk):
        investment = self.get_object(pk, request.user)
        if not investment:
            return Response({"error": "Investment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InvestmentSerializer(investment)
        return Response(serializer.data)

    def put(self, request, pk):
        investment = self.get_object(pk, request.user)
        if not investment:
            return Response({"error": "Investment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InvestmentSerializer(investment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        investment = self.get_object(pk, request.user)
        if not investment:
            return Response({"error": "Investment not found"}, status=status.HTTP_404_NO_CONTENT)
        investment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Transactions (Aggregated View)
class TransactionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            earnings = CompanyEarning.objects.filter(user=request.user)
            expenses = CompanyExpense.objects.filter(user=request.user)

            # Manually construct transaction list from earnings and expenses
            transactions = []
            for earning in earnings:
                transactions.append({
                    'id': earning.id,
                    'date': earning.date,
                    'description': earning.project,
                    'category': earning.project, # Using project as category for earnings
                    'amount': float(earning.amount),
                    'type': 'Income',
                })
            for expense in expenses:
                transactions.append({
                    'id': expense.id,
                    'date': expense.date,
                    'category': expense.category,
                    'amount': float(expense.amount),
                    'type': 'Expense',
                    'budget_id': expense.budget.id if expense.budget else None,
                })

            transactions.sort(key=lambda x: x['date'], reverse=True)

            balance = sum(t['amount'] for t in transactions if t['type'] == 'Income') - \
                      sum(t['amount'] for t in transactions if t['type'] == 'Expense')

            logger.info(f"Fetched {len(transactions)} transactions for user {request.user.username}")
            return Response({
                'balance': balance,
                'transactions': transactions
            })
        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Failed to fetch transactions: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        return Response(
            {"error": "Use /earnings/ or /expenses/ to create transactions"},
            status=status.HTTP_400_BAD_REQUEST
        )

# Transaction Detail View (Note: This is not currently used in the aggregated transaction list)
class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # This view would typically interact with a single Transaction model,
    # but your TransactionListCreateView aggregates data from Earnings and Expenses.
    # You might need to adjust this view or your model structure
    # if you intend to have a single Transaction model for both income and expenses.
    # For now, it remains as it was in your original code.

    def get_object(self, pk, user):
        # This assumes a 'Transaction' model exists and has a 'user' field.
        # Based on your TransactionListCreateView, you might not have a single Transaction model.
        try:
            return Transaction.objects.get(pk=pk, user=user)
        except Transaction.DoesNotExist:
            return None

    def get(self, request, pk):
        transaction = self.get_object(pk, request.user)
        if not transaction:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    def put(self, request, pk):
        transaction = self.get_object(pk, request.user)
        if not transaction:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        transaction = self.get_object(pk, request.user)
        if not transaction:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FinancialWeeklyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("FinancialWeeklyReportView.get called") # This is the key print statement
        try:
            logger.info(f"FinancialWeeklyReportView get method called for user: {request.user.username}") # Key logger call
            logger.info(f"Request path: {request.path}, Full path: {request.get_full_path()}")

            # --- TEMPORARILY REMOVED REPORT GENERATION CODE ---
            # We are just checking if this method is reached.
            # The original code for fetching data, calculating, and generating reports
            # is commented out or removed below.

            # Return a simple success response immediately
            print("Returning simple success response from FinancialWeeklyReportView")
            return Response({"message": "FinancialWeeklyReportView reached successfully!"}, status=status.HTTP_200_OK)

        except Exception as e:
            # Keep the error logging just in case something unexpected happens
            logger.error(f"Unexpected error in FinancialWeeklyReportView (simplified): {str(e)}", exc_info=True)
            return Response(
                {"error": f"An unexpected error occurred in simplified view: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        
            
                
# financial_manager/views.py

# ... (keep all your imports at the top) ...
import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
# import matplotlib.pyplot as plt # Not strictly needed for this PDF generation
import logging

# Django imports
from django.http import HttpResponse
from django.shortcuts import render # Keep render if you use it elsewhere
from django.views.decorators.csrf import csrf_exempt # Needed for unauthorized POST/PUT/DELETE, but not for GET
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated # Keep this import even if not used in the test view
from django.db.models import Sum # Useful for aggregation

# Model imports
from .models import CompanyEarning, CompanyExpense, Budget
from .serializers import CompanyEarningSerializer, CompanyExpenseSerializer, BudgetSerializer

import datetime
import pandas as pd
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
import logging
from django.http import HttpResponse
from django.db.models import Sum
from .models import CompanyEarning, CompanyExpense, Budget
from xlsxwriter import Workbook

logger = logging.getLogger(__name__)

def temp_weekly_report_test(request):
    print("temp_weekly_report_test view hit!")
    try:
        logger.info(f"temp_weekly_report_test view called")
        logger.info(f"Request path: {request.path}, Full path: {request.get_full_path()}")

        format_param = request.GET.get('format', 'excel').lower()
        logger.debug(f"Format parameter: {format_param}")
        if format_param not in ['excel', 'pdf']:
            return HttpResponse(
                json.dumps({"error": f"Invalid format '{format_param}'. Use 'excel' or 'pdf'."}),
                content_type='application/json',
                status=400
            )

        # Define the 7-day period (today - 7 days to today)
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=7)
        end_of_week = today
        logger.debug(f"Date range for report: {start_of_week} to {end_of_week}")

        # Fetch data (unfiltered for testing; add user filter in production)
        earnings = CompanyEarning.objects.filter(date__range=[start_of_week, end_of_week])
        expenses = CompanyExpense.objects.filter(date__range=[start_of_week, end_of_week])
        budgets = Budget.objects.all()
        logger.info(f"Found {earnings.count()} earnings, {expenses.count()} expenses, and {budgets.count()} budgets for the week (unfiltered by user).")

        total_earnings = sum(float(e.amount) for e in earnings) if earnings.exists() else 0
        total_expenses = sum(float(e.amount) for e in expenses) if expenses.exists() else 0
        profit_loss = total_earnings - total_expenses
        logger.debug(f"Calculated: Total Earnings: {total_earnings}, Total Expenses: {total_expenses}, Profit/Loss: {profit_loss}")

        if not earnings.exists() and not expenses.exists() and not budgets.exists():
            logger.warning("No data available for the weekly report for this week (unfiltered by user).")
            return HttpResponse(
                json.dumps({
                    "message": "No earnings, expenses, or budgets found for this week.",
                    "total_earnings": 0,
                    "total_expenses": 0,
                    "profit_loss": 0,
                    "transactions": [],
                    "budgets": []
                }),
                content_type='application/json',
                status=200
            )

        if format_param == 'excel':
            try:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    # Prepare data for Transactions sheet
                    excel_data = {
                        'Date': [e.date for e in earnings] + [e.date for e in expenses],
                        'Type': ['Earning' for _ in earnings] + ['Expense' for _ in expenses],
                        'Category': [e.project for e in earnings] + [e.category for e in expenses],
                        'Amount': [float(e.amount) for e in earnings] + [float(e.amount) for e in expenses],
                    }
                    budget_data = {
                        'Category': [b.category for b in budgets],
                        'Allocated': [float(b.allocated) for b in budgets],
                        'Spent': [float(b.spent) for b in budgets],
                        'Remaining': [float(b.allocated - b.spent) for b in budgets],
                    }

                    earnings_df = pd.DataFrame(excel_data)
                    budget_df = pd.DataFrame(budget_data)

                    # Write data to Excel
                    earnings_df.to_excel(writer, sheet_name='Transactions', index=False, startrow=5)
                    budget_df.to_excel(writer, sheet_name='Budgets', index=False, startrow=5)

                    workbook = writer.book
                    worksheet_transactions = writer.sheets['Transactions']
                    worksheet_budgets = writer.sheets['Budgets']

                    # Define high-quality formatting
                    header_format = workbook.add_format({
                        'bold': True,
                        'font_color': 'white',
                        'bg_color': '#005B96',  # Professional blue
                        'border': 1,
                        'align': 'center',
                        'valign': 'vcenter',
                        'font_name': 'Calibri',
                        'font_size': 12,
                    })
                    currency_format = workbook.add_format({
                        'num_format': '$#,##0.00',
                        'font_name': 'Calibri',
                        'font_size': 11,
                        'border': 1,
                    })
                    cell_format = workbook.add_format({
                        'font_name': 'Calibri',
                        'font_size': 11,
                        'border': 1,
                    })
                    title_format = workbook.add_format({
                        'bold': True,
                        'font_name': 'Calibri',
                        'font_size': 16,
                        'align': 'center',
                        'font_color': '#003087',
                    })
                    summary_format = workbook.add_format({
                        'bold': True,
                        'font_name': 'Calibri',
                        'font_size': 12,
                        'font_color': '#003087',
                    })

                    # Add title and summary
                    worksheet_transactions.write('A1', f'GINYE NIFFER Weekly Financial Report', title_format)
                    worksheet_transactions.merge_range('A1:D1', f'GINYE NIFFER Weekly Financial Report', title_format)
                    worksheet_transactions.write('A2', f'Period: {start_of_week} to {end_of_week}', summary_format)
                    worksheet_transactions.write('A3', f'Total Earnings: ${total_earnings:,.2f}', summary_format)
                    worksheet_transactions.write('A4', f'Total Expenses: ${total_expenses:,.2f}', summary_format)
                    worksheet_transactions.write('A5', f'Profit/Loss: ${profit_loss:,.2f}', summary_format)

                    worksheet_budgets.write('A1', f'GINYE NIFFER Weekly Budget Overview', title_format)
                    worksheet_budgets.merge_range('A1:D1', f'GINYE NIFFER Weekly Budget Overview', title_format)
                    worksheet_budgets.write('A2', f'Period: {start_of_week} to {end_of_week}', summary_format)

                    # Apply formatting to headers
                    for col, header in enumerate(excel_data.keys()):
                        worksheet_transactions.write(5, col, header, header_format)
                    for col, header in enumerate(budget_data.keys()):
                        worksheet_budgets.write(5, col, header, header_format)

                    # Apply formatting to data cells
                    worksheet_transactions.set_column('A:A', 15, cell_format)  # Date
                    worksheet_transactions.set_column('B:B', 15, cell_format)  # Type
                    worksheet_transactions.set_column('C:C', 25, cell_format)  # Category
                    worksheet_transactions.set_column('D:D', 15, currency_format)  # Amount
                    worksheet_budgets.set_column('A:A', 25, cell_format)  # Category
                    worksheet_budgets.set_column('B:D', 15, currency_format)  # Allocated, Spent, Remaining

                    # Add conditional formatting for negative values
                    worksheet_transactions.conditional_format('D7:D1000', {
                        'type': 'cell',
                        'criteria': '<',
                        'value': 0,
                        'format': workbook.add_format({'font_color': 'red'}),
                    })
                    worksheet_budgets.conditional_format('D7:D1000', {
                        'type': 'cell',
                        'criteria': '<',
                        'value': 0,
                        'format': workbook.add_format({'font_color': 'red'}),
                    })

                excel_buffer.seek(0)
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="weekly_report_{start_of_week}.xlsx"'
                response.write(excel_buffer.read())
                logger.info("Excel report generated successfully (from test view)")
                return response
            except Exception as e:
                logger.error(f"Excel generation failed (from test view): {str(e)}", exc_info=True)
                return HttpResponse(
                    json.dumps({"error": f"Failed to generate Excel report (from test view): {str(e)}"}),
                    content_type='application/json',
                    status=500
                )

        else:  # PDF format
            try:
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
                elements = []
                styles = getSampleStyleSheet()

                # Define custom styles
                styles.add(ParagraphStyle(
                    name='CompanyTitle',
                    fontName='Helvetica-Bold',
                    fontSize=16,
                    textColor=colors.Color(0/255, 91/255, 150/255),  # Professional blue
                    alignment=TA_CENTER,
                    spaceAfter=12,
                ))
                styles.add(ParagraphStyle(
                    name='ReportSubtitle',
                    fontName='Helvetica',
                    fontSize=12,
                    textColor=colors.black,
                    alignment=TA_CENTER,
                    spaceAfter=12,
                ))
                styles.add(ParagraphStyle(
                    name='SectionHeader',
                    fontName='Helvetica-Bold',
                    fontSize=12,
                    textColor=colors.Color(0/255, 91/255, 150/255),
                    spaceBefore=12,
                    spaceAfter=6,
                ))
                styles.add(ParagraphStyle(
                    name='SummaryText',
                    fontName='Helvetica',
                    fontSize=10,
                    textColor=colors.black,
                    spaceAfter=4,
                ))

                # Header with logo (optional, add path to logo if available)
                logo_path = os.path.join('static', 'images', 'logo.jpg')  # Adjust path as needed
                if os.path.exists(logo_path):
                    logo = Image(logo_path, width=1.5*inch, height=1*inch)
                    logo.hAlign = 'LEFT'
                    elements.append(logo)

                # Title and period
                elements.append(Paragraph("GINYE NIFFER Weekly Financial Report", styles['CompanyTitle']))
                elements.append(Paragraph(f"Period: {start_of_week} to {end_of_week}", styles['ReportSubtitle']))
                elements.append(Spacer(1, 12))

                # Summary section
                elements.append(Paragraph("Financial Summary", styles['SectionHeader']))
                summary_data = [
                    [Paragraph("Total Earnings:", styles['SummaryText']), Paragraph(f"${total_earnings:,.2f}", styles['SummaryText'])],
                    [Paragraph("Total Expenses:", styles['SummaryText']), Paragraph(f"${total_expenses:,.2f}", styles['SummaryText'])],
                    [Paragraph("Profit/Loss:", styles['SummaryText']), Paragraph(f"${profit_loss:,.2f}", styles['SummaryText'])],
                ]
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 12))

                # Budgets section
                elements.append(Paragraph("Budgets", styles['SectionHeader']))
                budget_table_data = [['Category', 'Allocated', 'Spent', 'Remaining']]
                if budgets.exists():
                    for b in budgets:
                        budget_table_data.append([
                            b.category,
                            f"${float(b.allocated):,.2f}",
                            f"${float(b.spent):,.2f}",
                            f"${float(b.allocated - b.spent):,.2f}"
                        ])
                else:
                    budget_table_data.append(['No budgets available', '', '', ''])

                budget_table = Table(budget_table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                budget_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0/255, 91/255, 150/255)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.Color(240/255, 240/255, 240/255)),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(budget_table)
                elements.append(Spacer(1, 24))

                # Transactions section
                elements.append(Paragraph("Transactions (This Week)", styles['SectionHeader']))
                transaction_table_data = [['Date', 'Type', 'Category', 'Amount']]
                all_transactions = []
                for e in earnings:
                    all_transactions.append({'date': e.date, 'type': 'Income', 'category': e.project, 'amount': float(e.amount)})
                for e in expenses:
                    all_transactions.append({'date': e.date, 'type': 'Expense', 'category': e.category, 'amount': float(e.amount)})

                all_transactions.sort(key=lambda x: x['date'], reverse=True)

                if all_transactions:
                    for t in all_transactions:
                        transaction_table_data.append([
                            t['date'].strftime('%Y-%m-%d'),
                            t['type'],
                            t['category'],
                            f"${t['amount']:,.2f}"
                        ])
                else:
                    transaction_table_data.append(['No transactions available', '', '', ''])

                transaction_table = Table(transaction_table_data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch, 1.5*inch])
                transaction_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0/255, 91/255, 150/255)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.Color(240/255, 240/255, 240/255)),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(transaction_table)

                # Footer
                elements.append(Spacer(1, 24))
                elements.append(Paragraph("Generated by GINYE NIFFER Financial System", styles['Normal']))
                elements.append(Paragraph(f"Report Date: {today}", styles['Normal']))

                doc.build(elements)
                pdf_buffer.seek(0)

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="weekly_report_{start_of_week}.pdf"'
                response.write(pdf_buffer.read())
                logger.info("PDF report generated successfully (from test view)")
                return response
            except Exception as e:
                logger.error(f"PDF generation failed (from test view): {str(e)}", exc_info=True)
                return HttpResponse(
                    json.dumps({"error": f"Failed to generate PDF report (from test view): {str(e)}"}),
                    content_type='application/json',
                    status=500
                )

    except Exception as e:
        logger.error(f"Unexpected error in temp_weekly_report_test view: {str(e)}", exc_info=True)
        return HttpResponse(
            json.dumps({"error": f"An unexpected error occurred in test view: {str(e)}"}),
            content_type='application/json',
            status=500
        )
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from .models import CompanyDocument, Invoice
from .serializers import CompanyDocumentSerializer, InvoiceSerializer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import logging
import uuid
import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Add ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # Add TA_CENTER and TA_LEFT for alignment
from io import BytesIO
import matplotlib.pyplot as plt
import logging
import uuid
logger = logging.getLogger(__name__)

# Document CRUD
class CompanyDocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = CompanyDocument.objects.filter(user=request.user)
        serializer = CompanyDocumentSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CompanyDocumentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Document uploaded by user {request.user.username}: {serializer.data['title']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Document upload failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyDocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return CompanyDocument.objects.get(pk=pk, user=user)
        except CompanyDocument.DoesNotExist:
            return None

    def get(self, request, pk):
        document = self.get_object(pk, request.user)
        if not document:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyDocumentSerializer(document, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, pk):
        document = self.get_object(pk, request.user)
        if not document:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        document.delete()
        logger.info(f"Document deleted by user {request.user.username}: ID {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)

# Invoice CRUD
class InvoiceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invoices = Invoice.objects.filter(user=request.user)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        # Generate unique invoice number
        data['invoice_number'] = f"INV-{uuid.uuid4().hex[:8].upper()}"
        serializer = InvoiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"Invoice created by user {request.user.username}: {data['invoice_number']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Invoice creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Invoice.objects.get(pk=pk, user=user)
        except Invoice.DoesNotExist:
            return None

    def get(self, request, pk):
        invoice = self.get_object(pk, request.user)
        if not invoice:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    def delete(self, request, pk):
        invoice = self.get_object(pk, request.user)
        if not invoice:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
        invoice.delete()
        logger.info(f"Invoice deleted by user {request.user.username}: ID {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
# views.py
from rest_framework import status, generics, serializers  # Add serializers here
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from django.http import HttpResponse
from .models import Invoice
from .serializers import InvoiceSerializer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm
from io import BytesIO
import os
from pathlib import Path
import logging
from django.db.models import Count

# Additional imports for drawing the stamp
from reportlab.graphics.shapes import Drawing, Circle
from reportlab.graphics.charts.textlabels import Label

logger = logging.getLogger(__name__)

# Define exact colors matching the sample
GREEN_5280 = colors.Color(0/255, 170/255, 79/255)  # #00AA4F
LIGHT_BLUE = colors.Color(173/255, 216/255, 230/255)  # Light blue background

# API views for client names and details
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_client_names(request):
    client_names = Invoice.objects.values_list('client_name', flat=True).distinct()
    return Response({'client_names': list(client_names)})

@api_view(['GET'])
def get_client_details(request):
    name = request.GET.get('name', '')
    try:
        invoice = Invoice.objects.filter(client_name__iexact=name).last()
        if not invoice:
            return Response({'error': 'Client not found'}, status=404)
        return Response({
            'client_name': invoice.client_name,
            'client_location': invoice.client_location,
            'client_address': invoice.client_address,
            'client_tin': invoice.client_tin,
            'client_email': invoice.client_email,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# Invoice List and Create View
# views.py
# ... (other imports remain the same)

class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)

    def generate_invoice_number(self, client_name):
        client_name = client_name.upper()
        prefix_length = 3
        prefix = client_name[:3]
        existing_prefixes = Invoice.objects.values('client_name').distinct()
        for record in existing_prefixes:
            other_name = record['client_name'].upper()
            if other_name != client_name and other_name.startswith(prefix):
                prefix_length = 4
                prefix = client_name[:4]
                break
        invoice_count = Invoice.objects.filter(client_name__iexact=client_name).count()
        invoice_number_suffix = f"{invoice_count + 1:03d}"
        current_year = "2025"
        invoice_number = f"{prefix}.{current_year}.{invoice_number_suffix}"
        return invoice_number

    def perform_create(self, serializer):
        # No need to check client_name; the serializer already validates it
        invoice_number = self.generate_invoice_number(self.request.data['client_name'])
        serializer.save(user=self.request.user, invoice_number=invoice_number)

# ... (rest of the file remains the same)

# Invoice Detail View
class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)



# invoices/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from .models import Invoice
from .serializers import InvoiceSerializer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm
from io import BytesIO
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Define exact colors matching the sample
GREEN_5280 = colors.Color(0/255, 170/255, 79/255)  # #00AA4F
LIGHT_BLUE = colors.Color(173/255, 216/255, 230/255)  # Light blue background
# Invoice PDF View
class InvoicePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            invoice = Invoice.objects.filter(pk=pk, user=request.user).first()
            if not invoice:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to fetch invoice: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        pdf_buffer = BytesIO()
        try:
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                topMargin=15 * mm,
                bottomMargin=15 * mm,
                leftMargin=15 * mm,
                rightMargin=15 * mm
            )
            elements = []
            styles = getSampleStyleSheet()

            # Define custom styles
            styles.add(ParagraphStyle(
                name='CompanyName',
                fontName='Helvetica-Bold',
                fontSize=18,
                textColor=colors.black,
                alignment=TA_RIGHT,
                spaceAfter=0,
                leading=20
            ))
            styles.add(ParagraphStyle(
                name='CompanyInfo',
                fontName='Helvetica',
                fontSize=9,
                textColor=colors.black,
                alignment=TA_RIGHT,
                spaceAfter=0,
                leading=11
            ))
            styles.add(ParagraphStyle(
                name='InvoiceTitle',
                fontName='Helvetica-Bold',
                fontSize=11,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=0,
                leading=13
            ))
            styles.add(ParagraphStyle(
                name='ClientInfo',
                fontName='Helvetica',
                fontSize=9,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=0,
                leading=11
            ))
            styles.add(ParagraphStyle(
                name='ClientInfoBold',
                fontName='Helvetica-Bold',
                fontSize=9,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=0,
                leading=11
            ))
            styles.add(ParagraphStyle(
                name='TableHeader',
                fontName='Helvetica-Bold',
                fontSize=8,
                textColor=colors.black,
                alignment=TA_CENTER,
                leading=10
            ))
            styles.add(ParagraphStyle(
                name='TableHeaderLeft',
                fontName='Helvetica-Bold',
                fontSize=8,
                textColor=colors.black,
                alignment=TA_LEFT,
                leading=10
            ))
            styles.add(ParagraphStyle(
                name='TableCell',
                fontName='Helvetica',
                fontSize=8,
                textColor=colors.black,
                alignment=TA_LEFT,
                leading=10
            ))

            # Calculate total usable width
            page_width = A4[0]
            total_width = page_width - (15 * mm * 2)

            # HEADER SECTION
            logo_path = os.path.join(Path(__file__).parent, 'static', 'images', 'logo.jpg')
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=80, height=60)
            else:
                logo = Paragraph("Logo Placeholder", styles['ClientInfo'])

            company_name = Paragraph(
                "THE <font color='#00AA4F'>5280</font> AGENCY",
                styles['CompanyName']
            )
            company_address = Paragraph("P.O.BOX 13275,   DAR ES SALAAM", styles['CompanyInfo'])
            company_tin = Paragraph("TIN: 112-179-720  VRN: 40-312778-F", styles['CompanyInfo'])
            company_phone = Paragraph("+255 (0) 762 460 846", styles['CompanyInfo'])

            header_data = [
                [logo, company_name],
                ['', company_address],
                ['', company_tin],
                ['', company_phone]
            ]

            header_table = Table(header_data, colWidths=[total_width * 0.2, total_width * 0.8])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, 3), 'TOP'),
                ('ALIGN', (0, 0), (0, 3), 'LEFT'),
                ('VALIGN', (1, 0), (1, 3), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 3), 'RIGHT'),
                ('SPAN', (0, 0), (0, 3)),
                ('TOPPADDING', (0, 0), (0, 0), 0),
                ('BOTTOMPADDING', (0, 0), (0, 0), 0),
            ]))
            elements.append(header_table)

            # Green line under header
            green_line_data = [['', '']]
            green_line_table = Table(green_line_data, colWidths=[total_width])
            green_line_table.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (-1, 0), 1.5, GREEN_5280),
                ('TOPPADDING', (0, 0), (-1, 0), 2),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ]))
            elements.append(green_line_table)

            # CLIENT AND INVOICE DETAILS
            client_name = invoice.client_name
            client_location = invoice.client_location
            client_address = invoice.client_address
            client_tin = invoice.client_tin

            invoice_date = invoice.date.strftime('%dth %B %Y')
            invoice_number = invoice.invoice_number

            client_info = [
                [Paragraph(client_name, styles['ClientInfo']), Paragraph(str(invoice_date), styles['ClientInfo'])],
                [Paragraph(client_location, styles['ClientInfo']), Paragraph(f"Inv No. {invoice_number}", styles['ClientInfo'])],
                [Paragraph(f"Address: {client_address}", styles['ClientInfo']), ""],
                [Paragraph(f"TIN: {client_tin}", styles['ClientInfo']), ""],
            ]

            client_table = Table(client_info, colWidths=[total_width * 0.6, total_width * 0.4])
            client_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, 3), 'TOP'),
                ('ALIGN', (0, 0), (0, 3), 'LEFT'),
                ('VALIGN', (1, 0), (1, 3), 'TOP'),
                ('ALIGN', (1, 0), (1, 3), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            elements.append(client_table)
            elements.append(Spacer(1, 8))

            # INVOICE HEADING AND SUBTITLE
            invoice_title_data = [
                [Paragraph(invoice.heading, styles['InvoiceTitle'])],
                [Paragraph(invoice.subtitle, styles['InvoiceTitle'])]
            ]
            invoice_title_table = Table(invoice_title_data, colWidths=[total_width])
            invoice_title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(invoice_title_table)
            elements.append(Spacer(1, 2))

            # ITEMS TABLE
            if invoice.include_days:
                headers = ['S/N', 'ITEMS DESCRIPTION', 'QUANTITY', 'DAYS', 'RATE (TZS)', 'AMOUNT (TZS)']
                col_widths = [30, 250, 70, 45, 75, 75]
            else:
                headers = ['S/N', 'ITEMS DESCRIPTION', 'QUANTITY', 'RATE (TZS)', 'AMOUNT (TZS)']
                col_widths = [30, 295, 70, 75, 75]

            total_col_width = sum(col_widths)
            scaling_factor = total_width / total_col_width
            col_widths = [w * scaling_factor for w in col_widths]

            invoice_items = invoice.items
            vat_rate = invoice.vat_rate
            include_agent_fee = invoice.include_agent_fee
            agent_fee = invoice.agent_fee if include_agent_fee else 0

            items_data = [headers]

            for idx, item in enumerate(invoice_items, start=1):
                days = item.get('days', 1) if invoice.include_days else 1
                total = item['quantity'] * item['unit_price'] * days
                if invoice.include_days:
                    items_data.append([
                        str(idx),
                        Paragraph(item['description'], styles['TableCell']),
                        f"{item['quantity']}",
                        f"{days}",
                        f"{item['unit_price']:,.2f}",
                        f"{total:,.2f}"
                    ])
                else:
                    items_data.append([
                        str(idx),
                        Paragraph(item['description'], styles['TableCell']),
                        f"{item['quantity']}",
                        f"{item['unit_price']:,.2f}",
                        f"{total:,.2f}"
                    ])

            subtotal = sum(item['quantity'] * item['unit_price'] * (item.get('days', 1) if invoice.include_days else 1) for item in invoice_items)
            total_with_agent = subtotal + agent_fee
            vat_amount = (total_with_agent * vat_rate) / 100
            total_amount = total_with_agent + vat_amount

            if invoice.include_days:
                items_data.append(['', Paragraph('Direct Costs', styles['TableHeaderLeft']), '', '', '', f"{subtotal:,.2f}"])
                if include_agent_fee:
                    items_data.append(['', Paragraph('Agent Fee', styles['TableHeaderLeft']), '', '', '', f"{agent_fee:,.2f}"])
                    items_data.append(['', Paragraph('Total Cost (exclusive VAT)', styles['TableHeaderLeft']), '', '', '', f"{total_with_agent:,.2f}"])
                items_data.extend([
                    ['', Paragraph('VAT', styles['TableHeaderLeft']), '', '', f"{vat_rate}%", f"{vat_amount:,.2f}"],
                    ['', Paragraph('Total with VAT', styles['TableHeaderLeft']), '', '', '', f"{total_amount:,.2f}"]
                ])
            else:
                items_data.append(['', Paragraph('Direct Costs', styles['TableHeaderLeft']), '', '', f"{subtotal:,.2f}"])
                if include_agent_fee:
                    items_data.append(['', Paragraph('Agent Fee', styles['TableHeaderLeft']), '', '', f"{agent_fee:,.2f}"])
                    items_data.append(['', Paragraph('Total Cost (exclusive VAT)', styles['TableHeaderLeft']), '', '', f"{total_with_agent:,.2f}"])
                items_data.extend([
                    ['', Paragraph('VAT', styles['TableHeaderLeft']), '', f"{vat_rate}%", f"{vat_amount:,.2f}"],
                    ['', Paragraph('Total with VAT', styles['TableHeaderLeft']), '', '', f"{total_amount:,.2f}"]
                ])

            items_table = Table(items_data, colWidths=col_widths, repeatRows=1)

            row_styles = []
            row_styles.append(('BOX', (0, 0), (-1, -1), 1, colors.black))
            row_styles.append(('BACKGROUND', (0, 0), (-1, 0), LIGHT_BLUE))
            row_styles.append(('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'))
            row_styles.append(('FONTSIZE', (0, 0), (-1, 0), 8))
            row_styles.append(('ALIGN', (0, 0), (-1, 0), 'CENTER'))
            row_styles.append(('VALIGN', (0, 0), (-1, 0), 'MIDDLE'))
            row_styles.append(('GRID', (0, 0), (-1, 0), 1, colors.black))

            num_items = len(invoice_items)
            row_styles.append(('FONTSIZE', (0, 1), (-1, num_items), 8))
            row_styles.append(('ALIGN', (0, 1), (0, num_items), 'CENTER'))
            if invoice.include_days:
                row_styles.append(('ALIGN', (2, 1), (3, num_items), 'CENTER'))
                row_styles.append(('ALIGN', (4, 1), (5, num_items), 'RIGHT'))
                row_styles.append(('GRID', (0, 1), (-1, num_items), 1, colors.black))
            else:
                row_styles.append(('ALIGN', (2, 1), (2, num_items), 'CENTER'))
                row_styles.append(('ALIGN', (3, 1), (4, num_items), 'RIGHT'))
                row_styles.append(('GRID', (0, 1), (-1, num_items), 1, colors.black))

            total_start = num_items + 1
            row_styles.append(('BACKGROUND', (0, total_start), (-1, -1), LIGHT_BLUE))
            row_styles.append(('ALIGN', (1, total_start), (1, -1), 'LEFT'))
            row_styles.append(('ALIGN', (-1, total_start), (-1, -1), 'RIGHT'))
            row_styles.append(('FONTNAME', (1, total_start), (1, -1), 'Helvetica-Bold'))
            row_styles.append(('FONTSIZE', (0, total_start), (-1, -1), 8))
            row_styles.append(('GRID', (-1, total_start), (-1, -1), 1, colors.black))
            row_styles.append(('LINEABOVE', (1, total_start), (-1, total_start), 1, colors.black))

            items_table.setStyle(TableStyle(row_styles))
            elements.append(items_table)
            elements.append(Spacer(1, 10))

            # FOOTER SECTION WITH IMPROVED SIGNATURE AND STAMP OVERLAY
            footer_data = [
                [Paragraph("<b>Prepared by:</b>", styles['ClientInfoBold']),
                 Paragraph("<b>Client's Approval:</b>", styles['ClientInfoBold'])],
                [Paragraph("Account details", styles['ClientInfo']),
                 Paragraph("Sign: ........................................................", styles['ClientInfo'])],
                [Paragraph("The 5280 Agency", styles['ClientInfo']),
                 Paragraph("Date: ........................................................", styles['ClientInfo'])],
                [Paragraph("Account No: NMB Bank - 22610041526", styles['ClientInfo']),
                 Paragraph("", styles['ClientInfo'])],
                [Paragraph("Approved by:", styles['ClientInfo']),
                 Paragraph("", styles['ClientInfo'])],
            ]

            # Create the GM line with signature and stamp overlay
            signature_filename = f"{invoice.signature_choice}-signature.png" if invoice.signature_choice else None
            signature_path = os.path.join(Path(__file__).parent, 'static', 'images', signature_filename) if signature_filename else None
            stamp_path = os.path.join(Path(__file__).parent, 'static', 'images', 'stamp.png')

            # Create a frame for the signature area
            gm_line = Paragraph("GM: ........................................................", styles['ClientInfo'])
            signature_frame = Table([[gm_line]], colWidths=[total_width * 0.5])

            # Create overlay elements
            overlay_elements = []
            signature_width = 70
            signature_height = 20
            stamp_width = 80
            stamp_height = 80

            if signature_path and os.path.exists(signature_path):
                try:
                    signature_image = Image(signature_path, width=signature_width, height=signature_height)
                    # Position signature to align with dotted line
                    signature_table = Table([[signature_image]], colWidths=[signature_width])
                    signature_table.setStyle(TableStyle([
                        ('LEFTPADDING', (0, 0), (-1, -1), 20),  # Adjust to align with dotted line
                        ('TOPPADDING', (0, 0), (-1, -1), -50),  # Vertical adjustment
                    ]))
                    overlay_elements.append(signature_table)
                except Exception as e:
                    logger.error(f"Failed to load signature image: {e}")

            if os.path.exists(stamp_path):
                try:
                    stamp_image = Image(stamp_path, width=stamp_width, height=stamp_height)
                    # Position stamp to overlay both signature and dotted line
                    stamp_table = Table([[stamp_image]], colWidths=[stamp_width])
                    stamp_table.setStyle(TableStyle([
                        ('LEFTPADDING', (0, 0), (-1, -1), 100),  # Adjust to overlay signature
                        ('TOPPADDING', (0, 0), (-1, -1), -40),  # Vertical adjustment
                    ]))
                    overlay_elements.append(stamp_table)
                except Exception as e:
                    logger.error(f"Failed to load stamp image: {e}")

            # Create a container for the GM line and overlay elements
            footer_container = Table([
                [signature_frame],
                *[[element] for element in overlay_elements]
            ], colWidths=[total_width * 0.5])

            footer_container.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ]))

            # Add the container to footer data
            footer_data.append([footer_container, Paragraph("Rubber Stamp", styles['ClientInfo'])])

            footer_table = Table(footer_data, colWidths=[total_width * 0.5, total_width * 0.5])
            footer_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))

            elements.append(footer_table)

            # Build PDF
            doc.build(elements)
            pdf_buffer.seek(0)
            return HttpResponse(pdf_buffer, content_type='application/pdf')

        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return Response({"error": f"PDF generation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
import os

class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = CompanyDocument.objects.filter(pk=pk, user=request.user).first()
        if not document:
            return Response({"error": "Document not found"}, status=404)
        
        actual_path = '/home/tpf/django_react_project/ea_marketing_project/ea_marketing_backend/ea_marketing_backend/media/' + document.file.name
        if os.path.exists(actual_path):
            return FileResponse(open(actual_path, 'rb'), as_attachment=True)
        return Response({"error": "File not found"}, status=404)
    
# views.py
from django.http import JsonResponse
from django.conf import settings

def media_path_test(request):
    return JsonResponse({
        'BASE_DIR': settings.BASE_DIR,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
        'MEDIA_URL': settings.MEDIA_URL,
        'sample_file_exists': os.path.exists(
            os.path.join(settings.MEDIA_ROOT, 'documents/1/weekly_report_pdf_1_eNcf7Qq.pdf')
        )
    })
    
