from django.shortcuts import render, redirect ,reverse
from django.http import HttpResponse
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
from django.contrib import messages 
from django.db.models import Q
import calendar
from django.utils.timezone import now
from matplotlib.ticker import MaxNLocator
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.utils import timezone
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import View
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def dashboard(request):
    user =request.user
    if not request.user.is_authenticated:
        return redirect('login')
    # ,Is_Splited='Yes',Is_Splited='No'
    ongoing_count = Project.objects.filter(is_completed=False, is_handed_over=False).count()
    completed_count = Project.objects.filter(is_completed=True, is_handed_over=False).count()
    handedover_count = Project.objects.filter(is_completed=True, is_handed_over=True).count()
    notifications = Notification.objects.order_by('-Date', '-time')[:50]

    context = {
        'user' : user,
        'ongoing_count': ongoing_count,
        'completed_count': completed_count,
        'handedover_count': handedover_count,
        'notifications': notifications,
    }

    return render(request, 'dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('create_user')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('create_user')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('create_user')

        if user_type == 'local':
            is_active = True
            is_staff = False
        elif user_type == 'unit':
            is_active = True
            is_staff = True
        else:
            messages.error(request, 'Invalid user type selected.')
            return redirect('create_user')

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                is_active=is_active,
                is_staff=is_staff
            )
            messages.success(request, 'User created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating user: {e}')
            return redirect('create_user')
    return render(request, 'projects/create_user.html')
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

