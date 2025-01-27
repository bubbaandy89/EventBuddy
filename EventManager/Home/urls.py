from django.urls import path

from Home import views

app_name = "events"

urlpatterns = [
    path("", views.events_home, name="events-root-home"),
    path("<str:uid>home", views.events_home, name="events-home"),
    path("<str:uid>home/newevent", views.newevent, name="newevent"),
    path("<str:uid>home/allevent", views.allevent, name="allevent"),
    path("<str:uid>home/delevent<str:eid>", views.deleteevent, name="deleteevent"),
    path("<str:uid>home/explore", views.explore, name="explore"),
    path("explore", views.explore, name="explore"),
    path("<str:uid>home/participantform<str:eid>", views.participate, name="participate"),
    path("<str:uid>home/profile", views.viewprofile, name="viewprofile"),
    path("<str:uid>home/viewpart<str:eid>", views.viewparticipant, name="viewparticipant"),
]
