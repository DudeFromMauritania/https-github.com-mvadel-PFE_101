from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cryptography.hazmat.primitives.asymmetric import padding, rsa ,dsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from users.models import UserProfile
from cryptography.hazmat.primitives import serialization
from django.db import connections


from users.models import UserProfile
from main.models import Transaction, Block, LandList

from django.contrib.auth.models import User

@login_required
def generate_signature(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        private_key_pem = request.POST.get('private_key')


        private_key =load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )

        signature = private_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return render(request, 'signature/result.html', {
            'message': message,
            'signature': signature.hex()
        })

    return render(request, 'signature/generate.html')





def verify_signature(request):
    if request.method == 'POST':
        plot_code = request.POST.get('plot_code')
        sender_username = request.POST.get('sender_username')
        receiver_username = request.POST.get('receiver_username')
        signature = request.POST.get('signature')
        
        if not plot_code.isdigit() :
             return render(request, 'verify/verify.html', {'message':"Veuillez entrer uniquement des chiffres"})

        receiver = User.objects.filter(username=receiver_username).first()
        sender = User.objects.filter(username=sender_username).first()
        if receiver is None or sender is None:
            return render(request, 'verify/verify.html', {'message': 'Le nom d\'utilisateur de l\'expéditeur ou du destinataire n\'existe pas'})



        land_list = LandList.objects.filter(plot_code=plot_code).first()

        if land_list is  None:
            return render(request, 'verify/verify.html', {'message': "le  terrain ID n\'existe pas"})

        data = f'{plot_code} {sender_username} {receiver_username}'


        user_to_v = User.objects.get(username=sender_username)
        user_profile = UserProfile.objects.get(user_id=user_to_v.id)
        public_key_pem = user_profile.public_key.encode() 


        public_key = load_pem_public_key(public_key_pem)

        try:
            signature = bytes.fromhex(signature)

            public_key.verify(
                signature,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            verification_result = True
        except InvalidSignature:

            verification_result = False
        except Exception:

            verification_result = False


        return render(request, 'verify/verify.html', {
            'verification_result': verification_result
        })

    return render(request, 'verify/verify.html')


@login_required
def userprofile(request):
    user_id = request.user.id
    user_profile = UserProfile.objects.get(user_id=user_id)
    public_key_pem = user_profile.public_key
    all_plot_code = user_profile.all_plot_code
    return render(request, 'verify/profile.html', {
        'public_key': public_key_pem,
        'user_id': user_id,
        'all_plot_code': all_plot_code 
    })


def save(request):
    user = User.objects.get(id=4)
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


    user_profile = UserProfile.objects.create(user=user, public_key=public_key_pem_str)

    return render(request, 'verify/admin_pk.html', {
                'username': user.username,
                'private_key': private_key_pem.decode(),
                'public_key': public_key_pem.decode(),
            })