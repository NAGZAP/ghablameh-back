from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count, Avg
from django.http import HttpRequest
from .models import OrganizationAdmin as OrganizationAdminModel, OrganizationMemberShipRequest, OrganizationMemberShipInvitation, Buffet, Rate, DailyMenu, Meal, Food, MealFood, Reserve, Client, Organization


class ClientInline(admin.StackedInline):
    model = Client
    extra = 0

class OrganizationInline(admin.StackedInline):
    model = Organization
    extra = 0

class OrganizationAdminInline(admin.StackedInline):
    model = OrganizationAdminModel
    extra = 0

class OrganizationMemberShipRequestInline(admin.StackedInline):
    model = OrganizationMemberShipRequest
    extra = 0
    # autocomplete_fields = ['client', 'organization']

# class OrganizationMemberShipInvitationInline(admin.StackedInline):
#     model = OrganizationMemberShipInvitation
#     extra = 0

class BuffetInline(admin.StackedInline):
    model = Buffet
    extra = 0

class RateInline(admin.StackedInline):
    model = Rate
    extra = 0
    autocomplete_fields = ['client', 'buffet']

class DailyMenuInline(admin.StackedInline):
    model = DailyMenu
    extra = 0

class MealInline(admin.StackedInline):
    model = Meal
    extra = 0

class FoodInline(admin.StackedInline):
    model = Food
    extra = 0

class MealFoodInline(admin.StackedInline):
    model = MealFood
    extra = 0
    autocomplete_fields = ['meal', 'food']
    

class ReserveInline(admin.StackedInline):
    model = Reserve
    extra = 0

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    
    inlines = [OrganizationMemberShipRequestInline, RateInline, ReserveInline]
    search_fields = ['user__username', 'user__email']
    autocomplete_fields = ['user']
    list_select_related = ['user']
    list_display = ['user', 'gender', 'birthdate', 'created_at','organizations_count']
    
    @admin.display(ordering='organizations_count', description='Organizations')
    def organizations_count(self, client):
        return client.organizations_count
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('organizations').annotate(organizations_count=Count('organizations'))

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "organizations":
            kwargs['required'] = False
        return super().formfield_for_manytomany(db_field, request, **kwargs)
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OrganizationMemberShipRequestInline, BuffetInline]
    search_fields = ['name']
    
    
@admin.register(Buffet)
class BuffetAdmin(admin.ModelAdmin):
    inlines = [RateInline, DailyMenuInline]
    search_fields = ['name', 'organization__name']
    autocomplete_fields = ['organization']
    list_display = ['name', 'organization', 'average_rate', 'created_at', 'updated_at']
    list_filter = ['organization']
    
    @admin.display(ordering='average_rate', description='Average Rate')
    def average_rate(self, buffet):
        return buffet.average_rate
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(average_rate=Avg('rates__rate'))

@admin.register(OrganizationAdminModel)
class OrganizationAdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'organization__name']
    autocomplete_fields = ['user', 'organization']

@admin.register(OrganizationMemberShipRequest)
class OrganizationMemberShipRequestAdmin(admin.ModelAdmin):
    search_fields = ['client__user__username', 'client__user__email', 'organization__name']
    autocomplete_fields = ['client', 'organization']
    list_display = ['client', 'organization', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'organization', 'client']

# @admin.register(OrganizationMemberShipInvitation)
# class OrganizationMemberShipInvitationAdmin(admin.ModelAdmin):
#     inlines = [ClientInline, OrganizationInline]
#     search_fields = ['client__user__username', 'client__user__email', 'organization__name']
#     autocomplete_fields = ['client', 'organization']


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    search_fields = ['client__user__username', 'client__user__email', 'buffet__name']
    autocomplete_fields = ['client', 'buffet']
    list_display = ['client', 'buffet', 'rate', 'created_at', 'updated_at']
    list_filter = ['rate']


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    inlines = [MealInline]
    search_fields = ['buffet__name']
    autocomplete_fields = ['buffet']
    list_select_related = ['buffet', 'buffet__organization']
    list_display = ['buffet','date','meals_count', 'organization']
    list_filter = ['buffet__organization']
    
    def organization(self, dailyMenu):
        return dailyMenu.buffet.organization.name
    
    
        

    @admin.display(ordering='meals_count', description='Meals')
    def meals_count(self, dailyMenu):
        return dailyMenu.meals_count
    
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request)\
            .prefetch_related('meals')\
            .annotate(meals_count=Count('meals'))
            


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    inlines = [MealFoodInline]
    search_fields = ['name', 'dailyMenu__buffet__name']
    autocomplete_fields = ['dailyMenu']
    list_display = ['name', 'dailyMenu', 'time', 'foods_count']
    
    def foods_count(self, meal):
        return meal.foods_count
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request)\
            .prefetch_related('mealfood_set')\
            .annotate(foods_count=Count('mealfood'))

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    inlines = [MealFoodInline]
    search_fields = ['name']


@admin.register(Reserve)
class ReserveAdmin(admin.ModelAdmin):
    search_fields = ['client__user__username', 'client__user__email', 'meal_food__meal__name', 'meal_food__food__name']
    autocomplete_fields = ['client', 'meal_food']
    list_display = ['client', 'meal_food', 'created_at', 'updated_at']
    # filter by organization
    list_filter = ['meal_food__meal__dailyMenu__buffet__organization']
    list_select_related = ['meal_food', 'meal_food__meal', 'meal_food__food', 'meal_food__meal__dailyMenu', 'meal_food__meal__dailyMenu__buffet', 'meal_food__meal__dailyMenu__buffet__organization']
    
    
@admin.register(MealFood)
class MealFoodAdmin(admin.ModelAdmin):
    search_fields = ['meal__name', 'food__name']
    autocomplete_fields = ['meal', 'food']
    list_display = ['meal', 'food', 'price', 'number_in_stock']