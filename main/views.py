from django.http import HttpResponse
from cryptography.hazmat.primitives import serialization, hashes
from users.models import UserProfile
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cryptography.hazmat.primitives.asymmetric import padding, rsa ,dsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from .models import Transaction, Block, LandList
import hashlib
from django.contrib.admin.views.decorators import user_passes_test
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils


def home(request):
    blocks = Block.objects.all().order_by('-id') 

    paginator = Paginator(blocks, 5)  
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)  

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'main/home.html', context)



def about(request):
    ### mah sal7a
    return render(request,'main/about.html',{'title':"about101"})




@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_land(request):
    if request.method == 'POST':
        plot_code = request.POST.get('plot_code')
        note = request.POST.get('note')
        sender_username = request.user.username
        receiver_username = request.POST.get('receiver_username')
        private_key_pem = request.POST.get('private_key')

        if not plot_code.isdigit() :
             return render(request, 'main/add_land.html', {'message':"Veuillez entrer uniquement des chiffres"})
        # create_genesis_block()
        last_block = Block.objects.last()
        if last_block is  None:
            create_genesis_block()

        # 5aras if the receiver  already exists or not ??!
        receiver = User.objects.filter(username=receiver_username).first()
        if receiver is None:
            return render(request, 'main/add_land.html', {'message': 'Le nom d\'utilisateur du destinataire n\'existe pas'})



        ### mzal lak t5ares can private_key_pem mlk l sender_username or not 


        #############  private_key_pem and public key sloa7tou done 


        data = f'{plot_code} {sender_username} {receiver_username}'
        try:
           
            signature = generate_signature(data, private_key_pem)
        except Exception as e:
            return render(request, 'main/add_land.html', {'message': 'La génération de signature a échoué'})


        ts=verify_signature(sender_username ,data ,signature)
        if ts == False:
            return render(request, 'main/add_land.html', {'message': 'La génération de signature a échoué 101'})




        # Check if the land already exists in LandList
        land_list = LandList.objects.filter(plot_code=plot_code).first()

        if land_list is not None:
            return render(request, 'main/add_land.html', {'message': 'Le terrain ID existe déjà'})

        # Create LandList entry for the new plot_code
        land_list = LandList.objects.create(plot_code=int(plot_code), note=note)


        try:
            
            receiver_user = User.objects.get(username=receiver_username)
            
        except Exception as e:
            return render(request, 'main/add_land.html', {'message': 'Le nom d\'utilisateur du destinataire n\'existe pas'})
       
        user_profile =UserProfile.objects.get(user=receiver_user)
        user_profile.all_plot_code.append(int(plot_code))
        user_profile.save()


       
        transaction = Transaction.objects.create(
            plot_code=plot_code,
            sender_username=sender_username,
            receiver_username=receiver_username,
            signature=signature
        )

        # Check if there are at least 5 transactions in the collection
        if Transaction.objects.count() % 5 == 0:
           
            transactions = Transaction.objects.order_by('-id')[:5][::-1]

            last_block = Block.objects.last()

           

            block = Block.objects.create(prev_hash=last_block.current_hash)

            # Convert transactions to a list of dictionaries
            transaction_dicts = []
            for t in transactions:
                transaction_dict = {
                    'id': t.id,
                    'plot_code': t.plot_code,
                    'sender_username': t.sender_username,
                    'receiver_username': t.receiver_username,
                    'signature': t.signature
                }
                transaction_dicts.append(transaction_dict)

            data_to_hash = {
                'prev_hash': block.prev_hash,
                'transactions': transaction_dicts
            }
            data_hash = hashlib.sha256(str(data_to_hash).encode()).hexdigest()


            block.current_hash = data_hash
            block.transactions = transaction_dicts
            block.save()



        return render(request, 'main/add_land.html', {'message': 'terrain Ajouté avec succès'})

    return render(request, 'main/add_land.html')


