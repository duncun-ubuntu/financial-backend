# urls.py
from django.urls import path
from .views import (
    UserProfileView,
    CompanyEarningListCreateView, CompanyEarningDetailView,
    CompanyExpenseListCreateView, CompanyExpenseDetailView,
    BudgetListCreateView, BudgetDetailView,
    InvestmentListCreateView, InvestmentDetailView,
    TransactionListCreateView, TransactionDetailView,
    temp_weekly_report_test,
    CompanyDocumentListCreateView, CompanyDocumentDetailView,
    InvoiceListCreateView, InvoiceDetailView, InvoicePDFView, DocumentDownloadView,
    get_client_names, get_client_details  # Add these imports
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('earnings/', CompanyEarningListCreateView.as_view(), name='earnings_list_create'),
    path('earnings/<int:pk>/', CompanyEarningDetailView.as_view(), name='earnings_detail'),
    path('expenses/', CompanyExpenseListCreateView.as_view(), name='expenses_list_create'),
    path('expenses/<int:pk>/', CompanyExpenseDetailView.as_view(), name='expenses_detail'),
    path('budgets/', BudgetListCreateView.as_view(), name='budgets_list_create'),
    path('budgets/<int:pk>/', BudgetDetailView.as_view(), name='budgets_detail'),
    path('investments/', InvestmentListCreateView.as_view(), name='investments_list_create'),
    path('investments/<int:pk>/', InvestmentDetailView.as_view(), name='investments_detail'),
    path('transactions/', TransactionListCreateView.as_view(), name='transactions_list_create'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transactions_detail'),
    path('weekly-report/', temp_weekly_report_test, name='weekly_report'),
    path('documents/', CompanyDocumentListCreateView.as_view(), name='documents_list_create'),
    path('documents/<int:pk>/', CompanyDocumentDetailView.as_view(), name='documents_detail'),
    path('invoices/', InvoiceListCreateView.as_view(), name='invoices_list_create'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoices_detail'),
    path('invoices/<int:pk>/pdf/', InvoicePDFView.as_view(), name='invoice_pdf'),
    path('documents/<int:pk>/download/', DocumentDownloadView.as_view()),
    path('invoices/client_names/', get_client_names, name='client-names'),  # Add this route
    path('invoices/client_details/', get_client_details, name='client-details'),  # Add this route
]