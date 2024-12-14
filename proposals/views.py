from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from proposals.models import Proposal
import os
# Create your views here.
from django.http import HttpResponse
from proposals.models import Proposal
from accounts.models import Task, Group, Member

def index(request):
    return HttpResponse("Proposals index page")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProposalForm
from .models import Proposal

@login_required
def submit_proposal(request):
    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.sponsor = request.user  # Assign the sponsor
            proposal.save()
            return redirect('accounts:sponsor_dashboard') # Redirect to sponsor dashboard
    else:
        form = ProposalForm()
    return render(request, 'proposals/submit_proposal.html', {'form': form})

@login_required
def delete_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id, sponsor=request.user)
    
    # Delete the associated file if it exists
    if proposal.file and os.path.isfile(proposal.file.path):
        os.remove(proposal.file.path)
    
    # Delete the proposal
    proposal.delete()
    return redirect('accounts:sponsor_dashboard')