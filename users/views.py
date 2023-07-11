from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

from .models import UserProfile
from django.db import DatabaseError

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        message=None
        try :
            form.is_valid()
        except DatabaseError as e:
                message=e 
                if message != None:
                    form = UserCreationForm()
                    return render(request, 'users/register.html', {'form': form,'message':'erreur dans le registre des utilisateurs '})
        if message==None:

            user = form.save()

            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()

            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            public_key_pem_str = public_key_pem.decode()  


            user_profile = UserProfile.objects.create(user=user, public_key=public_key_pem_str,all_plot_code=[])





            return render(request, 'users/keys.html', {
                'username': user.username,
                'private_key': private_key_pem.decode(),
                'public_key': public_key_pem.decode(),
            })

    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})



