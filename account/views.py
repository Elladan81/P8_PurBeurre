import logging
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib import messages

UserModel = get_user_model()

logger = logging.getLogger(__name__)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authentification réussie')
                else:
                    return HttpResponse('Compte indisponible')
            else:
                logger.info('Log Fail', exc_info=True, extra={'request': request})
                return HttpResponse('Ce compte est invalide')
    else:
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard'})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # new_user account is not active
            new_user.is_active = False
            # Save the user object
            new_user.save()
            # create the user profile
            Profile.objects.create(user=new_user)
            # send email to new_user to valid subscription
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('account/acc_active_email.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': default_token_generator.make_token(new_user)
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil mis à jour')
            return redirect('dashboard')
        else:
            messages.error(request, 'Impossible de mettre a jour ce profil')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


def activate(request, uidb64, token):
    """Is used to activate account by email"""
    try:
        # check uid and user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExit):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        # if everything ok, update user.is_active to True
        user.is_active = True
        user.save()
        messages.success(request, "Merci d'avoir validé votre email, vous pouvez vous connecter")
        return redirect('login')
    else:
        messages.error(request, "Votre lien d'activation est invalide")
        return redirect('purbeurre_website:index')