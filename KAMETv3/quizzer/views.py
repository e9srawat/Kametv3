import random
from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .models import *
from django.views.generic import *
from django.contrib.auth import authenticate, login, logout
from .forms import loginForm
from django.contrib.auth.mixins import LoginRequiredMixin


class AdminRequiredDispatchMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            return redirect('subs')
        return redirect('login')
    
class UserRequiredDispatchMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            return redirect('control')
        return redirect('login')   


# Create your views here.


def login_user(request):
 
    if request.method == "POST":
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('subs')
            else:
                form.add_error(None, 'Invalid username or password.')

    else:
        form = loginForm()

    return render(request, 'login.html', {'form': form})

class LogoutUser(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

class AdminPanel(AdminRequiredDispatchMixin, TemplateView):
    template_name = 'adminpanel.html'
    
class AllPapers(AdminRequiredDispatchMixin,ListView):
    model = Paper
    template_name = 'all_papers.html'
    context_object_name = 'all_papers'
    
class AddPaper(AdminRequiredDispatchMixin,CreateView):
    model = Paper
    template_name = 'add_paper.html'
    fields = ['subject', 'time_allotted', 'number_questions']
    success_url = reverse_lazy('all_papers')  

    def post(self, request, *args, **kwargs):
        subject = request.POST.get('Subject')
        time_allotted = request.POST.get('time_allotted')
        number_questions = request.POST.get('number_questions')
        Paper.objects.create(subject=subject, time_allotted=time_allotted, number_questions=number_questions)

        return HttpResponseRedirect(self.success_url)

class EditPaper(AdminRequiredDispatchMixin,UpdateView):
    model = Paper
    template_name = 'edit_paper.html'
    fields = ['subject', 'time_allotted', 'number_questions']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paper = get_object_or_404(Paper, pk=self.kwargs['paper_id'])
        context['paper'] = paper
        
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Paper, pk=self.kwargs['paper_id'])

    def get_success_url(self):
        return reverse_lazy('all_papers')
    
class DeletePaper(AdminRequiredDispatchMixin,DeleteView):
    model = Paper
    template_name = None
    
    def get_success_url(self):
        return reverse_lazy('all_papers')
    
class PaperQuestions(AdminRequiredDispatchMixin, ListView):
    model = Question
    template_name = 'paper_questions.html'
    context_object_name = 'questions'
    
    def get_queryset(self):
        self.paper = get_object_or_404(Paper, pk=self.kwargs['paper_id'])
        return Question.objects.filter(paper=self.paper)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paper'] = get_object_or_404(Paper, pk=self.kwargs['paper_id'])
        return context
    
class EditQuestion(AdminRequiredDispatchMixin,UpdateView):
    model = Question
    template_name = 'edit_question.html'
    fields = ['question_text']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        context['paper_id'] = question.paper.id
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Question, pk=self.kwargs['question_id'])

    def get_success_url(self):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return reverse_lazy('questions', kwargs={'paper_id': question.paper.id})
    
class DeleteQuestion(AdminRequiredDispatchMixin,DeleteView):
    model = Question
    template_name = None
    
    def get_success_url(self):
        return reverse_lazy('questions', kwargs={'paper_id': self.object.paper.id})
    
class AddQuestion(AdminRequiredDispatchMixin,CreateView):
    model = Question
    template_name = 'add_question.html'
    fields = ['question_text']
    
    def get_object(self, queryset=None):
        return get_object_or_404(Paper, pk=self.kwargs['paper_id'])

    def post(self, request, *args, **kwargs):
        paper = self.get_object()
        paper.add_question(request.POST['question_text'])
        return redirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paper'] = get_object_or_404(Paper, pk=self.kwargs['paper_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('questions', kwargs={'paper_id': self.kwargs['paper_id']})

    
class AllUsernames(AdminRequiredDispatchMixin,ListView):
    model = TestUser
    template_name = 'all_usernames.html'
    context_object_name = 'all_users'

