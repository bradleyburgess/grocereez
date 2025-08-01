from django.contrib.auth import get_user_model
from faker import Faker
import pytest

from households.models import Household, HouseholdMember
from ingredients.models import IngredientsCategory, Ingredient

faker = Faker()
User = get_user_model()


@pytest.fixture(scope="function")
def user(db):
    email = faker.email()
    password = faker.password()
    display_name = faker.name_nonbinary()
    first_name = faker.name_nonbinary()
    last_name = faker.last_name()
    user = User.objects.create_user(
        email=email,
        password=password,
        display_name=display_name,
        first_name=first_name,
    )  # type: ignore
    return {
        "user": user,
        "email": email,
        "password": password,
        "display_name": display_name,
        "first_name": first_name,
        "last_name": last_name,
    }


@pytest.fixture(scope="function")
def new_user(db):
    email = faker.email()
    password = faker.password()
    display_name = faker.name_nonbinary()
    first_name = faker.first_name()
    last_name = faker.last_name()
    return {
        "user": User.objects.create_user(
            email=email,
            password=password,
            display_name=display_name,
            last_name=last_name,
        ),  # type: ignore
        "email": email,
        "password": password,
        "display_name": display_name,
        "first_name": first_name,
        "last_name": last_name,
    }


@pytest.fixture(scope="function")
def signup_user():
    return {
        "email": faker.email(),
        "password": faker.password(),
        "display_name": faker.name_nonbinary(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
    }


@pytest.fixture
def household_name():
    return faker.last_name() + " Household"


@pytest.fixture
def household(db, user):
    h_name = user["last_name"] + " Household"
    household = Household.objects.create(name=h_name, created_by=user["user"])
    HouseholdMember.objects.create(
        user=user["user"],
        household=household,
        member_type=HouseholdMember.MemberType.ADMIN,
    )
    return household


@pytest.fixture
def ingredients_category(db, household, user):
    return IngredientsCategory.objects.create(
        name="Dry Goods",
        description="Pasta and stuff",
        household=household,
    )


@pytest.fixture
def ingredient(db, household, ingredients_category, user):
    return Ingredient.objects.create(
        name=faker.word(),
        household=household,
        category=ingredients_category,
    )
