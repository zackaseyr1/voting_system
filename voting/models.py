from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class VotingEvent(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name

    def is_voting_active(self):
        now = timezone.now()
        print("Start Time:", self.start_time)
        print("End Time:", self.end_time)
        print("Current Time:", now)
        return self.start_time <= now <= self.end_time

        
class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Competitor(models.Model):
    voting_event = models.ForeignKey(VotingEvent, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    flag = models.ImageField(upload_to='team_flags/', null=True, blank=True)
    score = models.IntegerField(default=0)

    def calculate_score(self):
        return self.vote_set.count()

    def __str__(self):
        return f"{self.team.name} - Competitor {self.pk}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.competitor.score = self.competitor.calculate_score()
        self.competitor.save()
