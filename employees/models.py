from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default = None)
    birth_date = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    leaves = models.IntegerField(default = 1)
    photo = models.FileField(null=True, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.user.username


# Choices for Client Department and Division
CLIENT_DEPARTMENT = (
    ("1", "Sports Department"),
    ("2", "Skill Department"),
    ("3", "LSG Department"),
    ("4", "Technical & Higher Education"),
)
DIVISION = (
    ("1", "Udaipur"),
    ("2", "Jodhpur"),
    ("3", "Kota"),
    ("4", "Bikaner"),
    ("5", "Jaipur"),
    ("6", "Ajmer"),
    ("7", "Bharatpur"),
    
)

# Project Model
class Project(models.Model):
    Client_Department = models.CharField(
        max_length=40,
        choices=CLIENT_DEPARTMENT,
        default='1'
    )
    Division = models.CharField(
        max_length=40,
        choices=DIVISION,
        default='1'
    )
    Name_Of_Project = models.CharField(max_length=50)
    Sanctioned_Amount = models.FloatField(default=0)
    Sanctioned_Amount_Date = models.DateField(default=datetime.date.today)
    Technical_Sanctioned_Amount = models.FloatField(default=0)
    Technical_Sanctioned_Amount_Date = models.DateField(default=datetime.date.today)
    Work_order_Amount = models.FloatField(default=0)
    Work_order_Amount_Date = models.DateField(default=datetime.date.today)
    Start_date = models.DateField(default=datetime.date.today)
    Stipulated_Date_Of_Completion = models.DateField(default=datetime.date.today)
    is_completed = models.BooleanField(default=False)
    is_handed_over = models.BooleanField(default=False)


    def __str__(self):
        return self.Name_Of_Project

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

# AmountReceived Model
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

    class Meta:
        verbose_name = 'Expenditure'
        verbose_name_plural = 'Expenditure'

    def __str__(self):
        return f" {self.Expenditure_date}%"
