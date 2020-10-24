from django.db import models
from django.utils import timezone
from django.urls import reverse
# Create your models here.

race_list = (
    ('T', 'Terran'),
    ('P', 'Protoss'),
    ('Z', 'Zerg'),
    ('R', 'Random')
)


class User(models.Model):
    class Meta:
        ordering = ['-joined_date', 'name']

    # Must change unique to UniqueConstraint.
    # And add Case-Insensitive to UniqueConstraint.condition.
    name = models.CharField(max_length=30, default="", unique=True, null=False)
    joined_date = models.DateField(default=timezone.now, null=False)
    career = models.TextField(default="추가 바람.")
    most_race = models.CharField(max_length=10, choices=race_list, null=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("haley_gg:users_detail", kwargs={"name": self.name})
