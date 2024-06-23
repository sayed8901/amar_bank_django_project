from django import forms
from .models import UserBankAccount, UserAddress
from .constants import ACCOUNT_TYPE, GENDER_TYPE

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    
    # for account info, creating form input fields using model form
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

    # for address info, creating form input fields using model form
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)


    # for user info, using model form
    class Meta:
        model = User

        # combining all the input fields from 3 different models
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2',
            'account_type', 'gender', 'birth_date',
            'street_address', 'city', 'postal_code', 'country',
        ]
    

    # for saving all the 3 types data models into the database
    def save(self, commit=True):
        new_user = super().save(commit=False) # ekhon sudhu anka user toiri korbo, database a data save korbo na. karon age nicher kaj gulo korte hobe

        if commit == True:
            new_user.save() # user model er data database e save korlam

            # workings for address model form
            street_address_field = self.cleaned_data.get('street_address')
            city_field = self.cleaned_data.get('city')
            postal_code_field = self.cleaned_data.get('postal_code')
            country_field = self.cleaned_data.get('country')

            # creating an address object
            UserAddress.objects.create(
                user = new_user,
                street_address = street_address_field,
                city = city_field,
                postal_code = postal_code_field,
                country = country_field
            )


            # workings for account model form
            account_type_field = self.cleaned_data.get('account_type')
            gender_field = self.cleaned_data.get('gender')
            birth_date_field = self.cleaned_data.get('birth_date')

            # creating an account object
            UserBankAccount.objects.create(
                user = new_user,
                account_type = account_type_field,
                birth_date = birth_date_field,
                gender = gender_field,

                # creating account number
                account_no = 100000 + new_user.id
            )
        
        return new_user
    


    # Adding Styles to form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # super() die existing user form er object ke inherite kore anlam, tarpor necessary over-wrighting korbo..

        for field in self.fields:
            # print(field)

            self.fields[field].widget.attrs.update({
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })

        
    


# Updating profile
# orthat, user tar profile e ki ki jinish update korte parbe...

class UserUpdateForm(forms.ModelForm):

    # for account info, creating form input fields using model form
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

    # for address info, creating form input fields using model form
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)


    # for user info, using model form
    class Meta:
        model = User
        # user model theke sudhu first_name, last_name & email update korte dibo.. username ba password basically ekhane change korte dicchi na...
        fields = ['first_name', 'last_name', 'email']



    # Adding Styles to form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # super() die existing user form er object ke inherite kore anlam, tarpor necessary over-wrighting korbo..

        for field in self.fields:
            # print(field)

            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })



        # jodi user er account thake tahole setir ekta instance ber korchi
        if self.instance:
            try:
                # jodi kono user thake tahole tar user_account & user_address ber korchi
                user_account = self.instance.account
                user_address = self.instance.address

            except UserBankAccount.DoesNotExist:
                # user na thake tahole tar user_account & user_address None dhorchi
                user_account = None
                user_address = None


            # jodi user thake tahole..
            if user_account:
                # user_account er data update korar jonno fields dichhi, sathe initial value hishebe current data dekhacchi
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                
                # ekivabe, user_address er data update korar jonno fields dichhi, sathe initial value hishebe current data dekhacchi
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country



    # for saving all the 3 types data models into the database
    def save(self, commit=True):

        user = super().save(commit=False) # ekhon sudhu anka user toiri korbo, database a data save korbo na. karon age nicher kaj gulo korte hobe

        if commit:
            user.save() # user model er data database e save korlam

            # jodi account thake taile seta jabe user_account e, ar jodi account na thake taile create hobe ar seta created er moddhe jabe
            user_account, created = UserBankAccount.objects.get_or_create(user=user)

            # workings for account model form
            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']

            user_account.save() # user model er data database e save korlam


            # ekivabe, jodi address thake taile seta jabe user_address e, ar jodi address na thake taile create hobe ar seta created er moddhe jabe
            user_address, created = UserAddress.objects.get_or_create(user=user)

            # workings for address model form
            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']

            user_address.save() # user model er data database e save korlam

        # Finally providing the user model after performing all the above mentioned operations
        return user




