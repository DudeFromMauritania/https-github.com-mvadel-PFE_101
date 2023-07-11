
from djongo import models

class Transaction(models.Model):
    id = models.ObjectIdField(primary_key=True)
    plot_code = models.IntegerField()
    sender_username = models.CharField(max_length=100)
    receiver_username = models.CharField(max_length=100)
    signature=models.CharField(max_length=100)
    class Meta:
        db_table = 'Transaction'

class Block(models.Model):
    prev_hash = models.CharField(max_length=100)
    current_hash = models.CharField(max_length=100)

    transactions = models.ArrayField(
        model_container=Transaction
    )

    class Meta:
        db_table = 'Blockchain'


class LandList(models.Model):
    plot_code =models.IntegerField()
    note = models.CharField(max_length=100)

    class Meta:
        db_table = 'LandList'


