import pytest
from unittest.mock import MagicMock, patch
from src.controllers.recipecontroller import RecipeController
from src.util.dao import DAO
from src.static.diets import Diet

# Fixtures for setting up the mock data and environment
@pytest.fixture
def mock_dao():
    mock_dao = MagicMock(spec=DAO)
    mock_dao.find.return_value = [
        {"name": "flour", "quantity": 2},
        {"name": "sugar", "quantity": 5},
        {"name": "butter", "quantity": 1},
        {"name": "lettuce", "quantity": 3},
        {"name": "tomato", "quantity": 2},
        {"name": "pasta", "quantity": 2},
        {"name": "tomato_sauce", "quantity": 1}
    ]
    return mock_dao

@pytest.fixture
def mock_recipes():
    return [
        {"name": "Cake", "diets": ["vegetarian"], "ingredients": {"flour": 1, "sugar": 2, "butter": 1}},
        {"name": "Salad", "diets": ["vegan", "vegetarian"], "ingredients": {"lettuce": 1, "tomato": 2}},
        {"name": "Pasta", "diets": ["vegetarian"], "ingredients": {"pasta": 2, "tomato_sauce": 1}},
    ]

@pytest.fixture
def recipe_controller(mock_dao, mock_recipes):
    with patch('src.controllers.recipecontroller.RecipeController.load_recipes', return_value=mock_recipes):
        return RecipeController(items_dao=mock_dao)

@pytest.fixture
def mock_calculate_readiness():
    with patch('src.util.calculator.calculate_readiness') as mock_calc:
        mock_calc.side_effect = lambda recipe, items: sum(min(items.get(ingredient, 0) / qty, 1) for ingredient, qty in recipe['ingredients'].items()) / len(recipe['ingredients'])
        yield mock_calc

# Test cases for the get_recipe method
def test_get_recipe_tc1(recipe_controller, mock_calculate_readiness):
    # TC1: Diet matches, take_best=True, valid readiness values
    diet = Diet.VEGETARIAN
    take_best = True

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    assert result in ["Cake", "Salad", "Pasta"]

def test_get_recipe_tc2(recipe_controller, mock_calculate_readiness):
    # TC2: Diet matches, take_best=False, valid readiness values
    diet = Diet.VEGETARIAN
    take_best = False

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    assert result in ["Cake", "Pasta", "Salad"]

def test_get_recipe_tc3(recipe_controller, mock_calculate_readiness):
    # TC3: Diet does not match, take_best=True
    diet = Diet.KETO
    take_best = True

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    assert result is None

def test_get_recipe_tc4(recipe_controller, mock_calculate_readiness):
    # TC4: Diet does not match, take_best=False
    diet = Diet.KETO
    take_best = False

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    assert result is None

def test_get_recipe_tc5(recipe_controller, mock_calculate_readiness):
    # TC5: Readiness values below threshold
    with patch('src.util.calculator.calculate_readiness') as mock_calc:
        mock_calc.side_effect = lambda recipe, items: 0.05
        diet = Diet.VEGETARIAN
        take_best = True

        result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
        assert result is None

def test_get_recipe_tc6(recipe_controller):
    # TC6: No valid readiness values (invalid recipes)
    with patch('src.controllers.recipecontroller.RecipeController.load_recipes', return_value=[]):
        recipe_controller.recipes = []
        diet = Diet.VEGETARIAN
        take_best = True

        result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
        assert result is None