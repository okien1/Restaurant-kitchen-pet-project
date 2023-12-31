from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from kitchen.forms import CookCreationForm, CookUpdateForm, DishOrderingForm
from kitchen.models import Dish, Cook, Ingredient


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View function for the home page of the site."""

    num_dishes = Dish.objects.count()
    num_cooks = Cook.objects.count()
    num_ingredients = Ingredient.objects.count()
    context = {
        "num_dishes": num_dishes,
        "num_cooks": num_cooks,
        "num_ingredients": num_ingredients,
    }

    return render(request, "kitchen/index.html", context=context)


class CookCreateView(generic.CreateView):
    model = Cook
    form_class = CookCreationForm
    template_name = "kitchen/register.html"
    success_url = reverse_lazy("kitchen:home")

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        login(self.request, self.object)

        return response


class CookListView(LoginRequiredMixin, generic.ListView):
    model = Cook
    context_object_name = "cook_list"
    template_name = "kitchen/cooks-list.html"
    paginate_by = 5


class CookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Cook
    context_object_name = "cook_detail"
    template_name = "kitchen/cook-detail.html"


class CookUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cook
    form_class = CookUpdateForm
    template_name = "kitchen/cook-update.html"
    success_url = reverse_lazy("kitchen:cooks-list")


class IngredientListView(LoginRequiredMixin, generic.ListView):
    model = Ingredient
    context_object_name = "ingredient_list"
    template_name = "kitchen/ingredient-list.html"
    queryset = Ingredient.objects.all().select_related("type")
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_type = self.request.GET.get("ingredient_type")

        if selected_type:
            queryset = queryset.filter(type__name=selected_type).select_related("type")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_type"] = self.request.GET.get("ingredient_type")
        return context


class IngredientCreateView(LoginRequiredMixin, generic.CreateView):
    model = Ingredient
    template_name = "kitchen/ingredient-create.html"
    success_url = reverse_lazy("kitchen:ingredient-list")
    fields = "__all__"

    def get_form(self, form_class: object = None) -> object:
        form = super().get_form(form_class)
        form.fields["quantity"].help_text = "This could be gr, kg, pieces, etc"
        return form


class IngredientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Ingredient
    template_name = "kitchen/ingredient-create.html"
    success_url = reverse_lazy("kitchen:ingredient-list")
    fields = "__all__"


class DishListView(LoginRequiredMixin, generic.ListView):
    model = Dish
    template_name = "kitchen/dish-list.html"
    queryset = Dish.objects.select_related("dish_type")
    paginate_by = 5
    form_class = DishOrderingForm

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.GET.get("ordering", None)

        if ordering == "price_asc":
            queryset = queryset.order_by("price")
        elif ordering == "price_desc":
            queryset = queryset.order_by("-price")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(self.request.GET)
        return context


class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish
    template_name = "kitchen/dish-create.html"
    success_url = reverse_lazy("kitchen:dish-list")
    fields = "__all__"


class DishDetailView(LoginRequiredMixin, generic.DetailView):
    model = Dish
    template_name = "kitchen/dish-detail.html"


class DishUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Dish
    template_name = "kitchen/dish-create.html"
    fields = "__all__"

    def get_success_url(self) -> str:
        return reverse_lazy("kitchen:dish-detail", kwargs={"pk": self.object.pk})
