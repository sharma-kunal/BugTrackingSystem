from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# class Users(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100)
#     emailID = models.EmailField()
#     password = models.CharField(max_length=50)
#
#     def __str__(self):
#         return str(self.id)


class Projects(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    ticket_form_key = models.CharField(max_length=50, null=True, blank=True)
    project_users = models.ManyToManyField(User, through='ProjectUserRelation')

    def __str__(self):
        return str(self.id)


class Tickets(models.Model):
    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    )
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Closed', 'Closed')
    )
    TICKET_TYPE_CHOICES = (
        ('Feature/Request', 'Feature/Request'),
        ('Bug/Error', 'Bug/Error'),
        ('Others', 'Others')
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)    # not null
    description = models.TextField(max_length=500, null=True, blank=True)
    # submitter = models.CharField(max_length=100, blank=True)     # user who registered the error
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)  # cannot be null (should belong to a project)
    users = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # can be null (no developer assigned)


class ProjectUserRelation(models.Model):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Developer', 'Developer')
    )

    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Projects, null=True, on_delete=models.CASCADE)
    user_role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = [['user_id', 'project_id']]

    def __str__(self):
        return str(self.user_id)+" " + str(self.project_id)

