from django.shortcuts import render


from django.http import HttpResponse
import datetime



def test(request):
    wut="hello world"
    return HttpResponse(wut)