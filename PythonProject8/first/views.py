from collections import defaultdict
from xml.sax.handler import property_interning_dict

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Voting, Option, Vote, Complaint, Comment, Like
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .forms import ProfileEditForm, CustomPasswordChangeForm, RegistrationForm, CustomAuthenticationForm
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout



def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_page')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.request.GET.get('next', '/')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

def home_page(request):
    return render(request, 'index.html')


@login_required()
def voting_page(request):
    return render(request, 'voting.html')


@login_required()
def create_voting(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        voting_type = request.POST.get('voting_type')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        voting = Voting.objects.create(question=question, creator=request.user, voting_type=voting_type, is_anonymous=is_anonymous)
        options = request.POST.getlist('options')
        for option_text in options:
            if option_text.strip():
                Option.objects.create(voting=voting, text=option_text)
        return redirect('view_voting', voting_id=voting.id)
    return render(request, 'create_voting.html')


@login_required()
def view_voting(request, voting_id):
    voting = cache.get(f'voting_{voting_id}')
    if not voting:
        voting = get_object_or_404(Voting.objects.select_related('creator').prefetch_related('options'), id=voting_id)
        cache.set(f'voting_{voting_id}', voting, 300)
    options = voting.options.all()
    previous_votes = Vote.objects.filter(user=request.user, voting=voting)
    previous_option_ids = [vote.option_id for vote in previous_votes]
    if request.method == 'POST':
        if voting.voting_type == 'single':
            option_id = request.POST.get('vote')
            option = get_object_or_404(Option, id=option_id)
            existing_vote = Vote.objects.filter(user=request.user, voting=voting).first()
            if existing_vote:
                if existing_vote.option_id != int(option_id):
                    existing_vote.option.votes -= 1
                    existing_vote.option.save()
                    existing_vote.option = option
                    existing_vote.save()
                    option.votes += 1
                    option.save()
            else:
                option.votes += 1
                option.save()
                Vote.objects.create(user=request.user, voting=voting, option=option)
        elif voting.voting_type == 'multiple':
            options_ids = request.POST.getlist('vote')
            for vote in previous_votes:
                vote.option.votes -= 1
                vote.option.save()
                vote.delete()
            for option_id in options_ids:
                option = get_object_or_404(Option, id=option_id)
                option.votes += 1
                option.save()
                Vote.objects.create(user=request.user, voting=voting, option=option)
        return redirect('view_results', voting_id=voting.id)
    return render(request, 'view_voting.html', {'voting': voting, 'options': options, 'previous_option_ids': previous_option_ids})


@login_required()
def edit_voting(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)
    if request.method == 'POST':
        voting.question = request.POST.get('question')
        voting.save()
        return redirect('view_voting', voting_id=voting.id)
    return render(request, 'edit_voting.html', {'voting': voting})


@login_required()
def add_option(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)
    if request.user != voting.creator:
        return HttpResponse("Вы не являетесь создателем этого опроса.")
    if request.method == 'POST':
        text = request.POST.get('option')
        Option.objects.create(voting=voting, text=text)
        return redirect('view_voting', voting_id=voting.id)
    return render(request, 'add_option.html', {'voting': voting})


@login_required()
def edit_option(request, voting_id, option_id):
    voting = get_object_or_404(Voting, id=voting_id)
    option = get_object_or_404(Option, id=option_id)
    if request.user != voting.creator:
        return HttpResponse("Вы не являетесь создателем этого опроса.")
    if request.method == 'POST':
        option.text = request.POST.get('option')
        option.save()
        return redirect('view_voting', voting_id=option.voting_id)
    return render(request, 'edit_option.html', {'option': option})


@login_required()
def view_options(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)
    if request.method == 'POST':
        option_id = request.POST.get('vote')
        option = get_object_or_404(Option, id=option_id)
        option.votes += 1
        option.save()
        return redirect('view_result', voting_id=voting.id)
    return render(request, 'view_options.html', {'voting': voting})


@login_required()
def view_results(request, voting_id):
    voting = get_object_or_404(Voting.objects.select_related('creator').prefetch_related('options'), id=voting_id)
    results = {option.text: option.votes for option in voting.options.all()}
    return render(request, 'view_results.html', {'results': results, 'voting': voting})


@login_required()
def list_votings(request):
    votings = Voting.objects.all().select_related('creator').prefetch_related('options')
    voting_count = votings.count()
    return render(request, 'list_voting.html', {'votings': votings, 'voting_count': voting_count})


@login_required()
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required()
def edit_profile(request):
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        profile_form = ProfileEditForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'edit_profile.html', {'profile_form': profile_form, 'password_form': password_form})


@login_required()
def profile_history(request):
    votes = Vote.objects.filter(user=request.user).select_related('voting', 'option')
    grouped_votes = defaultdict(list)
    for vote in votes:
        grouped_votes[vote.voting].append(vote.option.text)
    return render(request, 'profile_history.html', {'grouped_votes': dict(grouped_votes)})


@login_required()
def complaints(request):
    return render(request, 'complaints.html')


@login_required
def create_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Complaint.objects.create(user=request.user, title=title, description=description)
        return redirect('complaint_status')
    return render(request, 'create_complaint.html')


@login_required()
def complaint_status(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'complaint_status.html', {'complaints': complaints})


@login_required()
def add_comment(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        Comment.objects.create(voting=voting, user=request.user, text=text)
        return redirect('view_voting', voting_id=voting.id)


@login_required()
def add_likes(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)
    if not Like.objects.filter(voting=voting, user=request.user).exists():
        Like.objects.create(voting=voting, user=request.user)
    return redirect('view_voting', voting_id=voting.id)