from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = FastAPI()

# Base de données temporaire des recettes
recipes_db = {}

class Recipe(BaseModel):
    name: str
    ingredients: dict  # {"Tomate": 2, "Oignon": 1} (quantité par personne)

class ShoppingRequest(BaseModel):
    recipes: dict  # {"Pâtes Carbonara": 2, "Salade": 3}

@app.post("/recipes/")
def add_recipe(recipe: Recipe):
    recipes_db[recipe.name] = recipe.ingredients
    return {"message": "Recette ajoutée"}

@app.get("/recipes/")
def get_recipes():
    return recipes_db

@app.post("/shopping-list/")
def generate_shopping_list(request: ShoppingRequest):
    shopping_list = {}
    for recipe, persons in request.recipes.items():
        if recipe in recipes_db:
            for ingredient, quantity in recipes_db[recipe].items():
                shopping_list[ingredient] = shopping_list.get(ingredient, 0) + (quantity * persons)
        else:
            raise HTTPException(status_code=404, detail=f"Recette '{recipe}' non trouvée")
    return shopping_list

def add_to_cart_hyperu(ingredient):
    """ Ajoute un ingrédient au panier sur Hyper U via Selenium """
    driver = webdriver.Chrome()  # Assure-toi d'avoir chromedriver installé
    driver.get("https://www.coursesu.com/")

    time.sleep(3)  # Attente du chargement

    search_box = driver.find_element(By.NAME, "search")
    search_box.send_keys(ingredient)
    search_box.send_keys(Keys.RETURN)

    time.sleep(2)

    try:
        add_button = driver.find_element(By.CLASS_NAME, "add-to-cart-button")
        add_button.click()
    except:
        print(f"⚠️ Impossible d'ajouter {ingredient}")

    driver.quit()

@app.post("/add-to-cart/")
def add_items_to_cart(request: ShoppingRequest):
    shopping_list = generate_shopping_list(request)
    for item in shopping_list:
        add_to_cart_hyperu(item)
    return {"message": "Produits ajoutés au panier"}