def projects(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    sprojects = Project.objects.filter(Is_Splited='Yes')
    projects = Project.objects.filter(Is_Splited='No')

    search_query = request.GET.get('search', None)
    
    if search_query:
        search_keywords = search_query.split()
        q_objects = Q()
        for keyword in search_keywords:
            q_objects |= Q(Name_Of_Project__icontains=keyword) | Q(A_and_F_Number__icontains=keyword) | Q(Technical_Sanctioned_Number__icontains=keyword) | Q(Work_order_Number__icontains=keyword)
        projects = projects.filter(q_objects)
        sprojects = sprojects.filter(q_objects)
    context = {
        'user': user,
        'projects': projects,
        'sprojects':sprojects,
    }
    
    return render(request, 'projects/projects_list.html', context)

def add_project(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
 
    if request.method == "POST":
        try:
            cd = request.POST["Client_Department"]
            dd = request.POST["Division"]
            bt = request.POST["Budget"]
            nop = request.POST["Name_Of_Project"]
            sa = request.POST["Sanctioned_Amount"]
            sad = request.POST["Sanctioned_Amount_Date"]
            tsa = request.POST.get("Technical_Sanctioned_Amount", "") if request.POST.get("split") != "Yes" else None
            tsad = request.POST.get("Technical_Sanctioned_Amount_Date", "") if request.POST.get("split") != "Yes" else None
            sd = request.POST["Start_date"] if request.POST.get("split") != "Yes" else None
            sdoc = request.POST["Stipulated_Date_Of_Completion"] if request.POST.get("split") != "Yes" else None
            woad = request.POST["Work_Order_Amount_Date"] if request.POST.get("split") != "Yes" else None
            woa = request.POST["Work_Order_Amount"] if request.POST.get("split") != "Yes" else None
            ldc = request.POST["Likely_Date_Of_Completion"] if request.POST.get("split") != "Yes" else None
            an = request.POST["A&F_number"]
            tsn = request.POST["Technical_Sanctioned_number"] if request.POST.get("split") != "Yes" else None
            won = request.POST["Work_Order_number"] if request.POST.get("split") != "Yes" else None
            fy = request.POST["Financial_Year"]
            sp = request.POST.get("split", "No") 

            sad_date = parse_date(sad)
            tsad_date = parse_date(tsad) if tsad else None
            sd_date = parse_date(sd) if sd else None
            sdoc_date = parse_date(sdoc) if sdoc else None
            woad_date = parse_date(woad) if woad else None
            ldc_date = parse_date(ldc) if ldc else None

            new_project = Project(
                Client_Department=cd,
                Division=dd,
                Budget_type =bt,
                Name_Of_Project=nop,
                A_and_F_Amount=sa,
                A_and_F_Date=sad_date,
                Technical_Sanctioned_Amount=tsa,
                Technical_Sanctioned_Date=tsad_date,
                Work_order_Date = woad_date,
                Work_order_Amount = woa,
                Start_date=sd_date,
                Stipulated_Date_Of_Completion=sdoc_date,
                Likely_Date_Of_Completion = ldc_date,
                A_and_F_Number = an,
                Technical_Sanctioned_Number = tsn,
                Work_order_Number = won,
                Financial_year = fy,
                Is_Splited = sp
            )
            new_project.save()
            notification = Notification(
                user = user,
                message=f"{user.username} has added a new project {nop}"
            )
            notification.save()
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
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = Project.objects.filter(pk = project_id)
    if project:
        project = Project.objects.get(pk = project_id)
        project.delete()
        notification = Notification(
                user = user,
                message=f"{user.username} has deleted the project {project.Name_Of_Project}"
             )
        notification.save()

    return redirect('projects')

def add_amount_received(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    project_instance = get_object_or_404(Project, pk=project_id) 
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
            user = request.user
            notification = Notification(
                user = user,
                project = project_instance,
                message=f"{user.username} has added an entry for amount received of Rs. {ra} Lacs dated {rad_date} for the project {project_instance.Name_Of_Project}"
             )
            notification.save()        
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
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
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
            user = request.user
            notification = Notification(
                user = user,
                project = project_instance,
                message=f"{user.username} has added an entry for amount released of Rs. {ra} Lacs dated {rad_date} for the project {project_instance.Name_Of_Project}"
             )
            notification.save() 
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
    latest_progress = PhysicalProgress.objects.filter(project=project_instance).order_by('-Date_Of_Reporting').first()

    if request.method == "POST":
        try:
            rad = request.POST["Date_Of_Reporting"]
            ra = float(request.POST["Physical_Progress_Percentage"])  

            rad_date = parse_date(rad)
            if latest_progress and ra < float(latest_progress.Physical_Progress_Percentage):
                error = f"Progress must be equal to or greater than the last recorded progress {latest_progress.Physical_Progress_Percentage}%."
                return render(request, "projects/add_progress.html", {"error": error})
            
            progress = PhysicalProgress(
                project=project_instance,
                Date_Of_Reporting=rad_date,
                Physical_Progress_Percentage=ra,
            )
            
            progress.save()
            user = request.user
            notification = Notification(
                user = user,
                project = project_instance,
                message=f"{user.username} has added an entry for Physical Progress of  {ra}% dated {rad_date} for the project {project_instance.Name_Of_Project}"
             )
            notification.save() 

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
    latest_progress = Expenditure.objects.filter(project=project_instance).order_by('-Expenditure_date').first()
    if request.method == "POST":
        try:
            expenditure_value = request.POST.get("expenditure_value")
            date_str = request.POST.get("expenditure_date")
            physical_progress = float(request.POST.get("physical_progress"))
            remarks = request.POST.get("remarks")
            photo = request.FILES.get("photo")

            date = parse_date(date_str)
            if latest_progress and physical_progress < float(latest_progress.physical_progress):
                error = f"Progress must be equal to or greater than the last recorded progress {latest_progress.physical_progress}%."
                return render(request, "projects/add_expenditure.html", {"error": error})
            expenditure = Expenditure(
                project=project_instance,
                Expenditure_date=date,
                Expenditure_Value=expenditure_value,
                physical_progress=physical_progress,
                remarks=remarks,
                photo=photo
            )
            
            expenditure.save()
            user = request.user
            notification = Notification(
                user = user,
                project = project_instance,
                message=f"{user.username} has added an entry for Expenditure of Rs. {expenditure_value} Lacs dated {date} for the project {project_instance.Name_Of_Project}"
             )
            notification.save() 
            success = f"Total expenditure of Rs. {expenditure_value} Lacs is successfully added for {date.strftime('%B %Y')}."
            return render(request, "projects/add_expenditure.html", {"success": success, "project": project_instance})
        
        except ValueError as e:
            error = f"Invalid input: {e}"
            return render(request, "projects/add_expenditure.html", {"error": error, "project": project_instance})
        except IntegrityError as e:
            error = f"Database Error: {e}"
            return render(request, "projects/add_expenditure.html", {"error": error, "project": project_instance})
        except ValidationError as e:
            error = f"Validation Error: {e}"
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
            plt.xticks(years_received, years_received, rotation=45) 
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) 
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
            plt.xticks(years_released, years_released, rotation=45)  
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) 
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
            plt.xticks(years_expenditure, years_expenditure, rotation=45) 
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  
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

    remaining_amount = project.Work_order_Amount - total_expenditure
    agencycharge =  project.Technical_Sanctioned_Amount*9/100

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
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
        
    sprojects = Project.objects.filter(Is_Splited='Yes')
    projects = Project.objects.filter(Is_Splited='No')
    search_query = request.GET.get('search', None)
    financial_year = request.GET.get('financial_year', None)

    if search_query:
        search_keywords = search_query.split()
        q_objects = Q()
        for keyword in search_keywords:
            q_objects |= Q(Name_Of_Project__icontains=keyword) | Q(A_and_F_Number__icontains=keyword) | Q(Technical_Sanctioned_Number__icontains=keyword) | Q(Work_order_Number__icontains=keyword)
        projects = projects.filter(q_objects)
        sprojects = sprojects.filter(q_objects)
    if financial_year:
        projects = projects.filter(Financial_year=financial_year)
        sprojects = sprojects.filter(Financial_year=financial_year)

    for project in projects:
        total_expenditures = Expenditure.objects.filter(project=project).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_AmountReleased = AmountReleased.objects.filter(project=project).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_AmountReceived = AmountReceived.objects.filter(project=project).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0
        project.total_expenditure_sum = total_expenditures 
        project.total_AmountReleased = total_AmountReleased
        project.total_AmountReceived = total_AmountReceived

    for sproject in sprojects:
        projs = Project.objects.filter(parent_project=sproject)
        if not projs.exists():
            sproject.total_technical_sanctioned_sum = 0
            sproject.total_work_order = 0
            sproject.total_expenditure_sum = 0
            sproject.total_AmountReleased = 0
            sproject.total_AmountReceived = 0
            continue

        total_technical_sanctioned = projs.aggregate(Sum('Technical_Sanctioned_Amount'))['Technical_Sanctioned_Amount__sum'] or 0
        total_work_order = projs.aggregate(Sum('Work_order_Amount'))['Work_order_Amount__sum'] or 0
        total_expenditure = Expenditure.objects.filter(project__in=projs).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_amountReleased = AmountReleased.objects.filter(project__in=projs).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_amountReceived = AmountReceived.objects.filter(project__in=projs).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0

        sproject.total_technical_sanctioned_sum = total_technical_sanctioned 
        sproject.total_work_order = total_work_order
        sproject.total_expenditure_sum = total_expenditure 
        sproject.total_AmountReleased = total_amountReleased
        sproject.total_AmountReceived = total_amountReceived

    context = {
        'user': user,
        'sprojects': sprojects,
        'projects': projects,
        'search_query': search_query,
        'financial_year': financial_year,
        'status': request.GET.get('status', ''),
        'ongoing':  False,
        'completed': False,
        'handed': False
    }
    return render(request, 'projects/view_project.html', context)
def edit_stipulated_date(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    
    status = ""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        if request.method == 'POST':
            new_likely_date = request.POST.get('Likely_Date')
            new_completion_date = request.POST.get('Completion_Date')
            new_handover_date = request.POST.get('Handover_Date')
            
            if new_likely_date:
                likelydate = LikelyDate(
                    project=project,
                    Likely_date=new_likely_date
                )
                likelydate.save()
                user = request.user
                notification = Notification(
                    user = user,
                    project = project,
                    message=f"{user.username} has added a new entry for Likely date of completion of {new_likely_date} for the project {project.Name_Of_Project}"
             )
                notification.save() 

                status = "Likely date of completion updated successfully."
            
            if new_completion_date:
                completiondate = CompletionDate(
                    project=project,
                    Completion_date=new_completion_date
                )
                completiondate.save()
                user = request.user
                notification = Notification(
                    user = user,
                    project = project,
                    message=f"{user.username} has added a new entry for date of completion of {new_completion_date} for the project {project.Name_Of_Project}"
             )
                notification.save() 
                status = "Date of completion updated successfully."
            
            if new_handover_date:
                handoverdate = HandoverDate(
                    project=project,
                    Handover_date=new_handover_date
                )
                handoverdate.save()
                user = request.user
                notification = Notification(
                    user = user,
                    project = project,
                    message=f"{user.username} has added a new entry for date of handover of {new_handover_date} for the project {project.Name_Of_Project}"
             )
                notification.save() 

                status = "Date of handover updated successfully."

        likely_date_entries = LikelyDate.objects.filter(project=project)
        completion_date_entries = CompletionDate.objects.filter(project=project)
        handover_date_entries = HandoverDate.objects.filter(project=project)
        
        context = {
            'project': project,
            'likely_date_entries': likely_date_entries,
            'completion_date_entries': completion_date_entries,
            'handover_date_entries': handover_date_entries,
            'status': status
        }
        
        return render(request, "projects/edit_date_of_completion.html", context)
    except KeyError as e:
        status = "Missing field: {}".format(e)
    except ValidationError as e:
        status = "Validation error: {}".format(e)
    except Exception as e:
        status = "An error occurred: {}".format(e)

    likely_date_entries = LikelyDate.objects.filter(project=project)
    completion_date_entries = CompletionDate.objects.filter(project=project)
    handover_date_entries = HandoverDate.objects.filter(project=project)
    
    return render(request, "projects/edit_date_of_completion.html", {
        'status': status,
        'project': project,
        'likely_date_entries': likely_date_entries,
        'completion_date_entries': completion_date_entries,
        'handover_date_entries': handover_date_entries
    })
def mark_project_completed(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    project = get_object_or_404(Project, id=project_id)
    project.is_completed = True
    project.save()  
    user = request.user
    notification = Notification(
        user = user,
        project = project,
        message=f"{user.username} has marked the project {project.Name_Of_Project} as COMPLETED "
    )
    notification.save() 
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
        project.remaining_amount = calculate_remaining_amount(project.A_and_F_Amount, total_expenditure)
    
    return recent_physical_progress

def calculate_remaining_amount(sanctioned_amount, total_expenditure):
    remaining_amount = sanctioned_amount - total_expenditure
    return remaining_amount

def mark_project_handedover(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    project = get_object_or_404(Project, id=project_id)
    project.is_handed_over = True
    project.save()  
    user = request.user
    notification = Notification(
    user = user,
    project = project,
    message=f"{user.username} has marked the project {project.Name_Of_Project} as HANDOVER "
    )
    notification.save() 

    status = "Project {} marked as handed over".format(project.Name_Of_Project)
    query_params = urlencode({'status': status, 'project': project.id})

    return redirect(f"{reverse('view_project')}?{query_params}")
def edit_project(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            user = request.user
            notification = Notification(
            user = user,
            project = project,
            message=f"{user.username} has edited the project {project.Name_Of_Project} "
                )
            notification.save() 

            status = f"Project '{project.Name_Of_Project}' is successfully edited."
            projects = Project.objects.filter(Is_Splited='No')
            sprojects = Project.objects.filter(Is_Splited='Yes')
            return render(request, 'projects/projects_list.html', {'projects': projects, 'status': status , 'sprojects': sprojects})
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

@login_required
def edit_amount_received(request, project_id):
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        amount_received = request.POST.get('amount_received')
        
        entry = get_object_or_404(AmountReceived, pk=entry_id)
        amount = entry.Amount_Received
        date = entry.Amount_Received_Date

        entry.Amount_Received = amount_received
        entry.Amount_Received_Date = entry.Amount_Received_Date  

        entry.save()
        user = request.user
        notification = Notification(
            user=user,
            project=project,
            message=f"{user.username} has edited amount received entry dated for {date} of amount Rs. {amount} Lacs to Rs. {amount_received} Lacs in the project {project.Name_Of_Project}"
        )
        notification.save()
        messages.success(request, 'Amount Received entry updated successfully.')
        return redirect('edit_amount_received', project_id=project.pk)

    amount_received_entries = project.amount_received.all()  
    return render(request, 'projects/edit_amountreceived.html', {
        'project': project,
        'amount_received_entries': amount_received_entries,
    })

@login_required
def delete_amount_received(request, project_id):
    user = request
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        entry = get_object_or_404(AmountReceived, pk=entry_id)
        amount = entry.Amount_Received
        date = entry.Amount_Received_Date
        entry.delete()
        user = request.user
        notification = Notification(
            user=user,
            project=project,
            message=f"{user.username} has deleted the amount received entry dated for {date} of amount Rs. {amount} Lacs in the project {project.Name_Of_Project}"
        )
        notification.save()
        messages.success(request, 'Amount received entry deleted successfully.')
    
    return redirect('edit_amount_received', project_id=project_id)

@login_required
def edit_amount_released(request, project_id):
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        amount_released = request.POST.get('amount_released')
        
        if entry_id:
            amount_released_entry = get_object_or_404(AmountReleased, pk=entry_id, project=project)
            old_amount = amount_released_entry.Amount_Released
            date = amount_released_entry.Amount_Released_Date
            amount_released_entry.Amount_Released = amount_released
            amount_released_entry.save()

            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has edited amount released entry from Rs. {old_amount} Lacs to Rs. {amount_released} Lacs dated for {date} in the project {project.Name_Of_Project}"
            )
            notification.save()

            messages.success(request, 'Amount released entry updated successfully.')
        else:
            messages.error(request, 'Invalid entry ID.')

    amount_released_entries = AmountReleased.objects.filter(project=project)
    context = {
        'project': project,
        'amount_released_entries': amount_released_entries,
    }
    return render(request, 'projects/edit_amountrelesed.html', context)

@login_required
def delete_amount_released(request, project_id):
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            amount_released_entry = get_object_or_404(AmountReleased, pk=entry_id, project=project)
            amount = amount_released_entry.Amount_Released
            date = amount_released_entry.Amount_Released_Date
            amount_released_entry.delete()

            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has deleted the amount released entry of Rs. {amount} Lacs dated for {date} in the project {project.Name_Of_Project}"
            )
            notification.save()

            messages.success(request, 'Amount released entry deleted successfully.')
        else:
            messages.error(request, 'Invalid entry ID.')
    return redirect('edit_amountreleased', project_id=project_id)

@login_required
def edit_physical_progress(request, project_id):
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    physical_progress_entries = project.physical_progress_entries.all()

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        physical_progress_entry = get_object_or_404(PhysicalProgress, pk=entry_id)

        physical_progress_percentage = request.POST.get('physical_progress_percentage')

        if physical_progress_percentage:
            old_percentage = physical_progress_entry.Physical_Progress_Percentage
            date = physical_progress_entry.Date_Of_Reporting
            physical_progress_entry.Physical_Progress_Percentage = physical_progress_percentage
            physical_progress_entry.save()

            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has edited physical progress percentage from {old_percentage}% to {physical_progress_percentage}%  dated for {date} in the project {project.Name_Of_Project}"
            )
            notification.save()

            messages.success(request, 'Physical Progress percentage updated successfully.')
            return redirect('edit_physical_progress', project_id=project_id)
        else:
            messages.error(request, 'Please fill in all fields.')
    else:
        form = None

    context = {
        'project': project,
        'physical_progress_entries': physical_progress_entries,
        'form': form,
    }
    return render(request, 'projects/edit_physical_progress.html', context)

@login_required
def delete_physical_progress(request, project_id):
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            physical_progress = get_object_or_404(PhysicalProgress, pk=entry_id)
            percentage = physical_progress.Physical_Progress_Percentage
            date = physical_progress.Date_Of_Reporting
            physical_progress.delete()

            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has deleted the physical progress entry of {percentage}% dates for {date} in the project {project.Name_Of_Project}"
            )
            notification.save()

            messages.success(request, 'Physical progress entry deleted successfully.')
        else:
            messages.error(request, 'Invalid physical progress entry ID.')
    
    return redirect('edit_physical_progress', project_id=project_id)

@login_required
def edit_expenditure(request, project_id):
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')

    project = get_object_or_404(Project, pk=project_id)
    expenditures = Expenditure.objects.filter(project=project)

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        expenditure_value = request.POST.get('expenditure_value')
        physical_progress = request.POST.get('physical_progress')
        remarks = request.POST.get('remarks')

        if not all([entry_id, expenditure_value, physical_progress, remarks]):
            messages.error(request, 'All fields are required.')
            return redirect('edit_expenditure', project_id=project_id)

        expenditure = get_object_or_404(Expenditure, pk=entry_id, project=project)
        old_value = expenditure.Expenditure_Value
        old_physical_progress = expenditure.physical_progress
        old_remarks = expenditure.remarks
        date = expenditure.Expenditure_date
        expenditure.Expenditure_Value = expenditure_value
        expenditure.physical_progress = physical_progress
        expenditure.remarks = remarks
        expenditure.save()

        user = request.user
        notification_message = (f"{user.username} has edited an expenditure entry on {date}:\n"
                                f"- Previous value: Rs. {old_value} Lacs\n"
                                f"- New value: Rs. {expenditure_value} Lacs\n"
                                f"- Previous progress: {old_physical_progress}%\n"
                                f"- New progress: {physical_progress}%\n"
                                f"- Previous remarks: {old_remarks}\n"
                                f"- New remarks: {remarks}\n"
                                f"In the project {project.Name_Of_Project}.")

        Notification.objects.create(
            user=user,
            project=project,
            message=notification_message
        )

        messages.success(request, 'Expenditure updated successfully.')
        return redirect('edit_expenditure', project_id=project_id)

    context = {
        'project': project,
        'expenditures': expenditures,
    }
    return render(request, 'projects/edit_expenditure.html', context)
@login_required
def delete_expenditure(request, project_id):
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            expenditure = get_object_or_404(Expenditure, pk=entry_id)
            value = expenditure.Expenditure_Value
            date = expenditure.Expenditure_date
            expenditure.delete()

            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has deleted the expenditure entry of Rs. {value} Lacs dated for {date} in the project {project.Name_Of_Project}"
            )
            notification.save()

            messages.success(request, 'Expenditure entry deleted successfully.')
        else:
            messages.error(request, 'Invalid expenditure entry ID.')
    
    return redirect('edit_expenditure', project_id=project_id)
