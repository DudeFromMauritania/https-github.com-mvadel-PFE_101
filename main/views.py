from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

posts=[
    {
        'name':"med",
        'age' :"25"
    },
    {
        'name':"sss",
        'age' :"5"
    },
    {
        'name':"frs",
        'age' :"2"
    }
]

def home(request):
    context={
        'posts':posts
    }
    return render(request,'main/home.html',context)


def about(request):
    return render(request,'main/about.html',{'title':"about101"})