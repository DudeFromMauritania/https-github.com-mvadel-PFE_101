# from django.shortcuts import render
# from django.contrib.auth.forms import UserCreationForm
# # Create your views here.

# # def register(request):
# #     form = UserCreationForm()
# #     return render( request, 'users/register.html',{ 'form': form } )


# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#     else:
#         form = UserCreationForm()
#     return render(request, 'users/register.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

from .models import UserProfile

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the user object
            user = form.save()

            # Generate the public and private keys for the user
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()

            # Convert the keys to PEM format
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Save the public key to the user's profile in the database
            user_profile = UserProfile(user=user, public_key=public_key_pem)
            user_profile.save()

            # Render a template showing the public and private keys
            return render(request, 'users/keys.html', {
                'username': user.username,
                'private_key': private_key_pem.decode(),
                'public_key': public_key_pem.decode(),
            })
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
