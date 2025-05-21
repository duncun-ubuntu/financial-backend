# ea_marketing_backend/financial_manager/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
import os

def validate_file_size(value):
    max_size = 1 * 1024 * 1024  # 1MB in bytes
    if value.size > max_size:
        raise ValidationError("File size cannot exceed 1MB.")

def document_upload_path(instance, filename):
    return f"documents/{instance.user.id}/{filename}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.URLField(max_length=200, blank=True, default='https://via.placeholder.com/150')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    account_created = models.DateField(auto_now_add=True)
    language = models.CharField(max_length=50, default='English')
    theme = models.CharField(max_length=50, default='Light')

    def __str__(self):
        return self.name

class CompanyEarning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.project} - {self.amount}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    allocated = models.DecimalField(max_digits=10, decimal_places=2)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    _skip_validation = False  # Flag to bypass validation

    def __str__(self):
        return self.category

    def clean(self):
        if not self._skip_validation:
            if self.spent > self.allocated:
                raise ValidationError(f"Spent amount ({self.spent}) cannot exceed allocated amount ({self.allocated}).")

    def save(self, *args, **kwargs):
        if not self._skip_validation:
            self.clean()
        super().save(*args, **kwargs)

class CompanyExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    _skip_validation = False  # Flag to bypass validation

    def __str__(self):
        return f"{self.category} - {self.amount}"

    def clean(self):
        if not self._skip_validation:
            budget = self.budget
            current_spent = sum(Decimal(str(exp.amount)) for exp in budget.expenses.exclude(id=self.id))
            if current_spent + self.amount > budget.allocated:
                raise ValidationError(
                    f"Expense of {self.amount} exceeds remaining budget ({budget.allocated - current_spent}) for {budget.category}."
                )

    def save(self, *args, **kwargs):
        if not self._skip_validation:
            self.clean()
        super().save(*args, **kwargs)
        # Update budget's spent amount
        self.budget.spent = sum(Decimal(str(exp.amount)) for exp in self.budget.expenses.all())
        self.budget._skip_validation = True  # Bypass Budget validation
        self.budget.save()

class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.type} - {self.amount}"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50)  # "Income" or "Expense"

    def __str__(self):
        return f"{self.description} - {self.amount}"

class CompanyDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    file = models.CharField(max_length=100)  # Temporary for seeding
    file_type = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'),
        ('docx', 'Word'),
        ('xlsx', 'Excel'),
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.file_type})"

    def clean(self):
        if not hasattr(self, '_skip_validation') or not self._skip_validation:
            ext = os.path.splitext(self.file)[1].lower()
            valid_extensions = {
                'pdf': ['.pdf'],
                'docx': ['.docx', '.doc'],
                'xlsx': ['.xlsx', '.xls'],
            }
            if ext not in valid_extensions[self.file_type]:
                raise ValidationError(f"File extension {ext} does not match selected file type {self.file_type}.")

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=255)
    client_location = models.CharField(max_length=255)
    client_address = models.CharField(max_length=255)
    client_tin = models.CharField(max_length=50)
    client_email = models.EmailField()
    date = models.DateField()
    heading = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    items = models.JSONField()
    vat_rate = models.FloatField()
    include_days = models.BooleanField(default=False)
    include_agent_fee = models.BooleanField(default=False)
    agent_fee = models.FloatField(default=0.0)
    total_amount = models.FloatField()
    invoice_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    signature_choice = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('elisha', 'Elisha Signature'),
            ('ginye', 'Ginye Signature'),
            ('siza', 'Siza Signature'),
        ]
    )

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.client_name}"