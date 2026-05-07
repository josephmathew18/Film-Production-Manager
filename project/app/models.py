from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    validators=[MinValueValidator(1), MaxValueValidator(1000000)]
)

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    description = models.TextField()

    # ✅ PDF Upload
    script = models.FileField(upload_to='scripts/', null=True, blank=True)
    
    # ✅ Cover Image Upload
    image = models.ImageField(upload_to='project_images/', null=True, blank=True)

    written_by = models.CharField(max_length=100, null=True, blank=True)
    cinematography = models.CharField(max_length=100, null=True, blank=True)
    edited_by = models.CharField(max_length=100, null=True, blank=True)
    music_by = models.CharField(max_length=100, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    running_time = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title
# 🎭 Actor
class Actor(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# 📜 Scene
class Scene(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    duration = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    actors = models.ManyToManyField(Actor)

    def __str__(self):
        return self.title


# 📅 Schedule
class Schedule(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    date = models.DateField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.scene} - {self.date}"


# 💰 Expense
class Expense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.name

# 👤 User Profile (RBAC)
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('production_manager', 'Production Manager'),
        ('viewer', 'Viewer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, role='viewer')
    instance.userprofile.save()