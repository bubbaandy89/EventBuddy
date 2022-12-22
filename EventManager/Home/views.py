import datetime

from django.conf import settings  # noqa: F401
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import URLValidator
from django.shortcuts import redirect, render
from django.template import Context, Template  # noqa: F401
from django.utils import timezone

from Home.forms import NewEventForm
from Home.models import Event, Participant
from users.models import Profile

# from twilio.rest import Client

partlst = []  # global list for displaying participants for a particular event on home page
flag = 0  # boolean variable for deciding whether to display participants or not on home page


def get_caller_username(request) -> str:
    username: str = ""
    if request.user.is_authenticated:
        username = request.user.username
    return username


# Create your views here.
@login_required
def events_home(request, uid=""):
    if not uid:
        uid = request.user.id
    # use global variant of flag instead of creating local variant of it
    global flag
    elst = []
    eidlst = []
    expired_eventid_lst = []

    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()

    # for displaying only three items on user's home page
    i = 1

    # if flag is set to 0 then don't display anything else display related information
    if flag == 0:
        templst = []
    else:
        templst = partlst

    # assign additional info to display on webpage
    for all_users in Profile.objects.all():
        if all_users.user.username == get_caller_username(request):
            uname = all_users.user.first_name
            umail = all_users.user.email
        else:
            uname = ""
            umail = ""

    # automatically remove events from the database which are ongoing or are finished
    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()

    # simultaneously remove the participants of these events from participant database
    for ids in expired_eventid_lst:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()

    # collect the events in which user has participated or is the host
    for all_participants in Participant.objects.all():
        if all_participants.participant_email == umail:
            eidlst.append(all_participants.pevent_id)
    for all_events in Event.objects.all():
        if i <= 3:
            if all_events.host_email == umail:
                elst.append(all_events)
                i += 1
        else:
            break
    for entry in eidlst:
        for all_events in Event.objects.all():
            if i <= 3:
                if all_events.event_id == entry:
                    elst.append(all_events)
                    i += 1
            else:
                break

    # sorting the list according to start dates
    elst.sort(key=lambda eve: eve.event_start)
    flag = 0
    return render(
        request,
        "home.html",
        {"uname": uname, "eventlst": elst, "uid": uid, "umail": umail, "partlst": templst},
    )


@login_required
def newevent(request, uid=""):
    form = NewEventForm(request.POST)
    if not uid:
        uid = request.user.id
    if request.method == "POST":
        if not request.user.is_staff:
            raise PermissionDenied()

        name = request.POST["ename"]
        event_start_date = request.POST["estartd"]
        event_start_time = request.POST["estartt"]
        event_end_date = request.POST["eendd"]
        event_end_time = request.POST["eendt"]
        regendd = request.POST["regendd"]
        regendt = request.POST["regendt"]
        poslink = request.POST["plink"]
        for all_users in Profile.objects.all():
            if all_users.user.username == get_caller_username(request):
                uname = all_users.user.first_name
                umail = all_users.user.email
            else:
                uname = ""
                umail = ""
        if (
            not name
            or not event_start_date
            or not event_start_time
            or not event_end_date
            or not event_end_time
            or not regendd
            or not regendt
            or not poslink
        ):
            return render(
                request,
                "createevent.html",
                {
                    "message": "Please fill out all the fields.",
                    "uid": request.user.id,
                    "form": form,
                },
            )
        else:
            # separating out data to create datetime instance
            es = datetime.datetime(
                int(event_start_date[:4]),
                int(event_start_date[5:7]),
                int(event_start_date[8:]),
                int(event_start_time[:2]),
                int(event_start_time[3:]),
            )
            ee = datetime.datetime(
                int(event_end_date[:4]),
                int(event_end_date[5:7]),
                int(event_end_date[8:]),
                int(event_end_time[:2]),
                int(event_end_time[3:]),
            )
            regdate = datetime.datetime(
                int(regendd[:4]),
                int(regendd[5:7]),
                int(regendd[8:]),
                int(regendt[:2]),
                int(regendt[3:]),
            )
            edes = request.POST["edes"]

            # validation logic for event dates and times
            dtnow = datetime.datetime.now().strftime("%Y-%m-%d")
            timenow = datetime.datetime.now().strftime("%H:%M")

            if event_end_date < dtnow or event_end_date < dtnow:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start date or end date can't be before current date",
                        "uid": request.user.id,
                        "form": form,
                    },
                )
            if event_start_date > event_end_date:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start date must be before end date",
                        "uid": request.user.id,
                        "form": form,
                    },
                )
            if event_start_date == dtnow and (
                event_start_time < timenow or event_end_time < timenow
            ):
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start time must be after current time for current date.",
                        "uid": uid,
                    },
                )
            if event_start_time > event_end_time:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Start time must be before end time.",
                        "uid": request.user.id,
                        "form": form,
                    },
                )
            if regendd > event_start_date or regendd < dtnow:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Deadline date must be before end date or after current date.",
                        "uid": uid,
                    },
                )
            if regendd == dtnow and regendt <= timenow:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Deadline time must be after current time.",
                        "uid": request.user.id,
                        "form": form,
                    },
                )

            try:
                URLValidator()(poslink)
            except ValidationError:
                return render(
                    request,
                    "createevent.html",
                    {"message": "Please enter valid URL.", "uid": request.user.id, "form": form},
                )

            # saving data in database if validation is true
            for all_events in Event.objects.all():
                if name == all_events.event_name and (
                    es == all_events.event_start or ee == all_events.event_end
                ):
                    return render(
                        request,
                        "createevent.html",
                        {
                            "message": "Event with same credentials already exists.",
                            "uid": request.user.id,
                            "form": form,
                        },
                    )
            # temp = Event(
            #     event_name=name,
            #     event_start=es,
            #     event_end=ee,
            #     host_email=umail,
            #     host_name=uname,
            #     event_description=edes,
            #     registration_deadline=regdate,
            #     event_poster=poslink,
            # )
            # temp.save()

            if form.is_valid():
                form.save()
                # redirect to home page once event is created
                return redirect(events_home, uid=request.user.id)
            else:
                return render(
                    request,
                    "createevent.html",
                    {
                        "message": "Event form failed validation.",
                        "uid": request.user.id,
                        "form": form,
                    },
                )
    else:
        # if uid != "" and uid not in request.session:
        #     raise PermissionDenied()
        # if uid != "" and request.session[uid] != uid:
        #     raise PermissionDenied()
        return render(request, "createevent.html", {"uid": request.user.id, "form": form})


