from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("activate/<str:uidb64>/<str:token>/", views.activate, name="activate"),
    path("add/<int:deck_id>",views.add,name="add"),
    path("decks",views.decks,name="decks"),
    path("review/<int:deck_id>",views.review,name="review"),
    path("search",views.search,name="search"),
    path("logout",views.logout_view, name="logout"),
    path("edit/<int:deck_id>",views.edit,name="edit"),
    path("delete-card/<int:card_id>",views.delete_card,name="delete-card"),
    path("change/<int:card_id>", views.change, name="change"),
    path("courses",views.courses,name="courses"),
    path("decks/course/<int:course_id>",views.decks_course,name="deck-course"),
    path("add-deck-to-course/<int:course_id>",views.add_deck_to_course, name="add-deck-to-course"),
    path("delete_deck/<int:deck_id>",views.delete_deck,name="delete-deck"),
    path("edit-public/<int:deck_id>",views.edit_public,name="edit-public"),
]