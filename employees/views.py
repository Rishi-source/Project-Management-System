from django.shortcuts import render, redirect ,reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .models import *
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.db.models import Sum
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from django.db import IntegrityError
from datetime import date
from datetime import datetime
from django.utils.timezone import make_aware
from django.contrib import messages 
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import random
from django.core.mail import EmailMessage
import calendar
from django.utils.timezone import now
from matplotlib.ticker import MaxNLocator
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from collections import defaultdict
import pandas as pd
from django.utils import timezone
from calendar import month_name, month_abbr
# Create your views here.
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    ongoing_count = Project.objects.filter(is_completed=False, is_handed_over=False).count()
    completed_count = Project.objects.filter(is_completed=True, is_handed_over=False).count()
    handedover_count = Project.objects.filter(is_completed=True, is_handed_over=True).count()
    newly_added_projects = Project.objects.order_by('-Sanctioned_Amount_Date')[:5]  

    context = {
        'ongoing_count': ongoing_count,
        'completed_count': completed_count,
        'handedover_count': handedover_count,
        'newly_added_projects': newly_added_projects,

    }

    return render(request, 'dashboard.html', context)




def login_user(request):
    if 'error' in request.session:
        del request.session['error']

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username = username, password = password)

    if user != None:
        login(request, user)
        request.session['username'] = username
        return redirect('dashboard')
    else:
        request.session['error'] = "Username or Password is incorrect"
        return redirect('login')


def loginView(request):
    if 'username' in request.session:
        return redirect('dashboard')
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username = username, password = password)
            if user != None:
                login(request, user)
                request.session['username'] = username
                return redirect('dashboard')
            else:
                request.session['error'] = "Username or Password is incorrect"
                return redirect('login')

    else:
        form = LoginForm()

    return render(request, template_name = 'login.html', context = { 'form': form })

def logout_user(request):
    logout(request)
    if 'username' in request.session:
        del request.session['username']
    return redirect('login')


def forgot_password(request):
    del request.session['username']
    logout(request)
    return redirect('login')
def register(request):
    return render(request, "register.html")

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not (username and email and password and confirm_password):
            request.session['error'] = "All fields are required."
            return redirect('register_user')

        if password != confirm_password:
            request.session['error'] = "Passwords do not match."
            return redirect('register_user')

        if User.objects.filter(username=username).exists():
            request.session['error'] = "Username is already taken. Please choose another one."
            return redirect('register_user')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)  
            request.session['success'] = "User successfully registered."
            return redirect('dashboard')  
        except ValidationError as e:
            request.session['error'] = str(e)
            return redirect('register_user')

    return render(request, 'register.html')

# ------------------------------ PROJECTS START ------------------------------ #

def projects(request):
    if not request.user.is_authenticated:
        return redirect('login')
    project = Project.objects.all()
    return render(request, 'projects/projects_list.html', {'projects' : project} )


