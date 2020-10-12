from django.urls import path, include
from django.conf.urls import url
from .api import SignUP, Login, UserProjects, UserProjectID, TicketView, ListTicketView, LogOut, UsersView, UserView
from rest_framework.authtoken.views import obtain_auth_token
from .views import TicketForm

urlpatterns = [
    # path('', TicketForm),
    url(r'^reportError/(?P<ticket_form_key>\w+)/$', TicketForm, name='ticket_form'),
    path('api/user', UsersView.as_view(), name='all_users'),     # Just for testing purpose
    url(r'^api/user/(?P<user_id>\d+)/$', UserView.as_view(), name='user_details'),   # Done
    path('api/signup', SignUP.as_view(), name='create_user'),   # Done
    path('api/login', Login.as_view(), name='login_user'),  # Done
    path('api/logout', LogOut.as_view(), name='logout_user'),   # Done
    path('api/auth', obtain_auth_token, name='obtain_token'),   # Done
    path('api/user/project', UserProjects.as_view(), name='get_projects'),  # Done
    url(r'^api/user/project/(?P<project_id>\d+)/$', UserProjectID.as_view(), name='get_project_with_id'),   # Done
    url(r'^api/user/project/(?P<project_id>\d+)/ticket/$', TicketView.as_view(), name='get_project_tickets'),   # Done
    url(r'^api/user/project/(?P<project_id>\d+)/ticket/(?P<ticket_id>\d+)/$', ListTicketView.as_view(),
        name='get_project_ticket_with_id'),
]