def amount_released_analysis(request):
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    divisions = ['Udaipur', 'Jodhpur', 'Kota', 'Unit II', 'Unit III', 'Unit IV']
    yearly_data = {division: 0 for division in divisions}

    udaipur_monthly_data = [0] * 12
    jodhpur_monthly_data = [0] * 12
    kota_monthly_data = [0] * 12
    bikaner_monthly_data = [0] * 12
    jaipur_monthly_data = [0] * 12
    ajmer_monthly_data = [0] * 12


    for division in divisions:
        yearly_amounts_data = AmountReleased.objects.filter(
            Q(project__Division=division) | Q(project__parent_project__Division=division),
            Amount_Released_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Released'))

        yearly_data[division] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        for month in range(1, 13):
            monthly_amounts_data = AmountReleased.objects.filter(
                Q(project__Division=division) | Q(project__parent_project__Division=division),
                Amount_Released_Date__year=selected_year,
                Amount_Released_Date__month=month
                ).aggregate(total_amount=Sum('Amount_Released'))

            if division == 'Udaipur':
                udaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jodhpur':
                jodhpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Kota':
                kota_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit II':
                bikaner_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit III':
                jaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit IV':
                ajmer_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031) 

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
        'years': years,
    }
    return render(request, 'projects/amount_released_analysis.html', context)