def add_project(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        try:
            cd = request.POST["Client_Department"]
            dd = request.POST["Division"]
            nop = request.POST["Name_Of_Project"]
            sa = request.POST["Sanctioned_Amount"]
            sad = request.POST["Sanctioned_Amount_Date"]
            tsa = request.POST["Technical_Sanctioned_Amount"]
            sd = request.POST["Start_date"]
            tsad = request.POST["Technical_Sanctioned_Amount_Date"]
            sdoc = request.POST["Stipulated_Date_Of_Completion"]
            woad = request.POST["Work_Order_Amount_Date"]
            woa =request.POST["Work_Order_Amount"]

            sad_date = parse_date(sad)
            sd_date = parse_date(sd)
            tsad_date = parse_date(tsad)
            sdoc_date = parse_date(sdoc)
            woad_date = parse_date(woad)
            new_project = Project(
                Client_Department=cd,
                Division=dd,
                Name_Of_Project=nop,
                Sanctioned_Amount=sa,
                Sanctioned_Amount_Date=sad_date,
                Technical_Sanctioned_Amount=tsa,
                Technical_Sanctioned_Amount_Date=tsad_date,
                Work_order_Amount_Date = woad_date,
                Work_order_Amount = woa,
                Start_date=sd_date,
                Stipulated_Date_Of_Completion=sdoc_date
            )
            
            new_project.save()

            res = "Project {} is successfully added".format(nop)
            return render(request, "projects/add_project.html", {"status": res})

        except KeyError as e:
            res = "Missing field: {}".format(e)
            return render(request, "projects/add_project.html", {"status": res})
        except ValidationError as e:
            res = "Validation error: {}".format(e)
            return render(request, "projects/add_project.html", {"status": res})
        except Exception as e:
            res = "An error occurred: {}".format(e)
            return render(request, "projects/add_project.html", {"status": res})

    return render(request, "projects/add_project.html")

def delete_project(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')

    project = Project.objects.filter(pk = project_id)
    if project:
        project = Project.objects.get(pk = project_id)
        project.delete()
    return redirect('projects')

def add_amount_received(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    project_instance = get_object_or_404(Project, pk=project_id) 
    print(project_instance)
    
    if request.method == "POST":
        try:
            rad = request.POST["Recieved_Amount_Date"]
            ra = request.POST["Recieved_Amount"]

            rad_date = parse_date(rad)

            data = AmountReceived(
                project=project_instance,  
                Amount_Received_Date=rad_date, 
                Amount_Received=ra,
            )
            
        
            data.save()

            success = "Amount of Rs. {} lacs is successfully added".format(ra)
            return render(request, "projects/add_amountrecieved.html", {"success": success})

        except KeyError as e:
            error = "Missing field: {}".format(e)
            return render(request, "projects/add_amountrecieved.html", {"error": error})
        except ValidationError as e:
            error = "Validation error: {}".format(e)
            return render(request, "projects/add_amountrecieved.html", {"error": error}) 
        except Exception as e:
            error = "An error occurred: {}".format(e)
            return render(request, "projects/add_amountrecieved.html", {"error": error})

    return render(request, "projects/add_amountrecieved.html")

def add_amount_released(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    project_instance = get_object_or_404(Project, pk=project_id)  
    

    if request.method == "POST":
        try:
            rad = request.POST["Released_Amount_Date"]
            ra = request.POST["Released_Amount"]

            rad_date = parse_date(rad)

            data = AmountReleased(
                project=project_instance,
                Amount_Released_Date=rad_date, 
                Amount_Released=ra,
            )
            
            data.save()

            success = "Released Amount of Rs. {} lacs is successfully added".format(ra)
            return render(request, "projects/add_amountreleased.html", {"success": success})

        except KeyError as e:
            error = "Missing field: {}".format(e)
            return render(request, "projects/add_amountreleased.html", {"error": error})
        except ValidationError as e:
            error = "Validation error: {}".format(e)
            return render(request, "projects/add_amountreleased.html", {"error": error}) 
        except Exception as e:
            error = "An error occurred: {}".format(e)
            return render(request, "projects/add_amountreleased.html", {"error": error})

    return render(request, "projects/add_amountreleased.html")

def add_progress(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    project_instance = get_object_or_404(Project, pk=project_id)
        
    if request.method == "POST":
        try:
            rad = request.POST["Date_Of_Reporting"]
            ra = request.POST["Physical_Progress_Percentage"]

            rad_date = parse_date(rad)

            progress = PhysicalProgress(
                project=project_instance,
                Date_Of_Reporting=rad_date,
                Physical_Progress_Percentage=ra,
            )
            
            progress.save()

            res = f"Physical Progress of {ra}% is successfully recorded."
            return render(request, "projects/add_progress.html", {"success": res})

        except KeyError as e:
            error = f"Missing field: {e}"
            return render(request, "projects/add_progress.html", {"error": error})
        
        except ValidationError as e:
            error = f"Validation error: {e}"
            return render(request, "projects/add_progress.html", {"error": error})

        except Exception as e:
            error = f"An error occurred: {e}"
            return render(request, "projects/add_progress.html", {"error": error})

    return render(request, "projects/add_progress.html")

def add_total_expenditure(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    project_instance = get_object_or_404(Project, pk=project_id)
    
    if request.method == "POST":
        try:
            total_expenditure = request.POST.get("Total_Expenditure")
            date_str = request.POST.get("Date")
            date = make_aware(datetime.strptime(date_str, "%Y-%m-%d"))

            expenditure = Expenditure(
                project=project_instance,
                Expenditure_date=date,
                Expenditure_Value=total_expenditure
            )
            
            expenditure.save()

            success = f"Total expenditure of Rs. {total_expenditure} is successfully added for {date.strftime('%B %Y')}."
            return render(request, "projects/add_expenditure.html", {"success": success, "project": project_instance})
        
        except ValueError as e:
            error = f"Invalid input: {e}"
            return render(request, "projects/add_expenditure.html", {"error": error, "project": project_instance})
        except IntegrityError as e:
            error = f"Database Error: {e}"
            return render(request, "projects/add_expenditure.html", {"error": error, "project": project_instance})
        except Exception as e:
            error = f"An error occurred: {e}"
            return render(request, "projects/add_expenditure.html", {"error": error, "project": project_instance})

    return render(request, "projects/add_expenditure.html", {"project": project_instance})
from django.db.models import Sum
from django.utils.timezone import now

def fetch_yearly_data(project):
    yearly_data = {
        'received': [],
        'released': [],
        'expenditure': [],
    }

    current_year = now().year

    amounts_received = AmountReceived.objects.filter(project=project).values('Amount_Received_Date__year').annotate(total_received=Sum('Amount_Received')).order_by('Amount_Received_Date__year')

    amounts_released = AmountReleased.objects.filter(project=project).values('Amount_Released_Date__year').annotate(total_released=Sum('Amount_Released')).order_by('Amount_Released_Date__year')

    expenditures = Expenditure.objects.filter(project=project).values('Expenditure_date__year').annotate(total_expenditure=Sum('Expenditure_Value')).order_by('Expenditure_date__year')

    yearly_data = {
        'received': amounts_received,
        'released': amounts_released,
        'expenditure': expenditures,
    }

    return yearly_data

def fetch_monthly_data(project, selected_year):
    amounts_received = AmountReceived.objects.filter(project=project, Amount_Received_Date__year=selected_year)
    monthly_received_data = amounts_received.values('Amount_Received_Date__month').annotate(total_received=Sum('Amount_Received')).order_by('Amount_Received_Date__month')

    amounts_released = AmountReleased.objects.filter(project=project, Amount_Released_Date__year=selected_year)
    monthly_released_data = amounts_released.values('Amount_Released_Date__month').annotate(total_released=Sum('Amount_Released')).order_by('Amount_Released_Date__month')

    expenditures = Expenditure.objects.filter(project=project, Expenditure_date__year=selected_year)
    monthly_expenditure_data = expenditures.values('Expenditure_date__month').annotate(total_expenditure=Sum('Expenditure_Value')).order_by('Expenditure_date__month')

    monthly_data = {
        'received': monthly_received_data,
        'released': monthly_released_data,
        'expenditure': monthly_expenditure_data,
    }

    return monthly_data

def project_detail(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    project = get_object_or_404(Project, id=project_id)
    
    selected_year = None
    graphic_month_received = None
    graphic_month_released = None
    graphic_month_expenditure = None
    graphic_year_received = None
    graphic_year_released = None
    graphic_year_expenditure = None

    if request.method == 'GET':
        if 'years' in request.GET:
            selected_year = request.GET.get('years')

        monthly_data = fetch_monthly_data(project, selected_year or now().year)
        
        if monthly_data['received']:
            months_received = [data['Amount_Received_Date__month'] for data in monthly_data['received']]
            amounts_received = [data['total_received'] for data in monthly_data['received']]
            plt.figure(figsize=(8, 4))
            bars = plt.bar(months_received, amounts_received, color='blue')
            plt.title(f"Monthly Amounts Received for {selected_year or now().year}")
            plt.xlabel("Month")
            plt.ylabel("Amount (Rs. Lacs)")
            plt.xticks(np.arange(1, 13), calendar.month_name[1:13], rotation=45) 
            plt.tight_layout()

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graphic_month_received = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        if monthly_data['released']:
            months_released = [data['Amount_Released_Date__month'] for data in monthly_data['released']]
            amounts_released = [data['total_released'] for data in monthly_data['released']]
            plt.figure(figsize=(8, 4))
            bars = plt.bar(months_released, amounts_released, color='green')
            plt.title(f"Monthly Amounts Released for {selected_year or now().year}")
            plt.xlabel("Month")
            plt.ylabel("Amount (Rs. Lacs)")
            plt.xticks(np.arange(1, 13), calendar.month_name[1:13], rotation=45) 
            plt.tight_layout()

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graphic_month_released = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        if monthly_data['expenditure']:
            months_expenditure = [data['Expenditure_date__month'] for data in monthly_data['expenditure']]
            amounts_expenditure = [data['total_expenditure'] for data in monthly_data['expenditure']]
            plt.figure(figsize=(8, 4))
            bars = plt.bar(months_expenditure, amounts_expenditure, color='red')
            plt.title(f"Monthly Expenditure for {selected_year or now().year}")
            plt.xlabel("Month")
            plt.ylabel("Expenditure (Rs. Lacs)")
            plt.xticks(np.arange(1, 13), calendar.month_name[1:13], rotation=45) 
            plt.tight_layout()

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graphic_month_expenditure = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        yearly_data = fetch_yearly_data(project)

        if yearly_data['received']:
            years_received = [data['Amount_Received_Date__year'] for data in yearly_data['received']]
            amounts_received = [data['total_received'] for data in yearly_data['received']]
            plt.figure(figsize=(8, 4))
            bars = plt.bar(years_received, amounts_received, color='blue')
            plt.title(f"Yearly Amounts Received")
            plt.xlabel("Year")
            plt.ylabel("Amount (Rs. Lacs)")
            plt.xticks(years_received, rotation=45)  # Rotate ticks for better readability
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure ticks are integers
            plt.tight_layout()

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graphic_year_received = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        if yearly_data['released']:
            years_released = [data['Amount_Released_Date__year'] for data in yearly_data['released']]
            amounts_released = [data['total_released'] for data in yearly_data['released']]
            plt.figure(figsize=(8, 4))
            bars = plt.bar(years_released, amounts_released, color='green')
            plt.title(f"Yearly Amounts Released")
            plt.xlabel("Year")
            plt.ylabel("Amount (Rs. Lacs)")
            plt.xticks(years_received, rotation=45)  # Rotate ticks for better readability
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure ticks are integers
            plt.tight_layout()
            plt.tight_layout()

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graphic_year_released = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        if yearly_data['expenditure']:
            years_expenditure = [data['Expenditure_date__year'] for data in yearly_data['expenditure']]
            total_expenditure = [data['total_expenditure'] for data in yearly_data['expenditure']]
            plt.figure(figsize=(8, 4))
            bars = plt.bar(years_expenditure, total_expenditure, color='red')
            plt.title(f"Yearly Total Expenditure")
            plt.xlabel("Year")
            plt.ylabel("Total Expenditure (Rs. Lacs)")
            plt.xticks(years_received, rotation=45)  # Rotate ticks for better readability
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure ticks are integers
            plt.tight_layout()

            plt.tight_layout()

            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graphic_year_expenditure = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

    amounts_received = AmountReceived.objects.filter(project=project).order_by('Amount_Received_Date')
    amounts_released = AmountReleased.objects.filter(project=project).order_by('Amount_Released_Date')
    physical_progress = PhysicalProgress.objects.filter(project=project).order_by('-Date_Of_Reporting')
    total_expenditures = Expenditure.objects.filter(project=project).order_by('Expenditure_date')

    total_amount_received = amounts_received.aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0
    total_amount_released = amounts_released.aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
    total_expenditure_sum = total_expenditures.aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
    project = Project.objects.get(id=project_id)
    
    total_amount_received = AmountReceived.objects.filter(project=project).aggregate(total=Sum('Amount_Received'))['total'] or 0
    
    total_amount_released = AmountReleased.objects.filter(project=project).aggregate(total=Sum('Amount_Released'))['total'] or 0
    
    total_expenditure = Expenditure.objects.filter(project=project).aggregate(total=Sum('Expenditure_Value'))['total'] or 0

    remaining_amount = total_amount_received - total_expenditure
    agencycharge = project.Sanctioned_Amount - project.Technical_Sanctioned_Amount
    percentage = (agencycharge/project.Sanctioned_Amount)*100

    context = {
        'project': project,
        'selected_year': selected_year,
        'graphic_month_received': graphic_month_received,
        'graphic_month_released': graphic_month_released,
        'graphic_month_expenditure': graphic_month_expenditure,
        'graphic_year_received': graphic_year_received,
        'graphic_year_released': graphic_year_released,
        'graphic_year_expenditure': graphic_year_expenditure,
        'amounts_received': amounts_received,
        'total_amount_received': total_amount_received,
        'amounts_released': amounts_released,
        'total_amount_released': total_amount_released,
        'physical_progress': physical_progress,
        'total_expenditures': total_expenditures,
        'total_expenditure_sum': total_expenditure_sum,
        'remaining_amount': remaining_amount,
        'agencycharge':agencycharge,
        'percentage':percentage,
    }

    return render(request, 'projects/project_detail.html', context)
def calculate_total_expenditure():
    total_expenditure = Expenditure.objects.aggregate(total=models.Sum('Expenditure_Value'))['total']
    return total_expenditure if total_expenditure is not None else 0

def calculate_remaining_amount(sanctioned_amount, total_expenditure):
    remaining_amount = sanctioned_amount - total_expenditure
    return remaining_amount
def fetch_project_data(projects, total_expenditure_sum):
    recent_physical_progress = {}

    for project in projects:
        # Example logic to calculate recent physical progress
        # Replace this with your actual logic
        recent_physical_progress[project.id] = {
            'percentage': calculate_percentage(project.total_expenditure_sum, total_expenditure_sum)
        }
    
    return recent_physical_progress

def calculate_percentage(project_expenditure_sum, total_expenditure_sum):
    if total_expenditure_sum > 0:
        return round((project_expenditure_sum / total_expenditure_sum) * 100, 2)
    else:
        return 0


def view_project(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    projects = Project.objects.all()
    for project in projects:
        # Calculate total expenditure for the project
        total_expenditures = Expenditure.objects.filter(project=project).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_AmountReleased = AmountReleased.objects.filter(project=project).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_AmountReceived = AmountReceived.objects.filter(project=project).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0
        project.total_expenditure_sum = total_expenditures  # Attach total_expenditure_sum to each project instance
        project.total_AmountReleased = total_AmountReleased
        project.total_AmountReceived = total_AmountReceived
        # Fetch project status (assuming Project_Status model is linked to Project)    
    context = {
        'projects': projects,
    }
    return render(request, 'projects/view_project.html', context)
def edit_stipulated_date(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    status = ""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        if request.method == 'POST':
            new_stipulated_date = request.POST.get('Stipulated_Date')
            project.Stipulated_Date_Of_Completion = new_stipulated_date
            project.save()

            status = "Stipulated date of completion updated successfully."
            return render(request, "projects/edit_date_of_completion.html", {'status': status})

    except KeyError as e:
        status = "Missing field: {}".format(e)
    except ValidationError as e:
        status = "Validation error: {}".format(e)
    except Exception as e:
        status = "An error occurred: {}".format(e)

    return render(request, "projects/edit_date_of_completion.html", {'status': status, 'project': project})
def mark_project_completed(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    project = get_object_or_404(Project, id=project_id)
    project.is_completed = True
    project.save()  # Save the project object after making changes

    status = "Project {} marked as completed".format(project.Name_Of_Project)
    query_params = urlencode({'status': status, 'project': project.id})

    return redirect(f"{reverse('view_project')}?{query_params}")
def fetch_project_data(projects, total_expenditure):
    recent_physical_progress = {}
    status = ""
    for project in projects:
        latest_progress = PhysicalProgress.objects.filter(project=project).order_by('-Date_Of_Reporting').first()
        
        if latest_progress:
            recent_physical_progress[project.id] = {
                'percentage': latest_progress.Physical_Progress_Percentage,
                'date': latest_progress.Date_Of_Reporting.strftime('%Y-%m-%d')
            }
        else:
            recent_physical_progress[project.id] = {
                'percentage': 0,
                'date': None
            }

        project.total_expenditure = total_expenditure
        project.remaining_amount = calculate_remaining_amount(project.Sanctioned_Amount, total_expenditure)
    
    return recent_physical_progress

def calculate_remaining_amount(sanctioned_amount, total_expenditure):
    remaining_amount = sanctioned_amount - total_expenditure
    return remaining_amount

def mark_project_handedover(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    project = get_object_or_404(Project, id=project_id)
    project.is_handed_over = True
    project.save()  # Save the project object after making changes

    status = "Project {} marked as handed over".format(project.Name_Of_Project)
    query_params = urlencode({'status': status, 'project': project.id})

    return redirect(f"{reverse('view_project')}?{query_params}")
def edit_project(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            status = f"Project '{project.Name_Of_Project}' is successfully edited."
            projects = Project.objects.all()
            return render(request, 'projects/projects_list.html', {'projects': projects, 'status': status})
    else:
        form = ProjectForm(instance=project)
        status = ""

    context = {
        'form': form,
        'project_id': project_id,
        'status': status,
    }
    return render(request, 'projects/edit_project.html', context)
def amount_received(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    amount_received_entries = AmountReceived.objects.filter(project=project)

    context = {
        'project': project,
        'amount_received_entries': amount_received_entries,
    }

    return render(request, 'projects/edit_amountreceived.html', context)

def edit_amount_received(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        amount_received = request.POST.get('amount_received')
        
        # Retrieve the existing entry
        entry = get_object_or_404(AmountReceived, pk=entry_id)

        # Update the fields
        entry.Amount_Received = amount_received
        
        # Ensure Amount_Received_Date is set appropriately
        # For example, you might set it to the current date or retrieve it from the form
        entry.Amount_Received_Date = entry.Amount_Received_Date  # Ensure this is properly set

        # Save the entry
        entry.save()

        # Optionally, add a success message or redirect
        messages.success(request, 'Amount Received entry updated successfully.')
        return redirect('edit_amount_received', project_id=project.pk)

    # Handle GET request (rendering form)
    amount_received_entries = project.amount_received.all()  # Corrected related name usage
    return render(request, 'projects/edit_amountreceived.html', {
        'project': project,
        'amount_received_entries': amount_received_entries,
    })
def delete_amount_received(request, project_id):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        
        # Retrieve the amount received entry to delete
        entry = get_object_or_404(AmountReceived, pk=entry_id)
        entry.delete()
        
        messages.success(request, 'Amount received entry deleted successfully.')
    
    return redirect('edit_amount_received', project_id=project_id)
def edit_amount_released(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        amount_released = request.POST.get('amount_released')
        
        if entry_id:
            amount_released_entry = get_object_or_404(AmountReleased, pk=entry_id, project=project)
            amount_released_entry.Amount_Released = amount_released
            amount_released_entry.save()
            messages.success(request, 'Amount released entry updated successfully.')
        else:
            messages.error(request, 'Invalid entry ID.')

    amount_released_entries = AmountReleased.objects.filter(project=project)
    context = {
        'project': project,
        'amount_released_entries': amount_released_entries,
    }
    return render(request, 'projects/edit_amountrelesed.html', context)

def delete_amount_released(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            amount_released_entry = get_object_or_404(AmountReleased, pk=entry_id, project=project)
            amount_released_entry.delete()
            messages.success(request, 'Amount released entry deleted successfully.')
        else:
            messages.error(request, 'Invalid entry ID.')
    return redirect('projects/edit_amountrelesed.html', project_id=project_id)
def edit_physical_progress(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    physical_progress_entries = project.physical_progress_entries.all()

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        physical_progress_entry = get_object_or_404(PhysicalProgress, pk=entry_id)

        # Manually fetch form data from POST request
        physical_progress_percentage = request.POST.get('physical_progress_percentage')

        # Validate form data
        if physical_progress_percentage:
            # Update PhysicalProgress instance
            physical_progress_entry.Physical_Progress_Percentage = physical_progress_percentage
            physical_progress_entry.save()

            messages.success(request, 'Physical Progress percentage updated successfully.')
            return redirect('edit_physical_progress', project_id=project_id)
        else:
            messages.error(request, 'Please fill in all fields.')
    else:
        # Initialize an empty form for GET request
        form = None

    context = {
        'project': project,
        'physical_progress_entries': physical_progress_entries,
        'form': form,
    }
    return render(request, 'projects/edit_physical_progress.html', context)
def delete_physical_progress(request, project_id):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            physical_progress = get_object_or_404(PhysicalProgress, pk=entry_id)
            physical_progress.delete()
            messages.success(request, 'Expenditure entry deleted successfully.')
        else:
            messages.error(request, 'Invalid expenditure entry ID.')
    
    return redirect('projects/edit_physical_progress', project_id=project_id)
def edit_expenditure(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    expenditures = Expenditure.objects.filter(project=project)

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        expenditure_value = request.POST.get('expenditure_value')

        if entry_id and expenditure_value:
            try:
                expenditure = get_object_or_404(Expenditure, pk=entry_id, project=project)
                expenditure.Expenditure_Value = expenditure_value
                expenditure.save()
                messages.success(request, 'Expenditure updated successfully.')
            except Expenditure.DoesNotExist:
                messages.error(request, 'Expenditure entry not found.')
        else:
            messages.error(request, 'Please provide a valid expenditure value.')

    context = {
        'project': project,
        'expenditures': expenditures,
    }
    return render(request, 'projects/edit_expenditure.html', context)
def delete_expenditure(request, project_id):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            expenditure = get_object_or_404(Expenditure, pk=entry_id)
            expenditure.delete()
            messages.success(request, 'Expenditure entry deleted successfully.')
        else:
            messages.error(request, 'Invalid expenditure entry ID.')
    
    return redirect('edit_expenditure', project_id=project_id)
def amount_released_analysis(request):
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    divisions = ['Udaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Jaipur', 'Ajmer', 'Bharatpur']
    yearly_data = {division: 0 for division in divisions}

    # Monthly data variables for each division
    udaipur_monthly_data = [0] * 12
    jodhpur_monthly_data = [0] * 12
    kota_monthly_data = [0] * 12
    bikaner_monthly_data = [0] * 12
    jaipur_monthly_data = [0] * 12
    ajmer_monthly_data = [0] * 12
    bharatpur_monthly_data = [0] * 12

    month_names = month_abbr[1:]

    for division in divisions:
        # Calculate yearly amounts for the division
        yearly_amounts_data = AmountReleased.objects.filter(
            project__Division=division,
            Amount_Released_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Released'))

        yearly_data[division] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        # Calculate monthly amounts for the division
        for month in range(1, 13):
            monthly_amounts_data = AmountReleased.objects.filter(
                project__Division=division,
                Amount_Released_Date__year=selected_year,
                Amount_Released_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Released'))

            # Assign monthly amounts to respective division variables
            if division == 'Udaipur':
                udaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jodhpur':
                jodhpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Kota':
                kota_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Bikaner':
                bikaner_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jaipur':
                jaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Ajmer':
                ajmer_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Bharatpur':
                bharatpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031)  # List of years from 2020 to 2030

    context = {
        'year': selected_year,
        'divisions': divisions,
        'yearly_data': yearly_data,
        'udaipur_monthly_data': udaipur_monthly_data,
        'jodhpur_monthly_data': jodhpur_monthly_data,
        'kota_monthly_data': kota_monthly_data,
        'bikaner_monthly_data': bikaner_monthly_data,
        'jaipur_monthly_data': jaipur_monthly_data,
        'ajmer_monthly_data': ajmer_monthly_data,
        'bharatpur_monthly_data': bharatpur_monthly_data,
        'years': years,
    }
    return render(request, 'projects/amount_released_analysis.html', context)
def amount_recieved_analysis(request):
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    divisions = ['Udaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Jaipur', 'Ajmer', 'Bharatpur']
    yearly_data = {division: 0 for division in divisions}

    # Monthly data variables for each division
    udaipur_monthly_data = [0] * 12
    jodhpur_monthly_data = [0] * 12
    kota_monthly_data = [0] * 12
    bikaner_monthly_data = [0] * 12
    jaipur_monthly_data = [0] * 12
    ajmer_monthly_data = [0] * 12
    bharatpur_monthly_data = [0] * 12

    month_names = month_abbr[1:]

    for division in divisions:
        # Calculate yearly amounts for the division
        yearly_amounts_data = AmountReceived.objects.filter(
            project__Division=division,
            Amount_Received_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Received'))

        yearly_data[division] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        # Calculate monthly amounts for the division
        for month in range(1, 13):
            monthly_amounts_data = AmountReceived.objects.filter(
                project__Division=division,
                Amount_Received_Date__year=selected_year,
                Amount_Received_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Received'))

            # Assign monthly amounts to respective division variables
            if division == 'Udaipur':
                udaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jodhpur':
                jodhpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Kota':
                kota_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Bikaner':
                bikaner_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jaipur':
                jaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Ajmer':
                ajmer_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Bharatpur':
                bharatpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031)  # List of years from 2020 to 2030

    context = {
        'year': selected_year,
        'divisions': divisions,
        'yearly_data': yearly_data,
        'udaipur_monthly_data': udaipur_monthly_data,
        'jodhpur_monthly_data': jodhpur_monthly_data,
        'kota_monthly_data': kota_monthly_data,
        'bikaner_monthly_data': bikaner_monthly_data,
        'jaipur_monthly_data': jaipur_monthly_data,
        'ajmer_monthly_data': ajmer_monthly_data,
        'bharatpur_monthly_data': bharatpur_monthly_data,
        'years': years,
    }
    return render(request, 'projects/amount_recieved_analysis.html', context)
def expenditure_analysis(request):
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    divisions = ['Udaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Jaipur', 'Ajmer', 'Bharatpur']
    yearly_data = {division: 0 for division in divisions}

    # Monthly data variables for each division
    udaipur_monthly_data = [0] * 12
    jodhpur_monthly_data = [0] * 12
    kota_monthly_data = [0] * 12
    bikaner_monthly_data = [0] * 12
    jaipur_monthly_data = [0] * 12
    ajmer_monthly_data = [0] * 12
    bharatpur_monthly_data = [0] * 12

    for division in divisions:
        # Calculate yearly amounts for the division
        yearly_amounts_data = Expenditure.objects.filter(
            project__Division=division,
            Expenditure_date__year=selected_year
        ).aggregate(total_amount=Sum('Expenditure_Value'))

        yearly_data[division] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        # Calculate monthly amounts for the division
        for month in range(1, 13):
            monthly_amounts_data = Expenditure.objects.filter(
                project__Division=division,
                Expenditure_date__year=selected_year,
                Expenditure_date__month=month
            ).aggregate(total_amount=Sum('Expenditure_Value'))

            # Assign monthly amounts to respective division variables
            if division == 'Udaipur':
                udaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jodhpur':
                jodhpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Kota':
                kota_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Bikaner':
                bikaner_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jaipur':
                jaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Ajmer':
                ajmer_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Bharatpur':
                bharatpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031)  # List of years from 2020 to 2030

    context = {
        'year': selected_year,
        'divisions': divisions,
        'yearly_data': yearly_data,
        'udaipur_monthly_data': udaipur_monthly_data,
        'jodhpur_monthly_data': jodhpur_monthly_data,
        'kota_monthly_data': kota_monthly_data,
        'bikaner_monthly_data': bikaner_monthly_data,
        'jaipur_monthly_data': jaipur_monthly_data,
        'ajmer_monthly_data': ajmer_monthly_data,
        'bharatpur_monthly_data': bharatpur_monthly_data,
        'years': years,
    }
    return render(request, 'projects/expenditure_analysis.html', context)
def expenditure_analysis_client(request):
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    clients = ['Sports Department', 'Skill Department', 'LSG Department', 'Technical & Higher Education']
    yearly_data = {client: 0 for client in clients}

    # Monthly data variables for each division
    Sports_Department_monthly_data = [0] * 12
    Skill_Department_monthly_data = [0] * 12
    LSG_Department_monthly_data = [0] * 12
    Technical_Higher_Education_monthly_data = [0] * 12

    for client in clients:
        # Calculate yearly amounts for the division
        yearly_amounts_data = Expenditure.objects.filter(
            project__Client_Department=client,
            Expenditure_date__year=selected_year
        ).aggregate(total_amount=Sum('Expenditure_Value'))

        yearly_data[client] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        # Calculate monthly amounts for the division
        for month in range(1, 13):
            monthly_amounts_data = Expenditure.objects.filter(
                project__Client_Department=client,
                Expenditure_date__year=selected_year,
                Expenditure_date__month=month
            ).aggregate(total_amount=Sum('Expenditure_Value'))
            # Assign monthly amounts to respective division variables
            if client == 'Sports Department':
                Sports_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Skill Department':
                Skill_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'LSG Department':
                LSG_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Technical & Higher Education':
                Technical_Higher_Education_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031)  # List of years from 2020 to 2030

    context = {
    'year': selected_year,
    'clients': clients,  # Corrected variable name
    'yearly_data': yearly_data,
    'Sports_Department_monthly_data': Sports_Department_monthly_data,
    'Skill_Department_monthly_data': Skill_Department_monthly_data,
    'LSG_Department_monthly_data': LSG_Department_monthly_data,
    'Technical_Higher_Education_monthly_data': Technical_Higher_Education_monthly_data,
    'years': years,
}
    return render(request, 'projects/expenditure_analysis_client.html', context)
def amount_released_analysis_client(request):
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    clients = ['Sports Department', 'Skill Department', 'LSG Department', 'Technical & Higher Education']
    yearly_data = {client: 0 for client in clients}

    # Monthly data variables for each division
    Sports_Department_monthly_data = [0] * 12
    Skill_Department_monthly_data = [0] * 12
    LSG_Department_monthly_data = [0] * 12
    Technical_Higher_Education_monthly_data = [0] * 12

    for client in clients:
        # Calculate yearly amounts for the division
        yearly_amounts_data = AmountReleased.objects.filter(
            project__Client_Department=client,
            Amount_Released_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Released'))

        yearly_data[client] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        # Calculate monthly amounts for the division
        for month in range(1, 13):
            monthly_amounts_data = AmountReleased.objects.filter(
                project__Client_Department=client,
                Amount_Released_Date__year=selected_year,
                Amount_Released_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Released'))
            # Assign monthly amounts to respective division variables
            if client == 'Sports Department':
                Sports_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Skill Department':
                Skill_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'LSG Department':
                LSG_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Technical & Higher Education':
                Technical_Higher_Education_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031)  # List of years from 2020 to 2030

    context = {
    'year': selected_year,
    'clients': clients,  # Corrected variable name
    'yearly_data': yearly_data,
    'Sports_Department_monthly_data': Sports_Department_monthly_data,
    'Skill_Department_monthly_data': Skill_Department_monthly_data,
    'LSG_Department_monthly_data': LSG_Department_monthly_data,
    'Technical_Higher_Education_monthly_data': Technical_Higher_Education_monthly_data,
    'years': years,
}
    return render(request, 'projects/amount_released_analysis_client.html', context)
def amount_released_analysis_client(request):
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    clients = ['Sports Department', 'Skill Department', 'LSG Department', 'Technical & Higher Education']
    yearly_data = {client: 0 for client in clients}

    # Monthly data variables for each division
    Sports_Department_monthly_data = [0] * 12
    Skill_Department_monthly_data = [0] * 12
    LSG_Department_monthly_data = [0] * 12
    Technical_Higher_Education_monthly_data = [0] * 12

    for client in clients:
        # Calculate yearly amounts for the division
        yearly_amounts_data = AmountReleased.objects.filter(
            project__Client_Department=client,
            Amount_Released_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Released'))

        yearly_data[client] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        # Calculate monthly amounts for the division
        for month in range(1, 13):
            monthly_amounts_data = AmountReleased.objects.filter(
                project__Client_Department=client,
                Amount_Released_Date__year=selected_year,
                Amount_Released_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Released'))
            # Assign monthly amounts to respective division variables
            if client == 'Sports Department':
                Sports_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Skill Department':
                Skill_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'LSG Department':
                LSG_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Technical & Higher Education':
                Technical_Higher_Education_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031)  # List of years from 2020 to 2030

    context = {
    'year': selected_year,
    'clients': clients,  # Corrected variable name
    'yearly_data': yearly_data,
    'Sports_Department_monthly_data': Sports_Department_monthly_data,
    'Skill_Department_monthly_data': Skill_Department_monthly_data,
    'LSG_Department_monthly_data': LSG_Department_monthly_data,
    'Technical_Higher_Education_monthly_data': Technical_Higher_Education_monthly_data,
    'years': years,
}
    return render(request, 'projects/amount_released_analysis_client.html', context)
def amount_recieved_analysis_client(request):
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    clients = ['Sports Department', 'Skill Department', 'LSG Department', 'Technical & Higher Education']
    yearly_data = {client: 0 for client in clients}

    # Monthly data variables for each division
    Sports_Department_monthly_data = [0] * 12
    Skill_Department_monthly_data = [0] * 12
    LSG_Department_monthly_data = [0] * 12
    Technical_Higher_Education_monthly_data = [0] * 12

    for client in clients:
        # Calculate yearly amounts for the division
        yearly_amounts_data = AmountReceived.objects.filter(
            project__Client_Department=client,
            Amount_Received_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Received'))

        yearly_data[client] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        # Calculate monthly amounts for the division
        for month in range(1, 13):
            monthly_amounts_data = AmountReceived.objects.filter(
                project__Client_Department=client,
                Amount_Received_Date__year=selected_year,
                Amount_Received_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Received'))
            # Assign monthly amounts to respective division variables
            if client == 'Sports Department':
                Sports_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Skill Department':
                Skill_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'LSG Department':
                LSG_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Technical & Higher Education':
                Technical_Higher_Education_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031)  # List of years from 2020 to 2030

    context = {
    'year': selected_year,
    'clients': clients,  # Corrected variable name
    'yearly_data': yearly_data,
    'Sports_Department_monthly_data': Sports_Department_monthly_data,
    'Skill_Department_monthly_data': Skill_Department_monthly_data,
    'LSG_Department_monthly_data': LSG_Department_monthly_data,
    'Technical_Higher_Education_monthly_data': Technical_Higher_Education_monthly_data,
    'years': years,
}
    return render(request, 'projects/amount_recieved_analysis_client.html', context)

# ------------------------------ PROJECTS STOP ------------------------------ #



