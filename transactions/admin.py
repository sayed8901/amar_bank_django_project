from django.contrib import admin
from .models import Transaction

from .views import send_transaction_email

# # Normal way to register in Admin Panel
# admin.site.register(Transaction)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # admin panel theke table akare, ki ki field show korte chai
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']

    # directly admin panel theke Transaction model er kono field jemon 'loan_approve' ba 'balance_after_transaction er value update korte...
    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance

        obj.account.save()

        # mail sending implementation for loan approval message
        send_transaction_email(obj.account.user, obj.amount, 'Loan Approval Message', 'transactions/admin_loan_approval_email.html')

        super().save_model(request, obj, form, change)
