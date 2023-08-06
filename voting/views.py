from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VotingEvent, Competitor, Vote, Team
from django.db.models import Count
from django.utils import timezone
from django.db.models import Sum, Count, Case, When, IntegerField  # Import additional functions
#import os
#import matplotlib.pyplot as plt
#from django.conf import settings
#import io
#import base64
#import matplotlib.pyplot as plt
#from urllib.parse import quote
import threading
import os
import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg' before importing pyplot
import matplotlib.pyplot as plt
from django.http import JsonResponse

# ... Rest of the code ...

def landing_page(request):
    now = timezone.now()
    active_events = VotingEvent.objects.filter(start_time__lte=now, end_time__gt=now)
    return render(request, 'voting/landing_page.html', {'events': active_events})


def get_latest_voting_results(request, event_id):
    event = get_object_or_404(VotingEvent, pk=event_id)
    competitors = Competitor.objects.filter(voting_event=event)

    data = {
        'labels': [competitor.team.name for competitor in competitors],
        'scores': [competitor.score for competitor in competitors],
    }

    return JsonResponse(data)

def generate_graph(event):
    os.makedirs('media/voting_results', exist_ok=True)

    competitors = Competitor.objects.filter(voting_event=event)
    competitor_names = [competitor.team.name for competitor in competitors]
    scores = [competitor.score for competitor in competitors]

    plt.bar(competitor_names, scores)
    plt.xlabel('Competitor Name')
    plt.ylabel('Score')
    plt.title('Voting Results - ' + event.name)
    plt.xticks(rotation=45)
    plt.tight_layout()

    graph_file_path = os.path.join('media', 'voting_results', f'{event.name}_graph.png')
    plt.savefig(graph_file_path)
    plt.close()

    return graph_file_path

def results(request, event_id):
    event = get_object_or_404(VotingEvent, pk=event_id)
    competitors = Competitor.objects.filter(voting_event=event)

    # Start a new thread to generate the graph
    graph_thread = threading.Thread(target=generate_graph, args=(event,))
    graph_thread.start()
    graph_thread.join()  # Wait for the thread to finish generating the graph

    graph_file_path = os.path.join('media', 'voting_results', f'{event.name}_graph.png')

    # Use the graph_file_path to display the graph in the template
    return render(request, 'voting/results.html', {
        'event': event,
        'competitors': competitors,
        'graph_file_path': graph_file_path,
    })





@login_required
def vote(request, event_id):
    event = get_object_or_404(VotingEvent, pk=event_id)

    # Check if the voting has ended for the selected event
    if not event.is_voting_active():
        return redirect('results', event_id=event_id)

    user = request.user

    # Check if the user has already voted for this event
    has_voted = Vote.objects.filter(user=user, competitor__voting_event=event).exists()

    if has_voted:
        # User has already voted, you may show a message or redirect to results page
        return redirect('results', event_id=event_id)

    if request.method == 'POST':
        competitor_id = request.POST.get('competitor')

        try:
            competitor = Competitor.objects.get(pk=competitor_id, voting_event=event)
        except Competitor.DoesNotExist:
            return render(request, 'voting/vote.html', {'event': event, 'user': user, 'error_message': 'Invalid Competitor'})

        # Create the vote and mark that the user has voted for this event
        Vote.objects.create(user=user, competitor=competitor)

        # Redirect to the results page after voting
        return redirect('results', event_id=event_id)

    competitors = Competitor.objects.filter(voting_event=event)
    return render(request, 'voting/vote.html', {'event': event, 'competitors': competitors, 'user': user})



@login_required
def view_events(request):
    events = VotingEvent.objects.all()
    return render(request, 'voting/view_events.html', {'events': events})



def team_list(request):
    teams = Team.objects.all()
    return render(request, 'voting/team_list.html', {'teams': teams})



def team_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    # Get all competitors associated with the team
    competitors = Competitor.objects.filter(team=team)

    # Get all votes for the competitors associated with the team
    votes = Vote.objects.filter(competitor__in=competitors)

    # Calculate the number of wins for the team across all competitions
    wins = votes.aggregate(
        wins=Count(Case(When(competitor__score__gt=0, then=1), output_field=IntegerField()))
    )['wins']

    # Calculate the total number of competitions for the team
    total_competitions = Competitor.objects.filter(team=team).values('voting_event').distinct().count()

    # Calculate the number of losses for the team across all competitions
    losses = total_competitions - wins

    # Calculate the total scores for the team across all competitions
    total_scores = Competitor.objects.filter(team=team).aggregate(total_scores=Sum('score'))['total_scores']

    # Get the list of VotingEvent objects associated with the team's Competitors
    competitions_participated = VotingEvent.objects.filter(competitor__team=team).distinct()

    return render(request, 'voting/team_view.html', {
        'team': team,
        'wins': wins,
        'losses': losses,
        'total_scores': total_scores,
        'total_competitions': total_competitions,
        'competitions_participated': competitions_participated,
    })