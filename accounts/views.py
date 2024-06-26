from django.shortcuts import render, redirect
from django.views.generic import FormView

from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout
from django.urls import reverse_lazy

from django.views import View

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# to implement email sending functionality
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string




# Create your views here.
class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        # print(form.cleaned_data)

        user = form.save() # user registration form er data database e save hoye jabe
        login(self.request, user)
        print(user)

        return super().form_valid(form) # jodi form checking e sob thik thake tahole, form_valid function automatically mane nije nijei jeno call hoy tai etike supe() evabe diye call jore deya hocche
    



# Class based LoginView
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'

    def get_success_url(self):
        return reverse_lazy('home')



# Class based LogoutView
class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)

        return reverse_lazy('home')



# Alternatively, Function based LogoutView
def user_logout(request):
    logout(request)
    return redirect('home')





# UserUpdateView
class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'


    def get(self, request):
        form = UserUpdateForm(instance = request.user)
        return render(request, self.template_name, {'form': form})
    

    def post(self, request):
        form = UserUpdateForm(request.POST, instance = request.user)

        if form.is_valid():
            print(form.cleaned_data)
            form.save()

            return redirect('profile') # Redirect to the user's profile page
        
        return render(request, self.template_name, {'form': form})
    




# function to change password using old password
def password_change(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordChangeForm(user = request.user, data = request.POST)

            if form.is_valid():
                form.save()
                # password update korbe
                update_session_auth_hash(request, form.user)

                # sending email notification
                send_email = EmailMessage(
                    'Password Change Notification', 
                    'You have successfully changed your password.', 
                    to = [request.user.email]
                )

                send_email.send()


                return redirect('profile')
            
        else:
            form = PasswordChangeForm(user = request.user)
            
        return render(request, 'accounts/password_change.html', {'form': form})
    
    else:
        return redirect('login')
    



