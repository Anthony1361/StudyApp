from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User

# for the update-user form .../
# from django.contrib.auth.models import User
# there wasn't User after Room initially
#  .................. //


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # what fields do u want to render out when the user is registering
        fields = [ 'username','email', 'password1', 'password2']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']     

