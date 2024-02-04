import random
from typing import Any
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
                return redirect('subs')  # Redirect to the subs page upon successful login
            else:
                # Handle invalid login credentials
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
    
class PaperQuestions(ListView):
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
    
class EditQuestion(UpdateView):
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
        question = get_object_or_404(Question, pk=self.kwargs['pk'])
        return reverse_lazy('questions', kwargs={'paper_id': question.paper.id})
    
class AddQuestion(AdminRequiredDispatchMixin,CreateView):
    model = Question
    template_name = 'add_question.html'
    fields = ['question_text']

    def form_valid(self, form):
        paper = get_object_or_404(Paper, pk=self.kwargs['paper_id'])
        form.instance.paper = paper
        return super().form_valid(form)
    
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
        attempts = request.POST.get("attempts") or 5

        subject = "Welcome to Kamet"
        message = f'''You can login and give the test AT WWW.EXAMPLE.COM \n
        your username is "{username}" and your password is "{password}"'''
        from_email = "shivansh.rawat@enine.school"
        recipient = [email]

        if not User.objects.filter(username=username).exists():
            user = TestUser(username=username, password=password, email=email)
            user.createUser()
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

    def get_object(self, queryset=None):
        user_id = self.kwargs['user_id']
        return TestUser.objects.get(id=user_id)

class DeleteUser(AdminRequiredDispatchMixin,DeleteView):
    model = TestUser
    template_name = None
    success_url = reverse_lazy('all_usernames')
    
class UserSolutions(AdminRequiredDispatchMixin,DetailView):
    model = TestUser
    template_name = "user_solutions_detail.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_solutions = UserSolution.objects.filter(test_user=self.object)
        paper = Paper.objects.all()
        context["user_solutions"] = user_solutions
        context["papers"] = paper

        return context

class UpdateStatus(AdminRequiredDispatchMixin,UpdateView):
    model = UserSolution  
    def get_object(self, queryset=None):
        user_id = self.kwargs['user_id']
        tuser = get_object_or_404(TestUser, id=user_id)
        user_solutions = UserSolution.objects.filter(test_user=tuser)
        return user_solutions

    def post(self, request, *args, **kwargs):
        user_solutions = self.get_object()
        for user_solution in user_solutions:
            status = request.POST.get(
                f"status_{user_solution.id}"
            ) 
            user_solution.status = status
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
        testuser = TestUser.objects.get(username=user.username)
        paper_id = self.kwargs['paper_id']

        paper = Paper.objects.get(id=paper_id)
        
        context = {'paper':paper, 'tuser':testuser }
        return context

# class PaperQuestionsView(UserRequiredDispatchMixin,View):
#     template_name = 'questions_list.html'

#     def get(self, request, paper_id):
#         paper = get_object_or_404(Paper, id=paper_id)
#         questions = Question.objects.filter(paper=paper)
#         context = {
#             'paper': paper,
#             'questions': questions,
#         }

#         return render(request, self.template_name, context)
    
    
class RandomQuestionsView(UserRequiredDispatchMixin,ListView):
    template_name = "question_list.html"
    
    def get(self, request,paper_id, *args, **kwargs):
        user = self.request.user
        paper = get_object_or_404(Paper, id=paper_id)
        testuser = TestUser.objects.get(username=user.username)

        if testuser.attempts > 0:
            if user.is_authenticated:
                user_solved_questions = [
                    solution.question_id
                    for solution in UserSolution.objects.filter(test_user=testuser)
                ]
                available_questions = Question.objects.filter(paper=paper).exclude(id__in=user_solved_questions)
                random_questions = random.sample(
                    list(available_questions),
                    min(paper.number_questions, len(available_questions))
                )
                context = {
                    "questions": random_questions,
                    "time_allotted": paper.time_allotted
                }
                return render(request, self.template_name, context)
            else:
                return redirect("login")
        else:
            return render(request, "exhausted.html")
        
class ResultView(UserRequiredDispatchMixin,ListView):
    model = UserSolution
    template_name = 'result.html'
    context_object_name = 'user_solutions'

    def get_queryset(self):
        paper_id = self.kwargs.get('paper_id')  # Update this if your URL structure is different
        paper = Paper.objects.get(pk=paper_id)
        return UserSolution.objects.filter(question__paper=paper)
    
    def get_context_data(self, **kwargs):
        solutions = self.get_queryset()
        total = solutions.count()
        correct,incorrect = 0,0
        for i in solutions:
            if i.status == 'correct':
                correct+=1
            elif i.status == 'incorrect':
                incorrect+= 1
        context = super().get_context_data(**kwargs)
        context['paper'] = get_object_or_404(Paper, pk=self.kwargs['paper_id'])
        context['total'] = total
        context['correct'] = correct
        context['incorrect'] = incorrect
        return context
    
class SubmitAllSolutionsView(UserRequiredDispatchMixin,CreateView):
    model = UserSolution
         
    def post(self, request, *args, **kwargs):
        user = request.user
        testuser = TestUser.objects.get(username=user.username)
        
        if testuser.attempts > 0:
            testuser.attempts -= 1
            testuser.update()
                        
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