def amount_recieved_analysis(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    divisions = ['Udaipur', 'Jodhpur', 'Kota', 'Unit II', 'Unit III', 'Unit IV']
    yearly_data = {division: 0 for division in divisions}

    udaipur_monthly_data = [0] * 12
    jodhpur_monthly_data = [0] * 12
    kota_monthly_data = [0] * 12
    bikaner_monthly_data = [0] * 12
    jaipur_monthly_data = [0] * 12
    ajmer_monthly_data = [0] * 12

    for division in divisions:
        yearly_amounts_data = AmountReceived.objects.filter(
            Q(project__Division=division) | Q(project__parent_project__Division=division),
            Amount_Received_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Received'))

        yearly_data[division] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        for month in range(1, 13):
            monthly_amounts_data = AmountReceived.objects.filter(
            Q(project__Division=division) | Q(project__parent_project__Division=division),
                Amount_Received_Date__year=selected_year,
                Amount_Received_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Received'))

            if division == 'Udaipur':
                udaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jodhpur':
                jodhpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Kota':
                kota_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit II':
                bikaner_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit III':
                jaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit IV':
                ajmer_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031) 
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
        'years': years,
    }
    return render(request, 'projects/amount_recieved_analysis.html', context)
def expenditure_analysis(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    divisions = ['Udaipur', 'Jodhpur', 'Kota', 'Unit II', 'Unit III', 'Unit IV']
    yearly_data = {division: 0 for division in divisions}

    udaipur_monthly_data = [0] * 12
    jodhpur_monthly_data = [0] * 12
    kota_monthly_data = [0] * 12
    bikaner_monthly_data = [0] * 12
    jaipur_monthly_data = [0] * 12
    ajmer_monthly_data = [0] * 12

    for division in divisions:
        yearly_amounts_data = Expenditure.objects.filter(
            Q(project__Division=division) | Q(project__parent_project__Division=division),
            Expenditure_date__year=selected_year
        ).aggregate(total_amount=Sum('Expenditure_Value'))

        yearly_data[division] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        for month in range(1, 13):
            monthly_amounts_data = Expenditure.objects.filter(
            Q(project__Division=division) | Q(project__parent_project__Division=division),
                Expenditure_date__year=selected_year,
                Expenditure_date__month=month
            ).aggregate(total_amount=Sum('Expenditure_Value'))

            if division == 'Udaipur':
                udaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Jodhpur':
                jodhpur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Kota':
                kota_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit II':
                bikaner_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit III':
                jaipur_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif division == 'Unit IV':
                ajmer_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0

    years = range(2020, 2031) 

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
        'years': years,
    }
    return render(request, 'projects/expenditure_analysis.html', context)
def expenditure_analysis_client(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    clients = [
        'Higher Education Department',
        'Department of Skill, Employment & Enterpreneurship',
        'Rajasthan State Sports Council',
        'Youth Affairs & Sports( Khelo India)',
        'Rajasthan State Pollution Control Board, Bhilwara',
        'Government Engineering College, Ajmer',
        'Government Engineering College, Jhalawar',
        'Shiksha Sankul Jaipur',
        'DMFT-GovernmentPG College, Nathdwara',
        'Rajasthan High Court Jodhpur',
        'Science & Technology Department',
        'ITI Ajmer',
        'ITI Sikar',
        'ITI Kishangarh',
        'LSG Department',
        'Industries Department'
    ]
    yearly_data = {client: 0 for client in clients}

    Sports_Department_monthly_data = [0] * 12
    Skill_Department_monthly_data = [0] * 12
    LSG_Department_monthly_data = [0] * 12
    Technical_Higher_Education_monthly_data = [0] * 12
    Rajasthan_State_Pollution = [0] * 12
    Government_Engineering_College_A = [0] * 12
    Government_Engineering_College_J = [0] * 12
    Shiksha_Sankul_Jaipur = [0] * 12
    DMFT_GovernmentPG =[0] * 12
    Rajasthan_High_Court = [0] * 12
    Science_Technology = [0] * 12
    ITI_Ajmer = [0] * 12
    ITI_Sikar = [0] * 12
    ITI_Kishangarh = [0] * 12
    LSG_client = [0] * 12
    Industries_Department = [0] * 12

    for client in clients:
        yearly_amounts_data = Expenditure.objects.filter(
            Q(project__Client_Department=client) | Q(project__parent_project__Client_Department=client),
            Expenditure_date__year=selected_year
        ).aggregate(total_amount=Sum('Expenditure_Value'))

        yearly_data[client] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        for month in range(1, 13):
            monthly_amounts_data = Expenditure.objects.filter(
                Q(project__Client_Department=client) | Q(project__parent_project__Client_Department=client),
                Expenditure_date__year=selected_year,
                Expenditure_date__month=month
            ).aggregate(total_amount=Sum('Expenditure_Value'))
            if client == 'Higher Education Department':
                Sports_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Department of Skill, Employment & Enterpreneurship':
                Skill_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan State Sports Council':
                LSG_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Youth Affairs & Sports( Khelo India)':
                Technical_Higher_Education_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan State Pollution Control Board, Bhilwara':
                Rajasthan_State_Pollution[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Government Engineering College, Ajmer':
                Government_Engineering_College_A[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Government Engineering College, Jhalawar':
                Government_Engineering_College_J[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Shiksha Sankul Jaipur':
                Shiksha_Sankul_Jaipur[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'DMFT-GovernmentPG College, Nathdwara':
                DMFT_GovernmentPG[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan High Court Jodhpur':
                Rajasthan_High_Court[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Science & Technology Department':
                Science_Technology[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Ajmer':
                ITI_Ajmer[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Sikar':
                ITI_Sikar[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Kishangarh':
                ITI_Kishangarh[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'LSG Department':
                LSG_client[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Industries Department':
                Industries_Department[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            

    years = range(2020, 2031) 

    context = {
    'year': selected_year,
    'clients': clients, 
    'yearly_data': yearly_data,
    'Sports_Department_monthly_data': Sports_Department_monthly_data,
    'Skill_Department_monthly_data': Skill_Department_monthly_data,
    'LSG_Department_monthly_data': LSG_Department_monthly_data,
    'Technical_Higher_Education_monthly_data': Technical_Higher_Education_monthly_data,
    'Rajasthan_State_Pollution':Rajasthan_State_Pollution,
    'Government_Engineering_College_A':Government_Engineering_College_A,
    'Government_Engineering_College_J':Government_Engineering_College_J,
    'Shiksha_Sankul_Jaipur':Shiksha_Sankul_Jaipur,
    'DMFT_GovernmentPG':DMFT_GovernmentPG,
    'Rajasthan_High_Court':Rajasthan_High_Court,
    'Science_Technology':Science_Technology,
    'ITI_Ajmer':ITI_Ajmer,
    'ITI_Sikar':ITI_Sikar,
    'ITI_Kishangarh':ITI_Kishangarh,
    'LSG_client':LSG_client,
    'Industries_Department':Industries_Department,
    'years': years,
}
    return render(request, 'projects/expenditure_analysis_client.html', context)
def amount_released_analysis_client(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    clients = [
        'Higher Education Department',
        'Department of Skill, Employment & Enterpreneurship',
        'Rajasthan State Sports Council',
        'Youth Affairs & Sports( Khelo India)',
        'Rajasthan State Pollution Control Board, Bhilwara',
        'Government Engineering College, Ajmer',
        'Government Engineering College, Jhalawar',
        'Shiksha Sankul Jaipur',
        'DMFT-GovernmentPG College, Nathdwara',
        'Rajasthan High Court Jodhpur',
        'Science & Technology Department',
        'ITI Ajmer',
        'ITI Sikar',
        'ITI Kishangarh',
        'LSG Department',
        'Industries Department'
    ]
    yearly_data = {client: 0 for client in clients}

    Sports_Department_monthly_data = [0] * 12
    Skill_Department_monthly_data = [0] * 12
    LSG_Department_monthly_data = [0] * 12
    Technical_Higher_Education_monthly_data = [0] * 12
    Rajasthan_State_Pollution = [0] * 12
    Government_Engineering_College_A = [0] * 12
    Government_Engineering_College_J = [0] * 12
    Shiksha_Sankul_Jaipur = [0] * 12
    DMFT_GovernmentPG = [0] * 12
    Rajasthan_High_Court = [0] * 12
    Science_Technology = [0] * 12
    ITI_Ajmer = [0] * 12
    ITI_Sikar = [0] * 12
    ITI_Kishangarh = [0] * 12
    LSG_client = [0] * 12
    Industries_Department = [0] * 12

    for client in clients:
        yearly_amounts_data = AmountReleased.objects.filter(
            Q(project__Client_Department=client) | Q(project__parent_project__Client_Department=client),
            Amount_Released_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Released'))

        yearly_data[client] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        for month in range(1, 13):
            monthly_amounts_data = AmountReleased.objects.filter(
                Q(project__Client_Department=client) | Q(project__parent_project__Client_Department=client),
                Amount_Released_Date__year=selected_year,
                Amount_Released_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Released'))
            if client == 'Higher Education Department':
                Sports_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Department of Skill, Employment & Enterpreneurship':
                Skill_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan State Sports Council':
                LSG_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Youth Affairs & Sports( Khelo India)':
                Technical_Higher_Education_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan State Pollution Control Board, Bhilwara':
                Rajasthan_State_Pollution[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Government Engineering College, Ajmer':
                Government_Engineering_College_A[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Government Engineering College, Jhalawar':
                Government_Engineering_College_J[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Shiksha Sankul Jaipur':
                Shiksha_Sankul_Jaipur[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'DMFT-GovernmentPG College, Nathdwara':
                DMFT_GovernmentPG[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan High Court Jodhpur':
                Rajasthan_High_Court[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Science & Technology Department':
                Science_Technology[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Ajmer':
                ITI_Ajmer[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Sikar':
                ITI_Sikar[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Kishangarh':
                ITI_Kishangarh[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'LSG Department':
                LSG_client[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Industries Department':
                Industries_Department[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            

    years = range(2020, 2031) 

    context = {
    'year': selected_year,
    'clients': clients, 
    'yearly_data': yearly_data,
    'Sports_Department_monthly_data': Sports_Department_monthly_data,
    'Skill_Department_monthly_data': Skill_Department_monthly_data,
    'LSG_Department_monthly_data': LSG_Department_monthly_data,
    'Technical_Higher_Education_monthly_data': Technical_Higher_Education_monthly_data,
    'Rajasthan_State_Pollution':Rajasthan_State_Pollution,
    'Government_Engineering_College_A':Government_Engineering_College_A,
    'Government_Engineering_College_J':Government_Engineering_College_J,
    'Shiksha_Sankul_Jaipur':Shiksha_Sankul_Jaipur,
    'DMFT_GovernmentPG':DMFT_GovernmentPG,
    'Rajasthan_High_Court':Rajasthan_High_Court,
    'Science_Technology':Science_Technology,
    'ITI_Ajmer':ITI_Ajmer,
    'ITI_Sikar':ITI_Sikar,
    'ITI_Kishangarh':ITI_Kishangarh,
    'LSG_client':LSG_client,
    'Industries_Department':Industries_Department,
    'years': years,
}
    return render(request, 'projects/amount_released_analysis_client.html', context)
def amount_recieved_analysis_client(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))

    clients = [
        'Higher Education Department',
        'Department of Skill, Employment & Enterpreneurship',
        'Rajasthan State Sports Council',
        'Youth Affairs & Sports( Khelo India)',
        'Rajasthan State Pollution Control Board, Bhilwara',
        'Government Engineering College, Ajmer',
        'Government Engineering College, Jhalawar',
        'Shiksha Sankul Jaipur',
        'DMFT-GovernmentPG College, Nathdwara',
        'Rajasthan High Court Jodhpur',
        'Science & Technology Department',
        'ITI Ajmer',
        'ITI Sikar',
        'ITI Kishangarh',
        'LSG Department',
        'Industries Department'
    ]
    yearly_data = {client: 0 for client in clients}

    Sports_Department_monthly_data = [0] * 12
    Skill_Department_monthly_data = [0] * 12
    LSG_Department_monthly_data = [0] * 12
    Technical_Higher_Education_monthly_data = [0] * 12
    Rajasthan_State_Pollution = [0] * 12
    Government_Engineering_College_A = [0] * 12
    Government_Engineering_College_J = [0] * 12
    Shiksha_Sankul_Jaipur = [0] * 12
    DMFT_GovernmentPG = [0] * 12
    Rajasthan_High_Court = [0] * 12
    Science_Technology = [0] * 12
    ITI_Ajmer = [0] * 12
    ITI_Sikar = [0] * 12
    ITI_Kishangarh = [0] * 12
    LSG_client = [0] * 12
    Industries_Department = [0] * 12

    for client in clients:
        yearly_amounts_data = AmountReceived.objects.filter(
            Q(project__Client_Department=client) | Q(project__parent_project__Client_Department=client),
            Amount_Received_Date__year=selected_year
        ).aggregate(total_amount=Sum('Amount_Received'))

        yearly_data[client] = yearly_amounts_data['total_amount'] if yearly_amounts_data['total_amount'] else 0

        for month in range(1, 13):
            monthly_amounts_data = AmountReceived.objects.filter(
                Q(project__Client_Department=client) | Q(project__parent_project__Client_Department=client),
                Amount_Received_Date__year=selected_year,
                Amount_Received_Date__month=month
            ).aggregate(total_amount=Sum('Amount_Received'))
            if client == 'Higher Education Department':
                Sports_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Department of Skill, Employment & Enterpreneurship':
                Skill_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan State Sports Council':
                LSG_Department_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Youth Affairs & Sports( Khelo India)':
                Technical_Higher_Education_monthly_data[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan State Pollution Control Board, Bhilwara':
                Rajasthan_State_Pollution[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Government Engineering College, Ajmer':
                Government_Engineering_College_A[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Government Engineering College, Jhalawar':
                Government_Engineering_College_J[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Shiksha Sankul Jaipur':
                Shiksha_Sankul_Jaipur[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'DMFT-GovernmentPG College, Nathdwara':
                DMFT_GovernmentPG[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Rajasthan High Court Jodhpur':
                Rajasthan_High_Court[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Science & Technology Department':
                Science_Technology[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Ajmer':
                ITI_Ajmer[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Sikar':
                ITI_Sikar[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'ITI Kishangarh':
                ITI_Kishangarh[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'LSG Department':
                LSG_client[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            elif client == 'Industries Department':
                Industries_Department[month - 1] = monthly_amounts_data['total_amount'] if monthly_amounts_data['total_amount'] else 0
            

    years = range(2020, 2031) 

    context = {
    'year': selected_year,
    'clients': clients, 
    'yearly_data': yearly_data,
    'Sports_Department_monthly_data': Sports_Department_monthly_data,
    'Skill_Department_monthly_data': Skill_Department_monthly_data,
    'LSG_Department_monthly_data': LSG_Department_monthly_data,
    'Technical_Higher_Education_monthly_data': Technical_Higher_Education_monthly_data,
    'Rajasthan_State_Pollution':Rajasthan_State_Pollution,
    'Government_Engineering_College_A':Government_Engineering_College_A,
    'Government_Engineering_College_J':Government_Engineering_College_J,
    'Shiksha_Sankul_Jaipur':Shiksha_Sankul_Jaipur,
    'DMFT_GovernmentPG':DMFT_GovernmentPG,
    'Rajasthan_High_Court':Rajasthan_High_Court,
    'Science_Technology':Science_Technology,
    'ITI_Ajmer':ITI_Ajmer,
    'ITI_Sikar':ITI_Sikar,
    'ITI_Kishangarh':ITI_Kishangarh,
    'LSG_client':LSG_client,
    'Industries_Department':Industries_Department,
    'years': years,
}
    return render(request, 'projects/amount_recieved_analysis_client.html', context)
def notification(request):
    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.order_by('-Date', '-time')[:50]

    context = {
        'notifications': notifications,
    }

    return render(request, 'notification.html', context)
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return result.getvalue()
    return None
class GenerateProjectPDF(View):
    def get(self,request,pk):
        project = get_object_or_404(Project, id=pk)
    
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
            plt.xticks(years_received, years_received, rotation=45)  
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) 
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
            plt.xticks(years_released, years_released, rotation=45)  
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) 
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
            plt.xticks(years_expenditure, years_expenditure, rotation=45)  
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) 
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
        project = Project.objects.get(id=pk)
    
        total_amount_received = AmountReceived.objects.filter(project=project).aggregate(total=Sum('Amount_Received'))['total'] or 0
    
        total_amount_released = AmountReleased.objects.filter(project=project).aggregate(total=Sum('Amount_Released'))['total'] or 0
    
        total_expenditure = Expenditure.objects.filter(project=project).aggregate(total=Sum('Expenditure_Value'))['total'] or 0

        remaining_amount = project.Work_order_Amount - total_expenditure
        agencycharge =  project.Technical_Sanctioned_Amount*9/100

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
    }
        template = get_template('projects/project_pdf.html')
        html = template.render(context)

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'{project.Name_Of_Project}_details_{selected_year}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return HttpResponse('Error rendering PDF', status=500)
    
def not_allowed(request):
    return render(request, 'not_allowed.html')

def add_split_project(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    parent_project = get_object_or_404(Project, pk=project_id)
    success = None
    if request.method == 'POST':
        name_of_project = request.POST.get('Name_Of_Project')
        tech_sanction_date = request.POST.get('Technical_Sanctioned_Amount_Date')
        tech_sanction_amount = request.POST.get('Technical_Sanctioned_Amount')
        work_order_date = request.POST.get('Work_Order_Amount_Date')
        work_order_amount = request.POST.get('Work_Order_Amount')
        start_date = request.POST.get('Start_date')
        stipulated_completion_date = request.POST.get('Stipulated_Date_Of_Completion')
        likely_completion_date = request.POST.get('Likely_Date_Of_Completion')
        tsn = request.POST.get('Technical_Sanctioned_number')
        won = request.POST.get('Work_Order_number')
        if not all([name_of_project, tech_sanction_date, tech_sanction_amount, work_order_date,
                    work_order_amount, start_date, stipulated_completion_date, likely_completion_date, tsn, won]):
            return HttpResponseBadRequest('All fields are required.')

        try:
            tech_sanction_date = parse_date(tech_sanction_date)
            work_order_date = parse_date(work_order_date)
            start_date = parse_date(start_date)
            stipulated_completion_date = parse_date(stipulated_completion_date)
            likely_completion_date = parse_date(likely_completion_date)
        except ValueError:
            return HttpResponseBadRequest('Invalid date format.')

        if tech_sanction_date > start_date:
            return HttpResponseBadRequest('Technical sanctioned date cannot be after start date.')

        if work_order_date > start_date:
            return HttpResponseBadRequest('Work order date cannot be after start date.')

        if likely_completion_date < stipulated_completion_date:
            return HttpResponseBadRequest('Likely completion date cannot be before stipulated completion date.')

        project = Project(
            parent_project=parent_project,
            Name_Of_Project=name_of_project,
            Technical_Sanctioned_Date=tech_sanction_date,
            Technical_Sanctioned_Amount=tech_sanction_amount,
            Work_order_Date=work_order_date,
            Work_order_Amount=work_order_amount,
            Start_date=start_date,
            Stipulated_Date_Of_Completion=stipulated_completion_date,
            Likely_Date_Of_Completion=likely_completion_date,
            Technical_Sanctioned_Number=tsn,
            Work_order_Number=won,
        )
        project.save()
        notification = Notification(
            user=user,
            message=f"{user.username} has added a new project {name_of_project}"
        )
        notification.save()
        success = f"Project '{name_of_project}' has been successfully added added to {parent_project.Name_Of_Project}"

    context = {
        'project_id': project_id,
        'success': success
    }
    return render(request, 'projects/add_split_project.html', context)

def add_split_amountrecieved(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    proj = get_object_or_404(Project, pk=project_id)
    projects = Project.objects.filter(parent_project=proj)
    success = None
    if request.method == "POST":
        try:
            pj = request.POST["Project"]
            rad = request.POST["Recieved_Amount_Date"]
            ra = request.POST["Recieved_Amount"]

            project = get_object_or_404(Project, pk=pj)
            rad_date = parse_date(rad)

            data = AmountReceived(
                project=project,
                Amount_Received_Date=rad_date, 
                Amount_Received=ra,
            )
            data.save()
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has added an entry for amount received of Rs. {ra} Lacs dated {rad_date} for the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
            )
            notification.save()
            success = f"Amount of Rs. {ra} lacs is successfully added for the project {project.Name_Of_Project}"
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    context = {
        'projects': projects,
        'project_id': project_id,
        'success': success
    }
    return render(request, 'projects/add_split_amountrecieved.html', context)

def add_split_amountreleased(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    proj = get_object_or_404(Project, pk=project_id)
    projects = Project.objects.filter(parent_project=proj)
    success = None
    if request.method == "POST":
        try:
            pj = request.POST["Project"]
            rad = request.POST["Recieved_Amount_Date"]
            ra = request.POST["Recieved_Amount"]

            project = get_object_or_404(Project, pk=pj)
            rad_date = parse_date(rad)

            data = AmountReleased(
                project= project,
                Amount_Released_Date=rad_date, 
                Amount_Released=ra,
            )
            data.save()
            user = request.user
            notification = Notification(
                user = user,
                project = project,
                message=f"{user.username} has added an entry for amount released of Rs. {ra} Lacs dated {rad_date} for the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
             )
            notification.save()
            success = f"Amount of Rs. {ra} lacs is successfully added for the project {project.Name_Of_Project}"
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    context = {
        'projects': projects,
        'project_id': project_id,
        'success':success
    }
    return render(request, 'projects/add_split_amountreleased.html', context)
def add_split_expenditure(request,project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    proj = get_object_or_404(Project, pk=project_id)
    projects = Project.objects.filter(parent_project=proj)
    success = None
    if request.method == "POST":
        try:
            pj = request.POST["Project"]
            expenditure_value = float(request.POST.get("expenditure_value"))
            date_str = request.POST.get("expenditure_date")
            physical_progress = float(request.POST.get("physical_progress"))
            remarks = request.POST.get("remarks")
            photo = request.FILES.get("photo")
            
            project = get_object_or_404(Project, pk=pj)
            date = parse_date(date_str)
            latest_progress = Expenditure.objects.filter(project=project).order_by('-Expenditure_date').first()
            
            if latest_progress and physical_progress < float(latest_progress.physical_progress):
                error = f"Progress must be equal to or greater than the last recorded progress {latest_progress.physical_progress}%."
                return render(request, "projects/add_split_expenditure.html", {"error": error, 'projects': projects, 'project_id': project_id})

            expenditure = Expenditure(
                project=project,
                Expenditure_date=date,
                Expenditure_Value=expenditure_value,
                physical_progress=physical_progress,
                remarks=remarks,
                photo=photo
            )
            
            expenditure.save()
            user = request.user
            notification = Notification(
                user = user,
                project = project,
                message=f"{user.username} has added an entry for Expenditure of Rs. {expenditure_value} Lacs dated {date} for the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
             )
            notification.save()
            success = f"Amount of Rs. {expenditure_value} lacs is successfully added for the project {project.Name_Of_Project}"
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    context = {
        'projects': projects,
        'project_id': project_id,
        'success':success
    }
    return render(request, 'projects/add_split_expenditure.html', context)

def add_split_progress(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    
    proj = get_object_or_404(Project, pk=project_id)
    projects = Project.objects.filter(parent_project=proj)
    success = None

    if request.method == "POST":
        try:
            pj = request.POST["Project"]
            rad = request.POST["Date_Of_Reporting"]
            ra = float(request.POST["Physical_Progress_Percentage"]) 

            project = get_object_or_404(Project, pk=pj)
            rad_date = parse_date(rad)
            latest_progress = PhysicalProgress.objects.filter(project=project).order_by('-Date_Of_Reporting').first()

            if latest_progress and ra < float(latest_progress.Physical_Progress_Percentage):
                error = f"Progress must be equal to or greater than the last recorded progress {latest_progress.Physical_Progress_Percentage}%."
                return render(request, "projects/add_split_progress.html", {"error": error, 'projects': projects, 'project_id': project_id})

            data = PhysicalProgress(
                project=project,
                Date_Of_Reporting=rad_date,
                Physical_Progress_Percentage=ra,
            )
            data.save()
            
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has added an entry for Physical Progress of {ra}% dated {rad_date} for the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
            )
            notification.save()

            success = f"Physical Progress of {ra}% is successfully added for the project {project.Name_Of_Project}"
        
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    context = {
        'projects': projects,
        'project_id': project_id,
        'success': success
    }
    return render(request, 'projects/add_split_progress.html', context)

def edit_split_project(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if not user.is_superuser:
        return redirect('not_allowed')
    parent_proj = get_object_or_404(Project, pk=project_id)
    sub_projects = Project.objects.filter(parent_project=parent_proj)
    
    if request.method == 'POST':
        form = SplitProjectForm(request.POST, instance=parent_proj)
        if form.is_valid():
            form.save()
            status = f"Project '{parent_proj.Name_Of_Project}' is successfully edited."
            projects = Project.objects.filter(Is_Splited='No')
            sprojects = Project.objects.filter(Is_Splited='Yes')
            return render(request, 'projects/projects_list.html', {'projects': projects, 'status': status , 'sprojects': sprojects})
    else:
        form = SplitProjectForm(instance=parent_proj)
        status = ""
        
    context = {
        'form': form,
        'projects': sub_projects,
        'project_id': project_id,
        'status': status,
        'parent_proj':parent_proj
    }

    return render(request, 'projects/edit_split_project.html', context)

def edit_sproject(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if not user.is_superuser:
        return redirect('not_allowed')
    project = get_object_or_404(Project, id=project_id)
    id = project.parent_project.id
    if request.method == 'POST':
        form = SProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            status = f"Project '{project.Name_Of_Project}' is successfully edited."
            user=request.user
            notification = Notification(
            user = user,
            project = project,
            message=f"{user.username} has edited the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}  "
                )
            notification.save()

            return render(request, 'projects/edit_sproject.html', { 'form': form,'id':id , 'project_id': project_id, 'status': status})
    else:
        form = SProjectForm(instance=project)
        status = ""
    
    context = {
        'form': form,
        'project_id': project_id,
        'status': status,
        'id':id
    }
    return render(request, 'projects/edit_sproject.html', context)

@login_required
def edit_split_amount_received(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')
    
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        amount_received = request.POST.get('amount_received')
        
        entry = get_object_or_404(AmountReceived, pk=entry_id)
        old_amount = entry.Amount_Received
        entry.Amount_Received = amount_received
        entry.save()
        user = request.user
        notification = Notification(
            user=user,
            project=project,
            message=f"{user.username} has edited amount received entry dated for {date} of amount Rs. {old_amount} Lacs to Rs. {amount_received} Lacs in the project  {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
        )
        notification.save()
        messages.success(request, f"Amount Received entry updated successfully to {amount_received}.")
        return redirect('edit_split_amount_received', project_id=project.pk)

    amount_received_entries = project.amount_received.all()  
    return render(request, 'projects/edit_split_amountrecieved.html', {
        'project': project,
        'amount_received_entries': amount_received_entries,
    })

@login_required
def delete_split_amount_received(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')
    
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        entry = get_object_or_404(AmountReceived, pk=entry_id)
        amount = entry.Amount_Received
        entry.delete()
        user = request.user
        notification = Notification(
            user=user,
            project=project,
            message=f"{user.username} has deleted amount received entry dated for {date} of amount Rs. {amount_received} Lacs in the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
        )
        notification.save()
        messages.success(request, f"Amount received entry '{amount}' deleted successfully.")
    
    return redirect('edit_split_amount_received', project_id=project_id)

@login_required
def edit_split_amount_released(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')
    
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        amount_released = request.POST.get('amount_released')
        
        if entry_id:
            entry = get_object_or_404(AmountReleased, pk=entry_id, project=project)
            old_amount = entry.Amount_Released
            entry.Amount_Released = amount_released
            entry.save()
            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has edited amount released entry from Rs. {old_amount} Lacs to Rs. {amount_released} Lacs dated for {date} in the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
            )
            notification.save()
            messages.success(request, f"Amount released entry updated successfully to {amount_released}.")
        else:
            messages.error(request, 'Invalid entry ID.')

    amount_released_entries = AmountReleased.objects.filter(project=project)
    context = {
        'project': project,
        'amount_released_entries': amount_released_entries,
    }
    return render(request, 'projects/edit_split_amountreleased.html', context)

@login_required
def delete_split_amount_released(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')
    
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            entry = get_object_or_404(AmountReleased, pk=entry_id, project=project)
            amount = entry.Amount_Released
            entry.delete()
            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has deleted the amount released entry of Rs. {amount} Lacs dated for {date} in the project  {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
            )
            notification.save()
            messages.success(request, f"Amount released entry '{amount}' deleted successfully.")
        else:
            messages.error(request, 'Invalid entry ID.')
    
    return redirect('edit_split_amount_released', project_id=project_id)

@login_required
def edit_split_physical_progress(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')
    
    project = get_object_or_404(Project, pk=project_id)
    physical_progress_entries = project.physical_progress_entries.all()

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        physical_progress_entry = get_object_or_404(PhysicalProgress, pk=entry_id)

        physical_progress_percentage = request.POST.get('physical_progress_percentage')

        if physical_progress_percentage:
            old_percentage = physical_progress_entry.Physical_Progress_Percentage
            physical_progress_entry.Physical_Progress_Percentage = physical_progress_percentage
            physical_progress_entry.save()
            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has edited physical progress percentage from {old_percentage}% to {physical_progress_percentage}%  dated for {date} in the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
            )
            notification.save()
            messages.success(request, f"Physical Progress percentage updated successfully to {physical_progress_percentage}.")
            return redirect('edit_split_physical_progress', project_id=project_id)
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'project': project,
        'physical_progress_entries': physical_progress_entries,
    }
    return render(request, 'projects/edit_split_progress.html', context)

@login_required
def delete_split_physical_progress(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')
    
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            entry = get_object_or_404(PhysicalProgress, pk=entry_id)
            percentage = entry.Physical_Progress_Percentage
            entry.delete()
            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has deleted the physical progress entry of {percentage}% dates for {date} in the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
            )
            notification.save()
            messages.success(request, f"Physical progress entry '{percentage}%' deleted successfully.")
        else:
            messages.error(request, 'Invalid physical progress entry ID.')
    
    return redirect('edit_split_physical_progress', project_id=project_id)

@login_required
def edit_split_expenditure(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_superuser:
        return redirect('not_allowed')

    project = get_object_or_404(Project, pk=project_id)
    expenditures = Expenditure.objects.filter(project=project)

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        expenditure_value = request.POST.get('expenditure_value')
        physical_progress = request.POST.get('physical_progress')
        remarks = request.POST.get('remarks')

        if not all([entry_id, expenditure_value, physical_progress, remarks]):
            messages.error(request, 'All fields are required.')
            return redirect('edit_split_expenditure', project_id=project_id)

        expenditure = get_object_or_404(Expenditure, pk=entry_id, project=project)
        old_value = expenditure.Expenditure_Value
        old_physical_progress = expenditure.physical_progress
        old_remarks = expenditure.remarks
        expenditure.Expenditure_Value = expenditure_value
        expenditure.physical_progress = physical_progress
        expenditure.remarks = remarks
        expenditure.save()
        user = request.user
        notification_message = (f"{user.username} has edited an expenditure entry on {date}:\n"
                                f"- Previous value: Rs. {old_value} Lacs\n"
                                f"- New value: Rs. {expenditure_value} Lacs\n"
                                f"- Previous progress: {old_physical_progress}%\n"
                                f"- New progress: {physical_progress}%\n"
                                f"- Previous remarks: {old_remarks}\n"
                                f"- New remarks: {remarks}\n"
                                f"In the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}.")

        Notification.objects.create(
            user=user,
            project=project,
            message=notification_message
        )
        messages.success(request, f"Expenditure updated successfully to {expenditure_value}.")
        return redirect('edit_split_expenditure', project_id=project_id)

    context = {
        'project': project,
        'expenditures': expenditures,
    }
    return render(request, 'projects/edit_split_expenditure.html', context)

@login_required
def delete_split_expenditure(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and user.is_staff and not user.is_superuser:
        return redirect('not_allowed')
    
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            entry = get_object_or_404(Expenditure, pk=entry_id)
            value = entry.Expenditure_Value
            entry.delete()
            user = request.user
            notification = Notification(
                user=user,
                project=project,
                message=f"{user.username} has deleted the expenditure entry of Rs. {value} Lacs dated for {date} in the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
            )
            notification.save()
            messages.success(request, f"Expenditure entry '{value}' deleted successfully.")
        else:
            messages.error(request, 'Invalid expenditure entry ID.')
    
    return redirect('edit_split_expenditure', project_id=project_id)
def view_split_project(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    parent_proj = get_object_or_404(Project, pk=project_id)
    sub_projects = Project.objects.filter(parent_project=parent_proj)

    for project in sub_projects:
        total_expenditures = Expenditure.objects.filter(project=project).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_AmountReleased = AmountReleased.objects.filter(project=project).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_AmountReceived = AmountReceived.objects.filter(project=project).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0
        project.total_expenditure_sum = total_expenditures 
        project.total_AmountReleased = total_AmountReleased
        project.total_AmountReceived = total_AmountReceived

    search_query = request.GET.get('search', None)
    if search_query:
        search_keywords = search_query.split()
        q_objects = Q()
        for keyword in search_keywords:
            q_objects |= Q(Name_Of_Project__icontains=keyword) | Q(A_and_F_Number__icontains=keyword) | Q(Technical_Sanctioned_Number__icontains=keyword) | Q(Work_order_Number__icontains=keyword)
        sub_projects = sub_projects.filter(q_objects)

    context = {
        'projects': sub_projects,
        'project_id': project_id,
        'parent_proj': parent_proj,
        'status': request.GET.get('status', '') 
    }

    return render(request, 'projects/view_split_project.html', context)
def add_split_dates(request, project_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    
    status = ""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        if request.method == 'POST':
            new_likely_date = request.POST.get('Likely_Date')
            new_completion_date = request.POST.get('Completion_Date')
            new_handover_date = request.POST.get('Handover_Date')
            
            if new_likely_date:
                likelydate = LikelyDate(
                    project=project,
                    Likely_date=new_likely_date
                )
                likelydate.save()
                user = request.user
                notification = Notification(
                    user = user,
                    project = project,
                    message=f"{user.username} has added a new entry for Likely date of completion of {new_likely_date} for the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
             )
                notification.save() 

                status = "Likely date of completion updated successfully."
            
            if new_completion_date:
                completiondate = CompletionDate(
                    project=project,
                    Completion_date=new_completion_date
                )
                completiondate.save()
                user = request.user
                notification = Notification(
                    user = user,
                    project = project,
                    message=f"{user.username} has added a new entry for date of completion of {new_completion_date} for the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
             )
                notification.save() 
                status = "Date of completion updated successfully."
            
            if new_handover_date:
                handoverdate = HandoverDate(
                    project=project,
                    Handover_date=new_handover_date
                )
                handoverdate.save()
                user = request.user
                notification = Notification(
                    user = user,
                    project = project,
                    message=f"{user.username} has added a new entry for date of handover of {new_handover_date} for the project {project.parent_project.Name_Of_Project} -> {project.Name_Of_Project}"
             )
                notification.save() 

                status = "Date of handover updated successfully."

        likely_date_entries = LikelyDate.objects.filter(project=project)
        completion_date_entries = CompletionDate.objects.filter(project=project)
        handover_date_entries = HandoverDate.objects.filter(project=project)
        proj_id = project.parent_project.id
        context = {
            'project': project,
            'likely_date_entries': likely_date_entries,
            'completion_date_entries': completion_date_entries,
            'handover_date_entries': handover_date_entries,
            'status': status,
            'project_id':proj_id
        }
        
        return render(request, "projects/add_split_dates.html", context)
    
    except KeyError as e:
        status = "Missing field: {}".format(e)
    except ValidationError as e:
        status = "Validation error: {}".format(e)
    except Exception as e:
        status = "An error occurred: {}".format(e)

    likely_date_entries = LikelyDate.objects.filter(project=project)
    completion_date_entries = CompletionDate.objects.filter(project=project)
    handover_date_entries = HandoverDate.objects.filter(project=project)
    
    return render(request, "projects/add_split_dates.html", {
        'status': status,
        'project': project,
        'likely_date_entries': likely_date_entries,
        'completion_date_entries': completion_date_entries,
        'handover_date_entries': handover_date_entries,
        'project_id':proj_id
    })
def view_split_details(request,project_id):
    
    if not request.user.is_authenticated:
        return redirect('login')
     
    project = get_object_or_404(Project, id=project_id)
    proj_id = project.parent_project.id
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
            plt.xticks(years_received, years_received, rotation=45) 
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  
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
            plt.xticks(years_released, years_released, rotation=45) 
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True)) 
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
            plt.xticks(years_expenditure, years_expenditure, rotation=45) 
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
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

    remaining_amount = project.Work_order_Amount - total_expenditure
    agencycharge =  project.Technical_Sanctioned_Amount*9/100

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
        'project_id':proj_id
    }

    return render(request, 'projects/view_split_details.html', context)

class splitGenerateProjectPDF(View):
    def get(self,request,pk):
        project = get_object_or_404(Project, id=pk)
    
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
            plt.xticks(years_received, years_received, rotation=45)
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  
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
            plt.xticks(years_released, years_released, rotation=45)  
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  
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
            plt.xticks(years_expenditure, years_expenditure, rotation=45)  
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  
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
        project = Project.objects.get(id=pk)
    
        total_amount_received = AmountReceived.objects.filter(project=project).aggregate(total=Sum('Amount_Received'))['total'] or 0
    
        total_amount_released = AmountReleased.objects.filter(project=project).aggregate(total=Sum('Amount_Released'))['total'] or 0
    
        total_expenditure = Expenditure.objects.filter(project=project).aggregate(total=Sum('Expenditure_Value'))['total'] or 0

        remaining_amount = project.Work_order_Amount - total_expenditure
        agencycharge =  project.Technical_Sanctioned_Amount*9/100

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
    }
        template = get_template('projects/split_project_pdf.html')
        html = template.render(context)

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'{project.Name_Of_Project}_details.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return HttpResponse('Error rendering PDF', status=500)
def mark_split_project_completed(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    project.is_completed = True
    project.save()  
    notification = Notification(
        user=user,
        project=project,
        message=f"{user.username} has marked the project {project.Name_Of_Project} as COMPLETED"
    )
    notification.save() 
    status = f"Project {project.Name_Of_Project} marked as completed"
    query_params = urlencode({'status': status})

    return redirect(f"{reverse('view_split_project', args=[project.parent_project.id])}?{query_params}")

def mark_split_project_handedover(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if user.is_active and not (user.is_staff or user.is_superuser):
        return redirect('not_allowed')
    project = get_object_or_404(Project, pk=project_id)
    project.is_handed_over = True
    project.save()  
    notification = Notification(
        user=user,
        project=project,
        message=f"{user.username} has marked the project {project.Name_Of_Project} as HANDOVER"
    )
    notification.save() 
    status = f"Project {project.Name_Of_Project} marked as handed over"
    query_params = urlencode({'status': status})

    return redirect(f"{reverse('view_split_project', args=[project.parent_project.id])}?{query_params}")
def completed_projects(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
        
    sprojects = Project.objects.filter(Is_Splited='Yes',is_completed = True , is_handed_over = False)
    projects = Project.objects.filter(Is_Splited='No',is_completed = True , is_handed_over = False)
    search_query = request.GET.get('search', None)
    financial_year = request.GET.get('financial_year', None)

    if search_query:
        search_keywords = search_query.split()
        q_objects = Q()
        for keyword in search_keywords:
            q_objects |= Q(Name_Of_Project__icontains=keyword) | Q(A_and_F_Number__icontains=keyword) | Q(Technical_Sanctioned_Number__icontains=keyword) | Q(Work_order_Number__icontains=keyword)
        projects = projects.filter(q_objects)
        sprojects = sprojects.filter(q_objects)
    if financial_year:
        projects = projects.filter(Financial_year=financial_year)
        sprojects = sprojects.filter(Financial_year=financial_year)

    for project in projects:
        total_expenditures = Expenditure.objects.filter(project=project).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_AmountReleased = AmountReleased.objects.filter(project=project).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_AmountReceived = AmountReceived.objects.filter(project=project).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0
        project.total_expenditure_sum = total_expenditures 
        project.total_AmountReleased = total_AmountReleased
        project.total_AmountReceived = total_AmountReceived

    for sproject in sprojects:
        projs = Project.objects.filter(parent_project=sproject)
        if not projs.exists():
            sproject.total_technical_sanctioned_sum = 0
            sproject.total_work_order = 0
            sproject.total_expenditure_sum = 0
            sproject.total_AmountReleased = 0
            sproject.total_AmountReceived = 0
            continue

        total_technical_sanctioned = projs.aggregate(Sum('Technical_Sanctioned_Amount'))['Technical_Sanctioned_Amount__sum'] or 0
        total_work_order = projs.aggregate(Sum('Work_order_Amount'))['Work_order_Amount__sum'] or 0
        total_expenditure = Expenditure.objects.filter(project__in=projs).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_amountReleased = AmountReleased.objects.filter(project__in=projs).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_amountReceived = AmountReceived.objects.filter(project__in=projs).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0

        sproject.total_technical_sanctioned_sum = total_technical_sanctioned 
        sproject.total_work_order = total_work_order
        sproject.total_expenditure_sum = total_expenditure 
        sproject.total_AmountReleased = total_amountReleased
        sproject.total_AmountReceived = total_amountReceived

    context = {
        'user': user,
        'sprojects': sprojects,
        'projects': projects,
        'search_query': search_query,
        'financial_year': financial_year,
        'status': request.GET.get('status', '') ,
        'completed':True
    }
    return render(request, 'projects/view_project.html', context)

def ongoing_projects(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
        
    sprojects = Project.objects.filter(Is_Splited='Yes',is_completed = False , is_handed_over = False)
    projects = Project.objects.filter(Is_Splited='No',is_completed = False , is_handed_over = False)
    search_query = request.GET.get('search', None)
    financial_year = request.GET.get('financial_year', None)

    if search_query:
        search_keywords = search_query.split()
        q_objects = Q()
        for keyword in search_keywords:
            q_objects |= Q(Name_Of_Project__icontains=keyword) | Q(A_and_F_Number__icontains=keyword) | Q(Technical_Sanctioned_Number__icontains=keyword) | Q(Work_order_Number__icontains=keyword)
        projects = projects.filter(q_objects)
        sprojects = sprojects.filter(q_objects)
    if financial_year:
        projects = projects.filter(Financial_year=financial_year)
        sprojects = sprojects.filter(Financial_year=financial_year)

    for project in projects:
        total_expenditures = Expenditure.objects.filter(project=project).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_AmountReleased = AmountReleased.objects.filter(project=project).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_AmountReceived = AmountReceived.objects.filter(project=project).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0
        project.total_expenditure_sum = total_expenditures 
        project.total_AmountReleased = total_AmountReleased
        project.total_AmountReceived = total_AmountReceived

    for sproject in sprojects:
        projs = Project.objects.filter(parent_project=sproject)
        if not projs.exists():
            sproject.total_technical_sanctioned_sum = 0
            sproject.total_work_order = 0
            sproject.total_expenditure_sum = 0
            sproject.total_AmountReleased = 0
            sproject.total_AmountReceived = 0
            continue

        total_technical_sanctioned = projs.aggregate(Sum('Technical_Sanctioned_Amount'))['Technical_Sanctioned_Amount__sum'] or 0
        total_work_order = projs.aggregate(Sum('Work_order_Amount'))['Work_order_Amount__sum'] or 0
        total_expenditure = Expenditure.objects.filter(project__in=projs).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_amountReleased = AmountReleased.objects.filter(project__in=projs).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_amountReceived = AmountReceived.objects.filter(project__in=projs).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0

        sproject.total_technical_sanctioned_sum = total_technical_sanctioned 
        sproject.total_work_order = total_work_order
        sproject.total_expenditure_sum = total_expenditure 
        sproject.total_AmountReleased = total_amountReleased
        sproject.total_AmountReceived = total_amountReceived

    context = {
        'user': user,
        'sprojects': sprojects,
        'projects': projects,
        'search_query': search_query,
        'financial_year': financial_year,
        'status': request.GET.get('status', '') ,
        'ongoing':True
    }
    return render(request, 'projects/view_project.html', context)
def Handover_projects(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
        
    sprojects = Project.objects.filter(Is_Splited='Yes',is_completed = True , is_handed_over = True)
    projects = Project.objects.filter(Is_Splited='No',is_completed = True , is_handed_over = True)
    search_query = request.GET.get('search', None)
    financial_year = request.GET.get('financial_year', None)

    if search_query:
        search_keywords = search_query.split()
        q_objects = Q()
        for keyword in search_keywords:
            q_objects |= Q(Name_Of_Project__icontains=keyword) | Q(A_and_F_Number__icontains=keyword) | Q(Technical_Sanctioned_Number__icontains=keyword) | Q(Work_order_Number__icontains=keyword)
        projects = projects.filter(q_objects)
        sprojects = sprojects.filter(q_objects)
    if financial_year:
        projects = projects.filter(Financial_year=financial_year)
        sprojects = sprojects.filter(Financial_year=financial_year)

    for project in projects:
        total_expenditures = Expenditure.objects.filter(project=project).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_AmountReleased = AmountReleased.objects.filter(project=project).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_AmountReceived = AmountReceived.objects.filter(project=project).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0
        project.total_expenditure_sum = total_expenditures 
        project.total_AmountReleased = total_AmountReleased
        project.total_AmountReceived = total_AmountReceived

    for sproject in sprojects:
        projs = Project.objects.filter(parent_project=sproject)
        if not projs.exists():
            sproject.total_technical_sanctioned_sum = 0
            sproject.total_work_order = 0
            sproject.total_expenditure_sum = 0
            sproject.total_AmountReleased = 0
            sproject.total_AmountReceived = 0
            continue

        total_technical_sanctioned = projs.aggregate(Sum('Technical_Sanctioned_Amount'))['Technical_Sanctioned_Amount__sum'] or 0
        total_work_order = projs.aggregate(Sum('Work_order_Amount'))['Work_order_Amount__sum'] or 0
        total_expenditure = Expenditure.objects.filter(project__in=projs).aggregate(Sum('Expenditure_Value'))['Expenditure_Value__sum'] or 0
        total_amountReleased = AmountReleased.objects.filter(project__in=projs).aggregate(Sum('Amount_Released'))['Amount_Released__sum'] or 0
        total_amountReceived = AmountReceived.objects.filter(project__in=projs).aggregate(Sum('Amount_Received'))['Amount_Received__sum'] or 0

        sproject.total_technical_sanctioned_sum = total_technical_sanctioned 
        sproject.total_work_order = total_work_order
        sproject.total_expenditure_sum = total_expenditure 
        sproject.total_AmountReleased = total_amountReleased
        sproject.total_AmountReceived = total_amountReceived

    context = {
        'user': user,
        'sprojects': sprojects,
        'projects': projects,
        'search_query': search_query,
        'financial_year': financial_year,
        'status': request.GET.get('status', '') ,
        'handed':True
    }
    return render(request, 'projects/view_project.html', context)