@login_required
def send_land(request):
    if request.method == 'POST':
        plot_code = request.POST.get('plot_code')
        sender_username = request.user.username
        receiver_username = request.POST.get('receiver_username')
        private_key_pem = request.POST.get('private_key')


        if not plot_code.isdigit() :
            return render(request, 'main/send_land.html', {'message':"Veuillez entrer uniquement des chiffres"})
        # create_genesis_block()
        last_block = Block.objects.last()
        if last_block is None:
            create_genesis_block()

        sender_profile = UserProfile.objects.filter(user=request.user).first()
        all_plot_code = sender_profile.all_plot_code
        if int(plot_code) not in all_plot_code:
            return render(request, 'main/send_land.html', {'message': 'Vous n\'avez pas le terrain ID spécifié'})




        data = f'{plot_code} {sender_username} {receiver_username}'
        try:

            signature = generate_signature(data, private_key_pem)
        except Exception as e:
            return render(request, 'main/send_land.html', {'message': 'La génération de signature a échoué'})

        ts=verify_signature(sender_username ,data ,signature)
        if ts == False:
            return render(request, 'main/add_land.html', {'message': 'La génération de signature a échoué 101'})



        try:
            
            receiver_user = User.objects.get(username=receiver_username)
            
        except Exception as e:
            return render(request, 'main/add_land.html', {'message': 'Le nom d\'utilisateur du destinataire n\'existe pas '})


        user_profile= UserProfile.objects.get(user=receiver_user)
        user_profile.all_plot_code.append(int(plot_code))
        user_profile.save()

        transaction = Transaction.objects.create(
            plot_code=plot_code,
            sender_username=sender_username,
            receiver_username=receiver_username,
            signature=signature
        )

        # Remove the plot code from the all_plot_code list
        all_plot_code.remove(int(plot_code))


        sender_profile.all_plot_code = all_plot_code
        sender_profile.save()




        if Transaction.objects.count() % 5 == 0:

            transactions = Transaction.objects.order_by('-id')[:5][::-1]

            last_block = Block.objects.last()

            block = Block.objects.create(prev_hash=last_block.current_hash)

            transaction_dicts = []
            for t in transactions:
                transaction_dict = {
                    'id': t.id,
                    'plot_code': t.plot_code,
                    'sender_username': t.sender_username,
                    'receiver_username': t.receiver_username,
                    'signature': t.signature
                }
                transaction_dicts.append(transaction_dict)

            data_to_hash = {
                'prev_hash': block.prev_hash,
                'transactions': transaction_dicts
            }
            data_hash = hashlib.sha256(str(data_to_hash).encode()).hexdigest()

            block.current_hash = data_hash
            block.transactions = transaction_dicts
            block.save()



        return render(request, 'main/send_land.html', {'message': 'terrain envoyé avec succès'})

    return render(request, 'main/send_land.html')


def block_search(request):
    if request.method == 'POST':
        block_id = request.POST.get('id')
        if not block_id.isdigit() :
             return render(request, 'main/block.html', {'message':"Veuillez entrer uniquement des chiffres"})

        block = Block.objects.filter(id=int(block_id)).first()

        if block is None :
            return render(request, 'main/block.html',{'message': 'Bloc introuvable dans la blockchain'} )

        context = {
            "block_id":block_id,
            'prev_hash':block.prev_hash,
            'current_hash': block.current_hash,
            'transactions':block.transactions,
        }
        return render(request, 'main/block.html', context)

    return render(request, 'main/block.html')



def plot_history(request):
    if request.method == 'POST':
        plot_code = request.POST.get('plot_code')
        if not plot_code.isdigit() :
            return render(request, 'main/plot_history.html', {'message':"Veuillez entrer uniquement des chiffres"})

        land_list = LandList.objects.filter(plot_code=plot_code).first()
        if land_list is None:
            return render(request, 'main/plot_history.html', {'message': 'le terrain ID n\'existe pas'})

        plot_code = land_list.plot_code
        note = land_list.note

        transactions = Transaction.objects.filter(plot_code=plot_code).order_by('id')[::-1]

        context = {
            'plot_code': plot_code,
            'note': note,
            'transactions': transactions,
        }

        return render(request, 'main/plot_history.html', context)

    return render(request, 'main/plot_history.html')

def create_genesis_block():

    transaction_dict = {
        'id': 0,
        'plot_code': 0,
        'sender_username': 'None',
        'receiver_username': 'None',
        'signature':'None'
    }
    data_to_hash = {
                'prev_hash': 'Aucun',
                'transactions': transaction_dicts
            }
    data_hash = hashlib.sha256(str(data_to_hash).encode()).hexdigest()

    genesis_block = Block.objects.create(prev_hash='Aucun', current_hash=data_hash)



    genesis_block.transactions = [transaction_dict]
    genesis_block.save()

    return genesis_block

def generate_signature(data ,private_key_pem):
    private_key_pem=private_key_pem
    private_key =load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )

    signature = private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    return signature.hex()

def verify_signature(sender_username ,data ,signature):
    
    user_to_v = User.objects.get(username=sender_username)
    
    signature = bytes.fromhex(signature)

    user_profile = UserProfile.objects.get(user_id=user_to_v.id)
    public_key_pem = user_profile.public_key.encode()  # 7awelou chor  bytes

    # Load the public key from PEM format
    public_key = load_pem_public_key(public_key_pem)

    try:
        # Verify the signature using the public key  viiiiih 5a6a2 ma yvasel binathoum
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


    return verification_result






