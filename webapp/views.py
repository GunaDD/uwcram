from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import *
import random
import json
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponseForbidden

# Create your views here.

def index(request):
    messages_to_display = messages.get_messages(request)

    return render(request, 'webapp/index.html', {
        "messages":messages_to_display
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
    
        if user is not None:
            login(request, user)
            return render(request, 'webapp/index.html')
        else:
            print("NOT FOUND ACCOUNT !")

    return render(request, 'webapp/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'webapp/index.html')

def register(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print("its valid")
            user = form.save(commit = False)
            user.is_active = False
            user.save()
            
            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            message = render_to_string("webapp/account_activation_email.html",{
                "user": user,
                "domain":current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user)
            })
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return redirect("index")
        else:
            print(form.errors)
    return render(request, 'webapp/register.html')

def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        return redirect(reverse("login"))
    else:
        messages.error(request, "Activation link is invalid or expired")
        return redirect("index")

@login_required
def add(request, deck_id):
    if request.method == "POST":   
        deck = Deck.objects.get(id=deck_id)
        writer = request.user
        front_card = request.POST["front_card"]
        back_card = request.POST["back_card"]
        
        card = Card(deck=deck,writer=writer, front=front_card, back=back_card)
        card.save()
        return HttpResponseRedirect(reverse("edit", args=[deck_id]))
        
    deck = Deck.objects.get(id=deck_id)
    return render(request, 'webapp/add.html', {
        "deck": deck
    })

    
@login_required
def decks(request):
    if request.method == "POST":    
        deck_name = request.POST["deck_name"]
        user = request.user
        course_id = request.POST["course"]
        public = bool(request.POST["public"])

        course = Course.objects.get(id=course_id)
        deck = Deck(name=deck_name, writer=user, course=course, public=public)
        deck.save()

        return HttpResponseRedirect(reverse("decks"))

    user = request.user
    decks = []
    for deck in Deck.objects.all():
        if deck.writer == user:
            decks.append(deck)

    decks.reverse()

    return render(request, 'webapp/decks.html', {
        "decks": decks,
        "courses": Course.objects.all()
    })

def review(request, deck_id):
    deck = Deck.objects.get(id=deck_id)
    user = request.user

    if user != deck.writer and not deck.public: 
        return render(request, 'webapp/review.html', {
            "access":False,
        })

    lst = list(deck.cards.all())
    dictionary = []

    for card in lst:
        dictionary.append({
            'id': card.id,
            'front': card.front,
            'back': card.back
        })

    random.shuffle(dictionary)

    dictionary.append({
        'id': 0,
        'front': 'Congratulations, you have completed the deck!',
        'back': 'Congratulations, you have completed the deck!',
    })

    print("hi world")

    return render(request, 'webapp/review.html', {
        "cards": json.dumps(dictionary)
    })

def search(request):
    if request.method == "POST":
        list = []
        deck_name = request.POST["text"]
        for deck in Deck.objects.filter(public=True):
            if deck.name.find(deck_name) != -1:
                list.append(deck)

        return render(request, 'webapp/search.html', {
            "decks":list,
        })
    
    return render(request, 'webapp/search.html', {
        "decks":Deck.objects.filter(public=True)
    })

@login_required
def edit(request, deck_id):
    deck = Deck.objects.get(id=deck_id)

    if deck.writer != request.user:
        return HttpResponseForbidden("You are not authorized to edit this deck.")
    
    return render(request, 'webapp/edit.html', {
        "cards": deck.cards.all(),
        "deck": deck
    })

def delete_card(request, card_id):
    card = Card.objects.get(id=card_id)
    deck_id = card.deck.id
    card.delete()
    return HttpResponseRedirect(reverse("edit", args=[deck_id]))


def change(request, card_id):
    if request.method == "POST":
        front_card = request.POST["front_card"]
        back_card = request.POST["back_card"]
        
        card = Card.objects.get(id=card_id)
        deck_id = card.deck.id
        card.front = front_card
        card.back = back_card
        card.save()
        return HttpResponseRedirect(reverse("edit", args=[deck_id]))

    card = Card.objects.get(id=card_id)
    deck = card.deck
    return render(request, 'webapp/change.html', {
        "card":card,
        "deck":deck,
    })


def courses(request):
    if request.method == "POST":
        subject = request.POST["subject"].upper()
        catalog_number = request.POST["catalog_number"].upper()
        result = []
        for course in Course.objects.all():
            if subject in course.subject and catalog_number in course.catalog_number:
                result.append(course)

        paginator = Paginator(result, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, 'webapp/courses.html', {
            "page_obj": page_obj,
        })
    
    all_courses = Course.objects.all()
    paginator = Paginator(all_courses, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'webapp/courses.html', {
        "page_obj": page_obj
    })


def decks_course(request, course_id):
    course = Course.objects.get(id=course_id)
    result = []
    for deck in Deck.objects.all():
        if deck.course == course and (deck.public or request.user == deck.writer):
            result.append(deck)

    return render(request, 'webapp/search.html', {
        "decks":result,
    })

def add_deck_to_course(request, course_id):
    user = request.user
    decks = []
    for deck in Deck.objects.all():
        if deck.writer == user:
            decks.append(deck)

    decks.reverse()

    course = Course.objects.get(id=course_id)

    return render(request, 'webapp/decks.html', {
        "decks": decks,
        "courses": Course.objects.all(),
        "selected_course": course.id,
    })
    

@login_required
def delete_deck(request, deck_id):
    deck = Deck.objects.get(id=deck_id)
    deck.delete()
    return HttpResponseRedirect(reverse("decks"))


def edit_public(request, deck_id):
    deck = Deck.objects.get(id=deck_id)
    deck.public ^= 1
    deck.save()
    return HttpResponseRedirect(reverse("edit", args=[deck_id]))

