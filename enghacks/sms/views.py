from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def sms_response(request):
    return HttpResponse("Hello, world.")
