from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from .models import Project, Expense, Actor, Scene, Schedule
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users

@login_required(login_url='/login/')
def dashboard(request):
    expenses = Expense.objects.filter(project__user=request.user).select_related('project') if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Expense.objects.all().select_related('project')
    
    project_id = request.GET.get('project_id')
    if project_id:
        expenses = expenses.filter(project_id=project_id)
        
    expenses = expenses.order_by('project__title', '-date')
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    projects = Project.objects.filter(user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Project.objects.all()

    return render(request, 'dashboard.html', {
        'expenses': expenses,
        'total': total,
        'projects': projects,
        'selected_project_id': int(project_id) if project_id else None
    })

@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def add_expense(request):
    projects = Project.objects.filter(user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Project.objects.all()

    if request.method == 'POST':
        Expense.objects.create(
            project_id=request.POST.get('project'),
            name=request.POST.get('name'),
            amount=request.POST.get('amount'),
            category=request.POST.get('category'),
            date=request.POST.get('date')
        )
        return redirect('/dashboard/')   # ✅ IMPORTANT

    return render(request, 'add_expense.html', {'projects': projects})




def register_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'userprofile'):
            if request.user.userprofile.role == 'admin':
                return redirect('/admin-dashboard/')
            elif request.user.userprofile.role == 'production_manager':
                return redirect('/manager-dashboard/')
        return redirect('/home/')

    if request.method == 'POST':
        from django.contrib.auth.models import User
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if role not in ['production_manager', 'viewer']:
            return render(request, 'register.html', {'error': 'Invalid role selected.'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists.'})

        user = User.objects.create_user(username=username, password=password)
        
        # Ensure role is set correctly (overriding default signal)
        if hasattr(user, 'userprofile'):
            user.userprofile.role = role
            user.userprofile.save()

        login(request, user)
        return redirect('/home/')

    return render(request, 'register.html')

def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'userprofile'):
            if request.user.userprofile.role == 'admin':
                return redirect('/admin-dashboard/')
            elif request.user.userprofile.role == 'production_manager':
                return redirect('/manager-dashboard/')
        return redirect('/home/')
        
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            next_url = request.GET.get('next')
            if not next_url:
                if hasattr(user, 'userprofile'):
                    if user.userprofile.role == 'admin':
                        next_url = '/admin-dashboard/'
                    elif user.userprofile.role == 'production_manager':
                        next_url = '/manager-dashboard/'
                    else:
                        next_url = '/home/'
                else:
                    next_url = '/home/'
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required(login_url='/login/')
@allowed_users(['admin'])
def admin_dashboard(request):
    from django.contrib.auth.models import User
    total_projects = Project.objects.count()
    total_users = User.objects.count()
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    recent_projects = Project.objects.order_by('-id')[:5]

    return render(request, 'admin_dashboard.html', {
        'total_projects': total_projects,
        'total_users': total_users,
        'total_expenses': total_expenses,
        'recent_projects': recent_projects
    })

@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def manager_dashboard(request):
    recent_projects = Project.objects.order_by('-id')[:6]
    return render(request, 'manager_dashboard.html', {
        'recent_projects': recent_projects
    })


def logout_view(request):
    logout(request)
    return redirect('/')

# READ
@login_required(login_url='/login/')
def home(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
        projects = Project.objects.filter(user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Project.objects.all()
    else:
        projects = Project.objects.all()
    return render(request, 'home.html', {'projects': projects})


# CREATE
@login_required(login_url='/login/')
@allowed_users(['admin'])
def add_project(request):
    if request.method == 'POST':
        project = Project.objects.create(
            user=request.user,
            title=request.POST['title'],
            genre=request.POST['genre'],
            director=request.POST['director'],
            description=request.POST['description'],
            script=request.FILES.get('script'),   # ✅ IMPORTANT
            image=request.FILES.get('image'),      # ✅ IMPORTANT
            written_by=request.POST.get('written_by'),
            cinematography=request.POST.get('cinematography'),
            edited_by=request.POST.get('edited_by'),
            music_by=request.POST.get('music_by'),
            release_date=request.POST.get('release_date') or None,
            language=request.POST.get('language'),
            running_time=request.POST.get('running_time')
        )
        return redirect(f'/project/{project.id}/')

    return render(request, 'add_project.html')
    
# UPDATE
@login_required(login_url='/login/')
@allowed_users(['admin'])
def update_project(request, id):
    try:
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
            project = Project.objects.get(id=id, user=request.user)
        else:
            project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return redirect('/home/')

    if request.method == 'POST':
        project.title = request.POST['title']
        project.genre = request.POST['genre']
        project.director = request.POST['director']
        project.description = request.POST['description']
        
        project.written_by = request.POST.get('written_by')
        project.cinematography = request.POST.get('cinematography')
        project.edited_by = request.POST.get('edited_by')
        project.music_by = request.POST.get('music_by')
        project.release_date = request.POST.get('release_date') or None
        project.language = request.POST.get('language')
        project.running_time = request.POST.get('running_time')
        
        # Check if a new script file was uploaded
        if request.FILES.get('script'):
            project.script = request.FILES.get('script')
            
        # Check if a new image was uploaded
        if request.FILES.get('image'):
            project.image = request.FILES.get('image')
            
        project.save()
        return redirect('/home/')

    return render(request, 'update_project.html', {
        'project': project
    })


# DELETE
@login_required(login_url='/login/')
@allowed_users(['admin'])
def delete_project(request, id):
    try:
        Project.objects.get(id=id, user=request.user).delete()
    except Project.DoesNotExist:
        pass
    return redirect('/home/')

# --- PROJECT DETAILS HUB ---
@login_required(login_url='/login/')
def project_details(request, id):
    try:
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
            project = Project.objects.get(id=id, user=request.user)
        else:
            project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return redirect('/home/')
        
    actors = Actor.objects.filter(project=project)
    scenes = Scene.objects.filter(project=project)
    schedules = Schedule.objects.filter(scene__project=project).order_by('date')
    
    return render(request, 'project_details.html', {
        'project': project,
        'actors': actors,
        'scenes': scenes,
        'schedules': schedules
    })

# --- ACTORS ---
@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def add_actor(request, project_id=None):
    if project_id:
        try:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
                project = Project.objects.get(id=project_id, user=request.user)
            else:
                project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return redirect('/home/')
        projects = None
    else:
        project = None
        projects = Project.objects.filter(user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Project.objects.all()

    if request.method == 'POST':
        pid = project_id if project_id else request.POST.get('project')
        try:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
                p = Project.objects.get(id=pid, user=request.user)
            else:
                p = Project.objects.get(id=pid)
        except Project.DoesNotExist:
            return redirect('/home/')
            
        Actor.objects.create(
            name=request.POST['name'],
            role=request.POST['role'],
            contact=request.POST['contact'],
            project=p
        )
        return redirect(f'/project/{pid}/')

    return render(request, 'add_actor.html', {'project': project, 'projects': projects})

@login_required(login_url='/login/')
@allowed_users(['admin'])
def delete_actor(request, id):
    try:
        actor = Actor.objects.get(id=id, project__user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Actor.objects.get(id=id)
        project_id = actor.project.id
        actor.delete()
        return redirect(f'/project/{project_id}/')
    except Actor.DoesNotExist:
        pass
    return redirect('/home/')


# --- SCENES ---
@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def add_scene(request, project_id=None):
    if project_id:
        try:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
                project = Project.objects.get(id=project_id, user=request.user)
            else:
                project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return redirect('/home/')
        projects = None
        actors = Actor.objects.filter(project=project)
    else:
        project = None
        projects = Project.objects.filter(user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Project.objects.all()
        actors = Actor.objects.filter(project__user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Actor.objects.all()

    if request.method == 'POST':
        pid = project_id if project_id else request.POST.get('project')
        try:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
                p = Project.objects.get(id=pid, user=request.user)
            else:
                p = Project.objects.get(id=pid)
        except Project.DoesNotExist:
            return redirect('/home/')
            
        scene = Scene.objects.create(
            project=p,
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            duration=request.POST['duration'],
            status=request.POST.get('status', 'pending')
        )
        selected_actors = request.POST.getlist('actors')
        if selected_actors:
            scene.actors.set(selected_actors)
            
        return redirect(f'/project/{pid}/')

    return render(request, 'add_scene.html', {'project': project, 'projects': projects, 'actors': actors})

@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def update_scene(request, id):
    try:
        scene = Scene.objects.get(id=id, project__user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Scene.objects.get(id=id)
        project = scene.project
    except Scene.DoesNotExist:
        return redirect('/home/')

    all_actors = Actor.objects.filter(project=project)

    if request.method == 'POST':
        scene.title = request.POST['title']
        scene.description = request.POST['description']
        scene.location = request.POST['location']
        scene.duration = request.POST['duration']
        scene.status = request.POST.get('status', 'pending')
        scene.save()
        
        selected_actors = request.POST.getlist('actors')
        scene.actors.set(selected_actors)
            
        return redirect(f'/project/{project.id}/')

    return render(request, 'update_scene.html', {
        'scene': scene, 
        'project': project,
        'all_actors': all_actors,
    })

@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def delete_scene(request, id):
    try:
        scene = Scene.objects.get(id=id, project__user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Scene.objects.get(id=id)
        project_id = scene.project.id
        scene.delete()
        return redirect(f'/project/{project_id}/')
    except Scene.DoesNotExist:
        pass
    return redirect('/home/')


# --- SCHEDULES ---
@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def add_schedule(request, project_id=None):
    if project_id:
        try:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
                project = Project.objects.get(id=project_id, user=request.user)
            else:
                project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return redirect('/home/')
        projects = None
        scenes = Scene.objects.filter(project=project)
    else:
        project = None
        projects = Project.objects.filter(user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Project.objects.all()
        scenes = Scene.objects.filter(project__user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Scene.objects.all()

    if request.method == 'POST':
        scene_id = request.POST['scene']
        try:
            scene = Scene.objects.get(id=scene_id, project__user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Scene.objects.get(id=scene_id)
            pid = scene.project.id
        except Scene.DoesNotExist:
            return redirect('/home/')
            
        Schedule.objects.create(
            scene_id=scene.id,
            date=request.POST['date'],
            location=request.POST['location']
        )
        return redirect(f'/project/{pid}/')

    return render(request, 'add_schedule.html', {'project': project, 'projects': projects, 'scenes': scenes})

@login_required(login_url='/login/')
@allowed_users(['admin', 'production_manager'])
def delete_schedule(request, id):
    try:
        schedule = Schedule.objects.get(id=id, scene__project__user=request.user) if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin' else Schedule.objects.get(id=id)
        project_id = schedule.scene.project.id
        schedule.delete()
        return redirect(f'/project/{project_id}/')
    except Schedule.DoesNotExist:
        pass
    return redirect('/home/')
