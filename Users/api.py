from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Projects, ProjectUserRelation, Tickets
from .serializers import UserSerializer, ProjectSerializer, TicketSerializer
from rest_framework.exceptions import APIException, PermissionDenied, NotFound
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from uuid import uuid4


TICKETS_SORTED_BY = {
    'priority': ('Priority', ['Low', 'Medium', 'High']),
    'status': ('Status', ['Open', 'Closed']),
    'type': ('Type', ['Feature/Request', 'Bug/Error', 'Others'])
}


def validate_ticket(data):
    title = data.get('title', None)
    description = data.get('description', None)
    priority = {v: k for k, v in Tickets.PRIORITY_CHOICES}.get(data.get('priority', None))
    status = {v: k for k, v in Tickets.STATUS_CHOICES}.get(data.get('status', None))
    type = {v: k for k, v in Tickets.TICKET_TYPE_CHOICES}.get(data.get('type', None))

    if title and description and priority and status and type:
        return True
    return False


def user_exists(user_id):
    try:
        user = User.objects.get(id=user_id)
        return True
    except User.DoesNotExist:
        return False


def isAdmin(user_id, project_id):
    if user_exists(user_id):
        try:
            relation = ProjectUserRelation.objects.get(user_id=user_id, project_id=project_id)
            return relation.user_role == "Admin"
        except ProjectUserRelation.DoesNotExist:
            raise NotFound("Data you are looking is not found !!")
    raise PermissionDenied("Permission Denied")


