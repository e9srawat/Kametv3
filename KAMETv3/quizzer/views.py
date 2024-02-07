"""views"""

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    CreateView,
    TemplateView,
    View,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import loginForm
from .models import TestUser, Paper, Question, UserSolution


class AdminRequiredDispatchMixin(LoginRequiredMixin):
    """only admin can access"""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            return redirect("subs")
        return redirect("login")


class UserRequiredDispatchMixin(LoginRequiredMixin):
    """only non-admin can access"""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            return redirect("control")
        return redirect("login")


# Create your views here.


def login_user(request):
    """login view"""
    if request.method == "POST":
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("subs")
            form.add_error(None, "Invalid username or password.")
    else:
        form = loginForm()
    return render(request, "login.html", {"form": form})


class LogoutUser(View):
    """logout view"""

    def get(self, request, *args, **kwargs):
        """GET method"""
        logout(request)
        return redirect("login")


class AdminPanel(AdminRequiredDispatchMixin, TemplateView):
    """admin dashboard view"""

    template_name = "adminpanel.html"


class AllPapers(AdminRequiredDispatchMixin, ListView):
    """Show all available papers view"""

    model = Paper
    template_name = "all_papers.html"
    context_object_name = "all_papers"


class AddPaper(AdminRequiredDispatchMixin, CreateView):
    """Add a new paper view"""

    model = Paper
    template_name = "add_paper.html"
    fields = ["subject", "time_allotted", "number_questions"]
    success_url = reverse_lazy("all_papers")


class EditPaper(AdminRequiredDispatchMixin, UpdateView):
    """edit a paper view"""

    model = Paper
    template_name = "edit_paper.html"
    fields = ["subject", "time_allotted", "number_questions"]
    context_object_name = "paper"
    success_url = reverse_lazy("all_papers")


class DeletePaper(AdminRequiredDispatchMixin, DeleteView):
    """delete a paper view"""

    model = Paper
    template_name = None
    success_url = reverse_lazy("all_papers")


class PaperQuestions(AdminRequiredDispatchMixin, ListView):
    """Shows all questions in the selected paper view"""

    model = Question
    template_name = "paper_questions.html"

    def get_context_data(self, **kwargs):
        """returns context"""
        context = super().get_context_data(**kwargs)
        context["paper"] = Paper.objects.get(pk=self.kwargs["pk"])
        return context


class EditQuestion(AdminRequiredDispatchMixin, UpdateView):
    """Docstring"""

    model = Question
    template_name = "edit_question.html"
    fields = ["question_text"]

    def get_success_url(self):
        """returns success_url"""
        question = self.object
        return reverse_lazy("questions", kwargs={"pk": question.paper.id})


class DeleteQuestion(AdminRequiredDispatchMixin, DeleteView):
    """Docstring"""

    model = Question
    template_name = None

    def get_success_url(self):
        """returns success_url"""

        return reverse_lazy("questions", kwargs={"pk": self.object.paper.id})


class AddQuestion(AdminRequiredDispatchMixin, CreateView):
    """Docstring"""

    model = Paper
    template_name = "add_question.html"
    fields = []

    def post(self, request, *args, **kwargs):
        """POST method"""
        paper = self.get_object()
        paper.qpaper.create(question_text=request.POST["question_text"])
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """returns context"""

        context = super().get_context_data(**kwargs)
        context["paper"] = self.get_object()
        return context

    def get_success_url(self):
        """returns success_url"""
        return reverse_lazy("questions", kwargs={"pk": self.kwargs["pk"]})


class AllUsers(AdminRequiredDispatchMixin, ListView):
    """Docstring"""

    model = TestUser
    template_name = "all_usernames.html"
    context_object_name = "all_users"


