from django.db import models

# Create your models here.
class Amar_bank(models.Model):
    bank_name = 'Amar Bank'
    is_bankrupt = models.BooleanField(default=False)

