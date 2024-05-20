import pytest
from unittest.mock import MagicMock, patch
from src.controllers.recipecontroller import RecipeController
from src.util.dao import DAO
from src.static.diets import Diet

# Fixtures for setting up the mock data and environment
@pytest.fixture
def mock_dao():
    mock_dao = MagicMock(spec=DAO)
    mock_dao.get_all.return_value = [
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
    with patch('src.controllers.recipe_controller.RecipeController.load_recipes', return_value=mock_recipes):
        return RecipeController(items_dao=mock_dao)

# Mock calculate_readiness
@pytest.fixture
def mock_calculate_readiness():
    with patch('src.util.calculator.calculate_readiness') as mock_calc:
        mock_calc.side_effect = lambda recipe, items: sum(min(items.get(ingredient, 0) / qty, 1) for ingredient, qty in recipe['ingredients'].items()) / len(recipe['ingredients'])
        yield mock_calc

# Test cases for the get_recipe method
def test_get_recipe_optimal(recipe_controller, mock_calculate_readiness):
    diet = Diet.VEGETARIAN
    take_best = True

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    
    # Expect the best recipe with the highest readiness (Cake in this case)
    assert result == "Cake"

def test_get_recipe_random(recipe_controller, mock_calculate_readiness):
    diet = Diet.VEGETARIAN
    take_best = False

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    
    # Since take_best is False, any vegetarian recipe can be chosen randomly
    assert result in ["Cake", "Pasta"]

def test_get_recipe_no_valid_recipe(recipe_controller, mock_calculate_readiness):
    diet = Diet.VEGAN
    take_best = True

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    
    # No valid recipe meets the readiness threshold of 0.1
    assert result is None

def test_get_recipe_no_recipe_for_diet(recipe_controller, mock_calculate_readiness):
    diet = Diet.KETO
    take_best = True

    result = recipe_controller.get_recipe(diet=diet, take_best=take_best)
    
    # No recipe available for the Keto diet
    assert result is None