from django.contrib.auth.models import User
from djongo import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=2000)
    all_plot_code = models.JSONField(default=list)
    class Meta:
        db_table = 'user_profile'

