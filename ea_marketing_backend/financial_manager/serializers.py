from rest_framework import serializers
from .models import UserProfile, CompanyEarning, CompanyExpense, Budget, Investment, Transaction, CompanyDocument, Invoice

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'name', 'email', 'phone', 'address', 'date_of_birth', 'account_created', 'language', 'theme']

class CompanyEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyEarning
        fields = ['id', 'project', 'amount', 'date']

class CompanyExpenseSerializer(serializers.ModelSerializer):
    budget = serializers.PrimaryKeyRelatedField(queryset=Budget.objects.all())

    class Meta:
        model = CompanyExpense
        fields = ['id', 'category', 'amount', 'date', 'budget']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'allocated', 'spent']

class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = ['id', 'type', 'amount']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'date', 'description', 'category', 'amount', 'type']

class CompanyDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyDocument
        fields = ['id', 'title', 'file', 'file_url', 'file_type', 'uploaded_at']
        read_only_fields = ['id', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):  # Properly indented method
        request = self.context.get('request')
        if obj.file:
            # Handle both FileField and ImageField
            file_url = obj.file.url if hasattr(obj.file, 'url') else obj.file
            return request.build_absolute_uri(file_url) if request else file_url
        return None


# serializers.py
from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client_name', 'client_location', 'client_address',
            'client_tin', 'client_email', 'date', 'heading', 'subtitle', 'items',
            'vat_rate', 'include_days', 'include_agent_fee', 'agent_fee', 'total_amount',
            'created_at', 'signature_choice'
        ]
        read_only_fields = ['id', 'created_at', 'invoice_number']

    def validate_items(self, value):
        for item in value:
            if not item.get('description'):
                raise serializers.ValidationError("Each item must have a description.")
            if not isinstance(item.get('quantity'), (int, float)) or item['quantity'] < 1:
                raise serializers.ValidationError("Quantity must be a positive number.")
            if not isinstance(item.get('unit_price'), (int, float)) or item['unit_price'] < 0:
                raise serializers.ValidationError("Unit price must be a non-negative number.")
            if 'days' in item and (not isinstance(item['days'], (int, float)) or item['days'] < 1):
                raise serializers.ValidationError("Days must be a positive number.")
        return value

    def validate_vat_rate(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise serializers.ValidationError("VAT rate must be a non-negative number.")
        return value

    def validate_date(self, value):
        if not value:
            raise serializers.ValidationError("Date is required.")
        return value

    def validate_signature_choice(self, value):
        if value not in [None, 'elisha', 'ginye', 'siza']:
            raise serializers.ValidationError("Invalid signature choice.")
        return value