def allevent(request, uid=""):
    if not uid:
        uid = request.user.id
    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()
    expired_eventid_lst = []
    elst = []
    eidlst = []
    for all_users in Profile.objects.all():
        if all_users.user.username == get_caller_username(request):
            uname = all_users.user.first_name
            umail = all_users.user.email
        else:
            uname = ""
            umail = ""

    # automatically remove events from the database which are ongoing or are finished and their
    # corresponding participants
    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()

    # simultaneously remove the participants of these events from participant database
    for ids in expired_eventid_lst:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()

    # collect the events in which user has participated or is the host
    for all_participants in Participant.objects.all():
        if all_participants.participant_email == umail:
            eidlst.append(all_participants.pevent_id)
    for all_events in Event.objects.all():
        if all_events.host_email == umail:
            elst.append(all_events)
    for entry in eidlst:
        for all_events in Event.objects.all():
            if all_events.event_id == entry:
                elst.append(all_events)

    # sort the list according to start dates
    elst.sort(key=lambda eve: eve.event_start)
    return render(
        request, "allevents.html", {"uname": uname, "alleventlst": elst, "uid": uid, "umail": umail}
    )


def deleteevent(request, uid="", eid=""):
    if not uid:
        uid = request.user.id
    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()

    # find the event which has to be deleted in database and delete it
    for all_events in Event.objects.all():
        if all_events.event_id == eid:
            all_events.delete()

    # also delete the participants of that corresponding event
    for all_participants in Participant.objects.all():
        if all_participants.pevent_id == eid:
            all_participants.delete()
    return redirect(events_home, uid=uid)


def explore(request, uid=""):
    if not uid:
        uid = request.user.id
    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()
    exp = []
    expired_eventid_lst = []
    for all_users in Profile.objects.all():
        if all_users.user.username == get_caller_username(request):
            uname = all_users.user.first_name
            umail = all_users.user.email
    if uid == "":
        uname = ""
        umail = ""
    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()
    for ids in expired_eventid_lst:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()
    for all_events in Event.objects.all():
        exp.append(all_events)
    exp.sort(key=lambda eve: eve.event_start)
    return render(
        request,
        "explorepage.html",
        {"explst": exp, "uid": uid, "uname": uname, "umail": umail, "curr_dt": curr_dt},
    )


