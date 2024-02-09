from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
User = settings.AUTH_USER_MODEL
# from django.contrib.auth.models import User

from sign.models import Profile

@receiver(post_save, sender = User)    
def create_profile(sender, instance, created, **Kwargs):
    if created:
        Profile.objects.create(user = instance)
        print('profile created')  

# post_save.connect(create_profile, sender=User)        

@receiver(post_save, sender = User)    
def update_profile(sender, instance, created, **Kwargs):
    if created == false:
       instance.Profile.save()
       print('profile updated !!')       

# post_save.connect(update_profile, sender=User)   