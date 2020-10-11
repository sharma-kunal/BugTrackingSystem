from django.test import TestCase, Client

# Create your tests here.

user1 = Client()
user1.post('/signup', {''})

