from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import UserRegisterationForm
from .models import User


def register(request):
    if request.method == 'POST':
        register_form = UserRegisterationForm(request.POST)
        if register_form.is_valid():
            first_name = register_form.cleaned_data.get('first_name')
            last_name = register_form.cleaned_data.get('last_name')
            phone_number = register_form.cleaned_data.get('phone_number')
            email = register_form.cleaned_data.get('email')
            password = register_form.cleaned_data.get('password')
            username = email.split('@')[0]
            user = User.objects.create_user(email, first_name, last_name, username, password)
            user.phone_number = phone_number
            user.save()

            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            print(uid, token)
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': uid,
                'token': token
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect(f'/account/login/?command=verification&email={to_email}')
    else:
        register_form = UserRegisterationForm()
    context = {
        'register_form': register_form
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            # messages.success(request, "Logged In Successfuly")
            return redirect('home')
        else:
            messages.error(request, "Invalid Credential!")
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Logged Out!")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link!")
        return redirect('register')
    
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        if User.objects.filter(email__iexact=email).exists():
            user = User.objects.get(email__iexact=email)

            # reset password email activation link
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            print(uid, token)
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': uid,
                'token': token
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect(f'/account/login/?command=validate_password&email={to_email}')
        else:
            messages.error(request, 'Account does not exists!')
            return redirect('forget_password')
        
    return render(request, 'accounts/forget_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        messages.success(request, "Password updated successfuly.")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link!")
        return redirect('forget_password')