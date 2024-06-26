from django.db.models.query import QuerySet
from django.views.generic import CreateView, ListView
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from datetime import datetime
from django.utils import timezone

from django.db.models import Sum

from django.contrib.auth.models import User
from accounts.models import UserBankAccount


# importing LoginRequiredMixin to protect TransactionCreateMixin class so that only a logged in user can view these...
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm, MoneyTransferForm
from .constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID, SEND_MONEY, RECEIVE_MONEY


# to implement email sending functionality
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string




# creating a function to use send message functionality
def send_transaction_email(user, amount, subject, template):
    send_email = EmailMultiAlternatives(subject, '', to = [user.email])
    message = render_to_string(template, {
        'user': user,
        'amount' : amount,
    })
    send_email.attach_alternative(message, 'text/html')

    send_email.send()




# Create your views here.

# Ekta common transaction class create korchi, jeti inherite kore multiple transactions for example: deposit, withdraw or loan er kaj kora jabe
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    success_url = reverse_lazy('transaction_report')

    title = '' # echarao extra hisheba title ke form e pass kora jete pare, jar fole dynamically form er title show korano jabe


    # kono transaction er somoy, user er account ta transaction form e pass kore dite..
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account
        })

        return kwargs


    # template e 'title' ke context data hishebe pass korte...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title,
        })

        return context
    



# creating DepositMoneyView
class DepositMoneyView(TransactionCreateMixin):
    # TransactionCreateMixin ke inherite korer fole 'template_name', 'model = Transaction', & 'success_url' sobguloi ekhane inherited hohe gese, mane egulo use hocche...

    
    form_class = DepositForm # different transaction type er jonno 'form_class' e different type er form use korte hobe. for example: ekhane 'DepositMoneyView' er jonno 'DepositForm' use korte hobe
    
    title = 'Deposit' # extra hisheba amra akehane title ke-o form e mane frontend e pass kore dite pari

    # jehetu frontend e transaction_type field ta hidden kora ache, sehetu deposit form ta frontend theke view hobar somoy e backend theke transaction_type ke 'Deposit' hishebe set kore dicchi...
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial


    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        account.balance += amount

        account.save(
            update_fields=['balance',] # saving updated balance field
        )
        

        # messages to show from frontend
        messages.success(
            self.request,
            f'{amount}$ has been deposited to your account successfully.'
        )


        # mail sending implementation for deposit message
        send_transaction_email(self.request.user, amount, 'Deposit Message', 'transactions/deposit_email.html')


        return super().form_valid(form) # finally, parent ke overwrite kore uporer kajgulo define kore save kore dicchi
    
    


# DepositMoneyView er moto same to same vabe WithdrawMoneyView create korchi
class WithdrawMoneyView(TransactionCreateMixin):    
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields=['balance',] # saving updated balance field
        )
        
        messages.success(
            self.request,
            f'Successfully {amount}$ has been withdrawn from your account.'
        )

        # mail sending implementation for withdrawal message
        send_transaction_email(self.request.user, amount, 'Withdrawal Message', 'transactions/withdrawal_email.html')

        return super().form_valid(form)
    
    


# DepositMoneyView er moto same to same vabe LoanRequestView create korchi
class LoanRequestView(TransactionCreateMixin):    
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        # counting the approved loan_term for the current user
        current_loan_count = Transaction.objects.filter(
            account = self.request.user.account, 
            transaction_type = LOAN, 
            loan_approve = True
        ).count()

        if current_loan_count >= 3:
            return messages.warning('You have crossed the load limit')
            # return HttpResponse('You have crossed the limits.')
        else:
            messages.success(
                self.request,
                f'Loan request for {amount}$ has been submitted successfully.'
            )

            # mail sending implementation for loan request message
            send_transaction_email(self.request.user, amount, 'Loan Request Message', 'transactions/loan_request_email.html')

        return super().form_valid(form)
    
    




# creating TransactionReportView
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    context_object_name = 'report_list' # context ke nidrishto name dite...

    balance = 0 # filter korar pore ba age amar total balance ke show korbe
     

    def get_queryset(self):
        # jodi user kono date filter na kore, tahole tar total transaction report dekhabo
        # current user er sob data filter kore nie aslam
        queryset = Transaction.objects.filter(account = self.request.user.account)

        # defining string type date to use for query..
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            # converting string type dates to datetime type objects
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            # over-writing query parameters with defined date range
            queryset = queryset.filter(
                timestamp__date__gte = start_date,
                timestamp__date__lte = end_date)

            self.balance = Transaction.objects.filter(
                timestamp__date__gte = start_date, 
                timestamp__date__lte = end_date
            ).aggregate(Sum('amount'))['amount__sum']
            # (sql db er moto) django er models e multiple function er upore kono kaj korte use hoy. Jemon ekhane defined date duration er sobgulo amount sum kora hocche. and, satike amra 'amount_sum' name pore access korte parbo...
        else:
            # jodi kono filter na kore tahole current balance kei pass kore deya hocche...
            self.balance = self.request.user.account.balance
        
        # return queryset.distinct() # (sql er moto distinct() mane) unique queryset hote hobe
        return queryset


    # template e 'account' ke context data hishebe pass korte...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account,
        })

        return context




# creating PayLoanView
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id = loan_id)

        # jodi user er loan_approved kora thate tokhoni kebol se tar loan payment korte parbe...
        if loan.loan_approve == True:
            user_account = loan.account
        
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()

                loan.loan_approve = True
                loan.transaction_type = LOAN_PAID
                loan.save()

                return redirect('loan_list')
            
            else:
                messages.error(self.request, 'Loan amount is greater than your available balance.')
    
        return redirect('loan_list')




# creating LoanListView
class LoanListView(LoginRequiredMixin, ListView):
    template_name = 'transactions/loan_request.html'
    model = Transaction

    # context ke nidrishto name dite...
    context_object_name = 'loans' # total loan list ta ei loans context er moddhe thakbe

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(
            account = user_account, 
            transaction_type = LOAN
        )
        print(queryset)
        return queryset
    



# Money Transfer Class-based CreateView
class MoneyTransferView(TransactionCreateMixin):    
    form_class = MoneyTransferForm
    title = 'Money Transfer'
    template_name = 'transactions/money_transfer_form.html'
    success_url = reverse_lazy('transaction_report')

    def get_initial(self):
        initial = {'transaction_type': SEND_MONEY}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account_no = form.cleaned_data.get('account_number')
 
        # receiver activity
        receiver_account = UserBankAccount.objects.get(account_no = account_no)
        receiver_account.balance += amount

        receiver_account.save(
            update_fields = ['balance']
        )
 
        receiver_transaction = Transaction(
            amount = amount,
            transaction_type = RECEIVE_MONEY,
            account = receiver_account,
            balance_after_transaction = receiver_account.balance
        )
        
        receiver_transaction.save()
 

        # sender activity
        sender_account = self.request.user.account
        sender_account.balance -= amount

        sender_account.save(
            update_fields = ['balance']
        )
 
        messages.success(self.request, f"{amount} has been sent to Account: {account_no}")

        
        return super().form_valid(form)