class SignUP(APIView):
    def post(self, request):

        # set username to be a random 30 digit id
        _mutableflag = request.data._mutable
        request.data._mutable = True
        request.data['username'] = uuid4().hex[:30]
        request.data._mutable = _mutableflag

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        if email is None or password is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            if user.check_password(raw_password=password):
                try:
                    Token.objects.get(user=user)
                except Token.DoesNotExist:
                    # means was logged out
                    # so create Token
                    Token.objects.create(user=user)
                return Response({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': email
                }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class LogOut(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        return Response({}, status=status.HTTP_200_OK)


# /api/user
# Only For Website Admin
class UsersView(APIView):
    def get(self, request):
        if request.user.is_superuser:
            users = User.objects.all()
            result = []
            for user in users:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                })
            return Response(result, status=status.HTTP_200_OK)
        return Response({"msg": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)


# /api/user/<user_id>
class UserView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"msg": "User Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)


# /api/user/project
# Returns all projects linked to a user
class UserProjects(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        try:
            # find all project with <user_id> in the M-N Relation Table
            projects = ProjectUserRelation.objects.filter(user_id=user_id)

            result = []
            for project in projects:
                # Find all projects with Project Id as found above in variable projects
                result.append(Projects.objects.get(id=str(project.project_id)))

            # return all project details linked to this user
            serializer = ProjectSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Projects.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except ProjectUserRelation.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        user_id = request.user.id
        # checking if project data is valid
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = Projects.objects.create(name=serializer.data['name'], description=serializer.data['description'],
                                              ticket_form_key=uuid4().hex[:10])
            project.project_users.add(request.user)
            relation = ProjectUserRelation.objects.get(user_id=user_id, project_id=project.id)
            # change this default Admin value for all users
            relation.user_role = {v: k for k, v in ProjectUserRelation.ROLE_CHOICES}.get('Admin')
            relation.save()
            return Response({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'ticket_form_key': project.ticket_form_key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# /api/user/project/<project_id>
# get Specific Project with project id
class UserProjectID(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user_id = request.user.id

        try:
            # find the project with <project_id>
            project = Projects.objects.get(id=project_id)

            # check if this project is assigned to this user or not
            assigned = ProjectUserRelation.objects.get(user_id=user_id, project_id=project_id)
            if assigned:
                serializer = ProjectSerializer(project)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_403_FORBIDDEN)
        except Projects.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except ProjectUserRelation.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, project_id):
        # Only Admin can Update the Project
        user_id = request.user.id

        try:
            project = Projects.objects.get(id=project_id)
            isadmin = isAdmin(user_id, project_id)
            if isadmin == 403 or isadmin is False:
                return Response({}, status=status.HTTP_403_FORBIDDEN)
            elif isadmin == 204:
                return Response({}, status=status.HTTP_204_NO_CONTENT)

            # checking if request.data has COMPULSORY Parameters or not
            _mutable_flag = request.data._mutable
            request.data._mutable = True
            if 'name' not in request.data:
                request.data['name'] = project.name
            if 'description' not in request.data:
                request.data['description'] = project.description
            request.data._mutable = _mutable_flag

            serializer = ProjectSerializer(project, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Projects.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        user_id = request.user.id
        try:
            project = Projects.objects.get(id=project_id)
            isadmin = isAdmin(user_id, project_id)
            if isadmin == 403 or isadmin is False:
                return Response({}, status=status.HTTP_403_FORBIDDEN)
            elif isadmin == 204:
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            project.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Projects.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


# /api/user/project/<project_id>/ticket
# 3rd party user/admin can also open a ticket
class TicketView(APIView):
    def get(self, request, project_id):
        try:
            token = request.META['HTTP_AUTHORIZATION'].split()[1]
            user_id = Token.objects.get(key=token).user.id

            # get headers with get request

            count = self.request.query_params.get('count', False)
            by = self.request.query_params.get('by', None)
            sorted_by = TICKETS_SORTED_BY.get(by, None)

            # check if user is Admin or Developer
            admin = ProjectUserRelation.objects.get(user_id=user_id, project_id=project_id)
            admin = True if admin.user_role == "Admin" else False

            # if admin show all tickets, else show tickets assigned to the developer only
            if admin:
                tickets = Tickets.objects.filter(project=project_id)
                if count is True and sorted_by:
                    pass
                serializer = TicketSerializer(tickets, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # if developer -> show only those tickets to which developer is assigned
                # show only those tickets, which are assigned to this developer only for this project
                tickets = Tickets.objects.filter(user_id=user_id, project_id=project_id)
                serializer = TicketSerializer(tickets, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except KeyError:
            return Response({"msg": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        except Token.DoesNotExist:
            return Response({"msg": "Please Login/Register"}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"msg": "User does not exist"}, status=status.HTTP_403_FORBIDDEN)
        except ProjectUserRelation.DoesNotExist:
            return Response({"msg": "No Project Exists"}, status=status.HTTP_204_NO_CONTENT)
        except Tickets.DoesNotExist:
            return Response({"msg": "No Ticket Exists"}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, project_id):
        # Find the project in which ticket need to be opened
        try:
            project = Projects.objects.get(id=project_id)
        except Projects.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        try:
            # if user is Admin then only he can open a Proper Ticket, else others can only write title and description
            # for the ticket
            user_id = request.user.id
            user = User.objects.get(id=user_id)

            # check if user is Admin or Developer
            admin = ProjectUserRelation.objects.get(user_id=user_id, project_id=project_id)
            admin = True if admin.user_role == "Admin" else False

            # if user is admin then he can open the proper ticket
            if admin:
                data = request.data
                title = data.get('title', None)
                description = data.get('description', None)
                priority = {v: k for k, v in Tickets.PRIORITY_CHOICES}.get(data.get('priority', None))
                status_ = {v: k for k, v in Tickets.STATUS_CHOICES}.get(data.get('status', None))
                type = {v: k for k, v in Tickets.TICKET_TYPE_CHOICES}.get(data.get('type', None))
                developer_to_be_assigned_id = data.get('users', None)
                print("Admin creating ticket")
                ticket = Tickets.objects.create(
                    title=title,
                    description=description,
                    priority=priority,
                    status=status_,
                    type=type,
                    project=project,
                    users=developer_to_be_assigned_id
                )
                serializer = TicketSerializer(ticket)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                # check if all fields except developer assignment are NOT NULL
                # if validate_ticket(data):
                #     # now check if we need to assign user to ticket or not
                #     developer_to_be_assigned_id = data.get('users', None)
                #     if developer_to_be_assigned_id:
                #         # assign developer
                #         try:
                #             user = User.objects.get(id=developer_to_be_assigned_id)
                #             ticket = Tickets.objects.create(
                #                 title=data['title'],
                #                 description=data['description'],
                #                 priority={v: k for k, v in Tickets.PRIORITY_CHOICES}.get(data['priority']),
                #                 status={v: k for k, v in Tickets.STATUS_CHOICES}.get(data['status']),
                #                 type={v: k for k, v in Tickets.TICKET_TYPE_CHOICES}.get(data['type']),
                #                 project=project,
                #                 users=user
                #             )
                #             serializer = TicketSerializer(ticket)
                #             return Response(serializer.data, status=status.HTTP_201_CREATED)
                #         except User.DoesNotExist:
                #             return Response({}, status=status.HTTP_204_NO_CONTENT)
                #     else:
                #         ticket = Tickets.objects.create(
                #             title=data['title'],
                #             description=data['description'],
                #             priority={v: k for k, v in Tickets.PRIORITY_CHOICES}.get(data['priority']),
                #             status={v: k for k, v in Tickets.STATUS_CHOICES}.get(data['status']),
                #             type={v: k for k, v in Tickets.TICKET_TYPE_CHOICES}.get(data['type']),
                #             project=project
                #         )
                #         serializer = TicketSerializer(ticket)
                #         return Response(serializer.data, status=status.HTTP_201_CREATED)
                # else:
                #     return Response({}, status=status.HTTP_206_PARTIAL_CONTENT)

        except User.DoesNotExist:
            pass
        data = request.data
        title = data.get('title', None)
        description = data.get('description', None)
        if title:
            ticket = Tickets(title=title, description=description, project=project)
            ticket.save()
            result = dict()
            result['id'] = ticket.id
            result['title'] = title
            result['description'] = description
            return Response(result, status=status.HTTP_201_CREATED)
        return Response({"msg": "Ticket Title is required"}, status=status.HTTP_400_BAD_REQUEST)


# /api/user/project/<project_id>/ticket/<ticket_id>
class ListTicketView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, ticket_id):
        user_id = request.user.id

        try:
            # check if ticket exists for this project_id
            ticket = Tickets.objects.get(id=ticket_id, project_id=project_id)

            # since ticket exists, now check if user has permission to view the ticket

            # check if user is admin or not.
            # If Admin -> can see ticket
            # If not admin -< then can see ticket only if assigned to the ticket

            isadmin = isAdmin(user_id, project_id)
            if not isadmin:
                # so user is developer, so check if ticket is assigned to this developer or not
                if ticket.user.id == user_id:
                    serializer = TicketSerializer(ticket)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({}, status=status.HTTP_403_FORBIDDEN)
            else:
                serializer = TicketSerializer(ticket)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Tickets.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, project_id, ticket_id):
        user_id = request.user.id

        # check if project exists
        try:
            project = Projects.objects.get(id=project_id)
        except Projects.DoesNotExist:
            return Response({"msg": "Project Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)

        # check if admin or not
        isadmin = isAdmin(user_id, project_id)
        if not isadmin:
            return Response({"msg": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        else:
            # user is admin so update ticket
            try:
                ticket = Tickets.objects.get(id=ticket_id)
            except Tickets.DoesNotExist:
                return Response({"msg": "Ticket does not exist"}, status=status.HTTP_204_NO_CONTENT)

            # Put value of title and Project in request.data object (as they cannot be null) for checking in serializer
            _mutable_flag = request.data._mutable
            request.data._mutable = True
            if 'title' not in request.data:
                request.data['title'] = ticket.title
            request.data['project'] = project_id
            request.data._mutable = _mutable_flag

            # check if received data is valid
            serializer = TicketSerializer(ticket, request.data)
            if serializer.is_valid():
                data = request.data
                ticket.title = data.get('title', None)
                ticket.description = data.get('description', None)
                ticket.priority = {v: k for k, v in Tickets.PRIORITY_CHOICES}.get(data.get('priority', None))
                ticket.status = {v: k for k, v in Tickets.STATUS_CHOICES}.get(data.get('status', None))
                ticket.type = {v: k for k, v in Tickets.TICKET_TYPE_CHOICES}.get(data.get('type', None))

                # This part could be complicated,
                # Suppose Assigned Developer needs to be changed
                new_assigned_developer_object = None
                try:
                    # developer to be assigned
                    developer_to_be_assigned = data.get('users', None)

                    # checking if there was any other developer assigned to the ticket already
                    # If assigned, then removing the Project-User Relation from the UserProject Table
                    old_developer = ticket.users
                    if old_developer:
                        # first check count of tickets of old_developer in this project
                        # if count of tickets of old_developer >= 2
                            # don't delete the Project-User Relation
                        # elif count of ticktes of old_developer == 1
                            # delete the Project-User Relation if the User is not Admin

                        count = Tickets.objects.filter(users=old_developer.id).count()
                        if count == 1:
                            # remove relation of this old developer
                            try:
                                relation = ProjectUserRelation.objects.get(user_id=old_developer.id, project_id=project_id)
                                if relation.user_role != "Admin":
                                    relation.delete()
                            except ProjectUserRelation.DoesNotExist:
                                pass

                    # now checking if developer_to_be_assigned is a valid User
                    if developer_to_be_assigned:
                        new_assigned_developer_object = User.objects.get(id=developer_to_be_assigned)

                        # create a relation for the user and project as Developer
                        relation, created = ProjectUserRelation.objects.get_or_create(user_id=new_assigned_developer_object,
                                                                                      project_id=project)
                        if relation.user_role != "Admin":
                            relation.user_role = {v: k for k, v in ProjectUserRelation.ROLE_CHOICES}.get("Developer")
                            relation.save()
                except User.DoesNotExist:
                    return Response({"error": "User Does not Exist"}, status=status.HTTP_400_BAD_REQUEST)
                ticket.users = new_assigned_developer_object
                ticket.save()
                response = {
                    'id': ticket.id,
                    'title': ticket.title,
                    'description': ticket.description,
                    'priority': ticket.priority,
                    'status': ticket.status,
                    'type': ticket.type,
                    'CreatedDate': ticket.CreatedDate,
                    'users': ticket.users.id if ticket.users is not None else None
                }
                return Response(response, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Only Admin can delete the ticket
    def delete(self, request, project_id, ticket_id):
        user_id = request.user.id

        # check if user is admin
        if isAdmin(user_id, project_id):
            try:
                ticket = Tickets.objects.get(id=ticket_id)
                ticket.delete()
                return Response({"msg": "Ticket Deleted Successfully"}, status=status.HTTP_200_OK)
            except Tickets.DoesNotExist:
                return Response({"msg": "Ticket Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"msg": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
