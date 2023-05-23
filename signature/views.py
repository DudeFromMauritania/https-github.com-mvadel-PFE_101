from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

@login_required
def generate_signature(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        private_key_pem = request.POST.get('private_key')

        # Load the private key from PEM format
        private_key = load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )

        # Sign the message with the private key
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