def participate(request, uid="", eid=""):
    if not uid:
        uid = request.user.id
    if request.method == "POST":
        # if uid != "" and uid not in request.session:
        #     raise PermissionDenied()
        # if uid != "" and request.session[uid] != uid:
        #     raise PermissionDenied()
        # extracting additional info from database
        for all_users in Profile.objects.all():
            if all_users.user.username == get_caller_username(request):
                uname = all_users.user.first_name
                umail = all_users.user.email
        if uid == "":
            uname = ""
            umail = ""
        cono = request.POST["cono"]
        reg = request.POST.get("grpreg")
        if reg == "group":
            isGrp = True
            nopar = request.POST["nopar"]
        else:
            isGrp = False
            nopar = 1
        if not cono or not reg or not nopar:
            return render(
                request,
                "participantform.html",
                {"uid": uid, "eid": eid, "message": "Please fill out all the fields."},
            )
        if len(cono) != 10:
            return render(
                request,
                "participantform.html",
                {"uid": uid, "eid": eid, "message": "Please enter valid contact number."},
            )

        # logic for checking whether the user has participated in event or not
        for all_participants in Participant.objects.all():
            if all_participants.participant_email == umail and all_participants.pevent_id == eid:
                return render(
                    request,
                    "participantform.html",
                    {
                        "uid": uid,
                        "eid": eid,
                        "message": "You have already participated in this event.",
                    },
                )

        # save the participant data to the database if validation is true
        curr_time = timezone.now()
        for all_events in Event.objects.all():
            if all_events.event_id == eid:
                if all_events.registration_deadline < curr_time:
                    return render(
                        request,
                        "participantform.html",
                        {
                            "uid": uid,
                            "eid": eid,
                            "message": "The participation deadline has passed.",
                        },
                    )
                temp = Participant(
                    pevent_id=eid,
                    participant_email=umail,
                    participant_contactno=cono,
                    participant_name=uname,
                    group_registration=isGrp,
                    no_of_members=nopar,
                )
                try:
                    temp.save()

                    # code to send the mail to user upon participating. Uncomment the lines below
                    # to enable this feature.
                    # Set the variables EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to the email ID and
                    # corresponding password in settings.py
                    # subject = 'New Participation in EventBuddy'
                    # mailtemplate = Template(("Hello {{sname}},\n\nYou recently participated in"
                    # " the event with following credentials on EventBuddy:\nName of event: "
                    # "{{ename}}\nStart of event: {{estart}}\nEnd of event: {{eend}}\n"
                    # "Host: {{host}}\nEvent Description: {{edest}}\n\nRegards,\nEventBuddy Team"))
                    # context = Context(
                    #   {
                    #       'sname':uname,
                    #       'ename':all_events.event_name,
                    #       'estart':all_events.event_start,
                    #       'eend':all_events.event_end,
                    #       'host':all_events.host_name,
                    #       'edest':all_events.event_description
                    #   }
                    # )
                    # mailbody = mailtemplate.render(context)
                    # email_from = settings.EMAIL_HOST_USER
                    # recipients = [umail]
                    # try:
                    #    send_mail(subject, mailbody, email_from, recipients)
                    # except:
                    #    print('Mail not sent.')
                    # -----Uncomment tii here----

                    # code for sending phone messages to user upon participating using Twilio API.
                    # Uncomment the lines below to enable this feature.
                    # Set the variables TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN and TWILIO_NUMBER to
                    # your choice in settings.py.
                    # messagetemplate = Template(("You recently participated in the event with"
                    # following credentials on EventBuddy:\nName of event: {{ename}}\nStart of"
                    # " event: {{estart}}\nEnd of event: {{eend}}\n"
                    # "Host: {{host}}\nEvent Description: {{edest}}"))
                    # context = Context(
                    #   {
                    #       'ename':all_events.event_name,
                    #       'estart':all_events.event_start,
                    #       'eend':all_events.event_end,
                    #       'host':all_events.host_name,
                    #       'edest':all_events.event_description
                    #   }
                    # )
                    # message_body = messagetemplate.render(context)
                    # cono_modified = '+91' + cono
                    # try:
                    #    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    #    client.messages.create(to=cono_modified,from_=settings.TWILIO_NUMBER,body=message_body)
                    # except:
                    #    print("Message couldn\'t be sent")
                    # ----Uncomment till here-----

                except ValueError:
                    return render(
                        request,
                        "participantform.html",
                        {
                            "uid": uid,
                            "eid": eid,
                            "message": "Contact Number should only consist of numbers.",
                        },
                    )
                return redirect(explore, uid=uid)
    else:
        # if uid != "" and uid not in request.session:
        #     raise PermissionDenied()
        # if uid != "" and request.session[uid] != uid:
        #     raise PermissionDenied()
        return render(request, "participantform.html", {"uid": uid, "eid": eid})


def viewprofile(request, uid=""):
    if not uid:
        uid = request.user.id
    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()
    for all_users in Profile.objects.all():
        if all_users.user.username == get_caller_username(request):
            uname = all_users.user.first_name
            umail = all_users.user.email
        else:
            uname = ""
            umail = ""
    return render(request, "profilepage.html", {"uid": uid, "uname": uname, "umail": umail})


def viewparticipant(request, uid="", eid=""):
    if not uid:
        uid = request.user.id
    # if uid != "" and uid not in request.session:
    #     raise PermissionDenied()
    # if uid != "" and request.session[uid] != uid:
    #     raise PermissionDenied()
    # clear the list everytime the user requests for participant information
    partlst.clear()
    global flag
    flag = 1
    for all_participants in Participant.objects.all():
        if all_participants.pevent_id == eid:
            partlst.append(all_participants)
    return redirect(events_home, uid=uid)
