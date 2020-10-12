from django.shortcuts import render
from .models import Projects

# Create your views here.


def TicketForm(request, ticket_form_key):
    try:
        project = Projects.objects.get(ticket_form_key=ticket_form_key)
    except Projects.DoesNotExist:
        return render(request, 'error.html')
    return render(request, 'ticket_form.html', context={'ticket_form_key': ticket_form_key,
                                                        'project_id': project.id})
