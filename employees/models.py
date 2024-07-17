from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default = None)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.user.username


# Choices for Client Department and Division
CLIENT_DEPARTMENT = (
    ("Sports Department", "Sports Department"),
    ("Skill Department", "Skill Department"),
    ("LSG Department", "LSG Department"),
    ("Technical & Higher Education", "Technical & Higher Education"),
)
DIVISION = (
    ("Udaipur", "Udaipur"),
    ("Jodhpur", "Jodhpur"),
    ("Kota", "Kota"),
    ("Unit II", "Unit II"),
    ("Unit III", "Unit III"),
    ("Unit IV", "Unit IV"),
    
)
BUDGET_TYPE = (
    ("Budget Ghoshna", "Budget Ghoshna"),
    ("Non Budget Ghoshna", "Non Budget Ghoshna"),
)
FINANCIAL_YEAR = [
    ("2016-2017", "2016-2017"),
    ("2017-2018", "2017-2018"),
    ("2018-2019", "2018-2019"),
    ("2019-2020", "2019-2020"),
    ("2020-2021", "2020-2021"),
    ("2021-2022", "2021-2022"),
    ("2022-2023", "2022-2023"),
    ("2023-2024", "2023-2024"),
    ("2024-2025", "2024-2025"),
    ("2025-2026", "2025-2026"),
    ("2026-2027", "2026-2027"),
    ("2027-2028", "2027-2028"),
    ("2028-2029", "2028-2029"),
    ("2029-2030", "2029-2030"),
    ("2030-2031", "2030-2031"),
]
SPLITING = [
    ("Yes", "Yes"),
    ("No", "No"),
]

# Project Model
class Project(models.Model):
    parent_project = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_projects')
    Client_Department = models.CharField(
        max_length=40,
        choices=CLIENT_DEPARTMENT,
        null=True, blank=True
    )
    Division = models.CharField(
        max_length=40,
        choices=DIVISION,
        null=True, blank=True
    )
    Budget_type = models.CharField(
        max_length=40,
        choices=BUDGET_TYPE,
        null=True, blank=True
    )
    Financial_year = models.CharField(
        max_length=40,
        choices=FINANCIAL_YEAR,
        null=True, blank=True
    )
    Name_Of_Project = models.CharField(max_length=50,null=True, blank=True)
    A_and_F_Amount = models.FloatField( db_column='A&F_Amount', verbose_name='A&F Amount',null=True, blank=True)
    A_and_F_Date = models.DateField( db_column='A&F_Date',verbose_name='A&F Date',null=True, blank=True)
    A_and_F_Number = models.CharField(max_length=50, db_column='A&F_Number',verbose_name='A&F Number',null=True, blank=True)
    Is_Splited = models.CharField(
        max_length=40,
        choices=SPLITING,
     null=True, blank=True
    )

    Technical_Sanctioned_Amount = models.FloatField(null=True, blank=True)
    Technical_Sanctioned_Date = models.DateField(default=datetime.date.today, null=True, blank=True)
    Technical_Sanctioned_Number = models.CharField(max_length=50,null=True, blank=True)
    Work_order_Amount = models.FloatField(null=True, blank=True)
    Work_order_Date = models.DateField(default=datetime.date.today, null=True, blank=True)
    Work_order_Number = models.CharField(max_length=50,null=True, blank=True)
    Start_date = models.DateField(default=datetime.date.today, null=True, blank=True)
    Stipulated_Date_Of_Completion = models.DateField(default=datetime.date.today, null=True, blank=True)
    is_completed = models.BooleanField(default=False, null=True, blank=True)
    is_handed_over = models.BooleanField(default=False, null=True, blank=True)
    Likely_Date_Of_Completion = models.DateField(default=datetime.date.today, null=True, blank=True)
    Reporting_Date = models.DateField(default=datetime.date.today, editable=False, null=True, blank=True)



    def __str__(self):
        return self.Name_Of_Project

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

class AmountReceived(models.Model):
    project = models.ForeignKey(Project, related_name='amount_received', on_delete=models.CASCADE)
    Amount_Received_Date = models.DateField()
    Amount_Received = models.FloatField()

    class Meta:
        verbose_name = 'Amount Received'
        verbose_name_plural = 'Amounts Received'

    def __str__(self):
        return f"{self.project.Name_Of_Project} - {self.Amount_Received_Date}: {self.Amount_Received}"

class AmountReleased(models.Model):
    project = models.ForeignKey(Project, related_name='amount_released', on_delete=models.CASCADE)
    Amount_Released_Date = models.DateField()
    Amount_Released = models.FloatField()

    class Meta:
        verbose_name = 'Amount Released'
        verbose_name_plural = 'Amounts Released'

    def __str__(self):
        return f"{self.project.Name_Of_Project} - {self.Amount_Released_Date}: {self.Amount_Released}"

class PhysicalProgress(models.Model):
    project = models.ForeignKey(Project, related_name='physical_progress_entries', on_delete=models.CASCADE)
    Date_Of_Reporting = models.DateField()
    Physical_Progress_Percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        verbose_name = 'Physical Progress'
        verbose_name_plural = 'Physical Progress'

    def __str__(self):
        return f"{self.project.Name_Of_Project} - {self.Date_Of_Reporting}: {self.Physical_Progress_Percentage}%"

class Expenditure(models.Model):
    project = models.ForeignKey(Project, related_name='Expenditure', on_delete=models.CASCADE)
    Expenditure_date = models.DateField()
    Expenditure_Value = models.FloatField(default=0)
    physical_progress = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    remarks = models.CharField(max_length=1000 , blank = True)
    photo = models.ImageField(upload_to='Expenditure/', blank = True)

    class Meta:
        verbose_name = 'Expenditure'
        verbose_name_plural = 'Expenditure'

    def __str__(self):
        return f" {self.Expenditure_date}%"
class LikelyDate(models.Model):
    project = models.ForeignKey(Project, related_name='Likely_Date', on_delete=models.CASCADE)
    Likely_date = models.DateField()
    Date = models.DateField(default=datetime.date.today, editable=False)

    class Meta:
        verbose_name = 'Likely_Date'
        verbose_name_plural = 'Likely_Date'

    def __str__(self):
        return f" {self.Likely_date}"
class CompletionDate(models.Model):
    project = models.ForeignKey(Project, related_name='Completion_date', on_delete=models.CASCADE)
    Completion_date = models.DateField()
    Date = models.DateField(default=datetime.date.today, editable=False)

    class Meta:
        verbose_name = 'Completion_date'
        verbose_name_plural = 'Completion_date'

    def __str__(self):
        return f" {self.Completion_date}"
class HandoverDate(models.Model):
    project = models.ForeignKey(Project, related_name='Handover_date', on_delete=models.CASCADE)
    Handover_date = models.DateField()
    Date = models.DateField(default=datetime.date.today, editable=False)

    class Meta:
        verbose_name = 'Handover_date'
        verbose_name_plural = 'Handover_date'

    def __str__(self):
        return f" {self.Handover_date}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default = None)
    project = models.ForeignKey(Project, related_name='Notification', on_delete=models.CASCADE,null = True,blank = True)
    message = models.CharField(max_length=1000 , blank = True)
    Date = models.DateField(default=datetime.date.today, editable=False)
    time = models.TimeField(default=timezone.localtime, editable=False)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notification'

    def __str__(self):
        return f" {self.user.username}"