class Register(AdminRequiredDispatchMixin, View):
    """Docstring"""

    template_name = "register.html"

    def get(self, request):
        """GET method"""
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """POST method"""
        buser = get_user_model()
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        attempts = request.POST["attempts"] or 1

        if not buser.objects.filter(username=username).exists():
            tuser = buser.objects.create_user(
                username=username, password=password, email=email
            )
            testuser = TestUser.objects.create(user=tuser, attempts=attempts)
            # testuser.send_email(password)
            return redirect("all_usernames")
        return render(request, self.template_name, {"error": "Username already exists"})


class EditSettings(AdminRequiredDispatchMixin, UpdateView):
    """Docstring"""

    model = TestUser
    template_name = "edit_settings.html"
    fields = ["attempts"]
    success_url = reverse_lazy("all_usernames")
    context_object_name = "tuser"


class DeleteUser(AdminRequiredDispatchMixin, DeleteView):
    """Docstring"""

    model = TestUser
    template_name = None
    success_url = reverse_lazy("all_usernames")


class UserSolutions(AdminRequiredDispatchMixin, DetailView):
    """Docstring"""

    model = TestUser
    template_name = "user_solutions_detail.html"

    def get_context_data(self, **kwargs):
        """returns context"""
        context = super().get_context_data(**kwargs)
        paper = Paper.objects.all()
        context["papers"] = paper
        return context


class UpdateStatus(AdminRequiredDispatchMixin, UpdateView):
    """Docstring"""

    model = UserSolution
    success_url = reverse_lazy("all_usernames")

    def get_object(self, queryset=None):
        """Returns object"""
        user = TestUser.objects.get(pk=self.kwargs["pk"])
        return UserSolution.objects.filter(test_user=user)

    def post(self, request, *args, **kwargs):
        """POST method"""
        user_solutions = self.get_object()
        for user_solution in user_solutions:
            user_solution.status = request.POST[f"status_{user_solution.id}"]
            user_solution.save()
        return redirect("all_usernames")


class Subjects(UserRequiredDispatchMixin, ListView):
    """Docstring"""

    model = Paper
    template_name = "subjects.html"
    context_object_name = "subjects"


class Base(UserRequiredDispatchMixin, TemplateView):
    """Docstring"""

    template_name = "base.html"

    def get_context_data(self, **kwargs):
        """returns context"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["paper"] = Paper.objects.get(id=self.kwargs["paper_id"])
        context["tuser"] = TestUser.objects.get(user=user)
        return context


class TakeTest(UserRequiredDispatchMixin, View):
    """Docstring"""

    template_name = "question_list.html"

    def get(self, request, *args, **kwargs):
        """GET method"""
        user = self.request.user
        paper = Paper.objects.get(id=self.kwargs["pk"])
        testuser = TestUser.objects.get(user=user)

        if testuser.attempts > 0:
            testuser.attempted()
            context = {
                "questions": paper.random_question(testuser),
                "time_allotted": paper.time_allotted,
            }
            return render(request, self.template_name, context)
        return render(request, "exhausted.html")

    def post(self, request, *args, **kwargs):
        """POST method"""
        testuser = TestUser.objects.get(user=request.user)
        for ques_id, sol_text in request.POST.items():
            if ques_id != "csrfmiddlewaretoken":
                question = Question.objects.get(id=ques_id)
                if sol_text:
                    UserSolution(
                        test_user=testuser, question=question, solution=sol_text
                    )
        return redirect("subs")


class ResultView(UserRequiredDispatchMixin, DetailView):
    """Docstring"""

    model = TestUser
    template_name = "result.html"
    context_object_name = "tuser"

    def get_context_data(self, **kwargs):
        """returns context"""
        context = super().get_context_data(**kwargs)
        user = self.object
        paper = Paper.objects.get(pk=self.kwargs["paper_id"])
        solutions = user.user_solution.filter(question__paper=paper)
        total = len(solutions)
        correct = len([i for i in solutions if i.status == "correct"])
        unchecked = len([i for i in solutions if i.status == "unchecked"])
        context["user_solutions"] = solutions
        context["total"] = total
        context["unchecked"] = unchecked
        context["correct"] = correct
        return context