class Register(AdminRequiredDispatchMixin,View):
    template_name = 'register.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        attempts = request.POST.get("attempts") or 1

        subject = "Welcome to Kamet"
        message = f'''You can login and give the test AT WWW.EXAMPLE.COM \n
        your username is "{username}" and your password is "{password}"'''
        from_email = "shivansh.rawat@enine.school"
        recipient = [email]

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password, email=email)
            testuser = TestUser(user=user, attempts=attempts)
            testuser.save()
            #send_mail(subject, message, from_email, recipient)
            return redirect("all_usernames")
        return render(
            request, self.template_name, {"error": "Username already exists"}
        )
    
class EditSettings(AdminRequiredDispatchMixin,UpdateView):
    model = TestUser
    template_name = 'edit_settings.html'
    fields = ['attempts']
    success_url = reverse_lazy('all_usernames')

    def get_context_data(self, **kwargs):
        return {'tuser':self.object}


class DeleteUser(AdminRequiredDispatchMixin,DeleteView):
    model = TestUser
    template_name = None
    success_url = reverse_lazy('all_usernames')
    
class UserSolutions(AdminRequiredDispatchMixin,DetailView):
    model = TestUser
    template_name = "user_solutions_detail.html"
    context_object_name = "user"
    
    def get_context_data(self, **kwargs):
        user_solutions = self.object.user_solution.all()
        paper = Paper.objects.all()
        context = {"user_solutions":user_solutions, "papers":paper, "tuser":self.object}

        return context

class UpdateStatus(AdminRequiredDispatchMixin,UpdateView):
    model = UserSolution  
    success_url = reverse_lazy('all_usernames')  
    
    def get_object(self):
        user = TestUser.objects.get(pk=self.kwargs['pk'])
        return UserSolution.objects.filter(test_user=user)

    def post(self, request, *args, **kwargs):
        user_solutions = self.get_object()
        for user_solution in user_solutions:
            user_solution.status =  request.POST.get(f"status_{user_solution.id}")
            user_solution.save()

        return redirect("all_usernames")

class Subjects(UserRequiredDispatchMixin,ListView):
    model = Paper
    template_name = "subjects.html"
    context_object_name = 'subjects'
    
class Base(UserRequiredDispatchMixin,TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        user = self.request.user   
        context = {'paper':Paper.objects.get(id=self.kwargs['paper_id']), 'tuser':TestUser.objects.get(user=user) }
        return context

    
class RandomQuestionsView(UserRequiredDispatchMixin,ListView):
    template_name = "question_list.html"
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        paper = Paper.objects.get(id=self.kwargs['paper_id'])
        testuser = TestUser.objects.get(username=user.username)

        if testuser.attempts > 0:
            testuser.attempted()
            context = {
                "questions": paper.random_question(testuser),
                "time_allotted": paper.time_allotted
            }
            return render(request, self.template_name, context)
        else:
            return render(request, "exhausted.html")
        
class ResultView(UserRequiredDispatchMixin,DetailView):
    model = TestUser
    template_name = 'result.html'

    # def get_object(self):
    #     return TestUser.objects.get(pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        paper = Paper.objects.get(pk=self.kwargs['paper_id'])
        user = self.object
        solutions = user.solutions(paper)
        total = solutions.count()
        correct,incorrect = 0,0
        for i in solutions:
            if i.status == 'correct':
                correct+=1
            elif i.status == 'incorrect':
                incorrect+= 1
        context = {'user_solutions':solutions,'paper':self.get_object(),'total':total,'correct':correct,'incorrect':incorrect}
        return context
    
class SubmitAllSolutionsView(UserRequiredDispatchMixin,CreateView):
    model = UserSolution
         
    def post(self, request, *args, **kwargs):
        user = request.user
        testuser = TestUser.objects.get(username=user.username)

        for ques_id, sol_text in request.POST.items():
            if ques_id != 'csrfmiddlewaretoken':
                question = Question.objects.get(id=ques_id)
                if sol_text:
                    UserSolution.objects.create(
                        test_user=testuser,
                        question=question,
                        solution=sol_text,
                    )
        return redirect("subs")
