from flask import request
from flask_restful import Resource
from models import db, Restaurant, Pizza, RestaurantPizza

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict() for r in restaurants], 200

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            return restaurant.to_dict(rules=('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza.restaurant_pizzas')), 200
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        return {"error": "Restaurant not found"}, 404

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict() for p in pizzas], 200

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data['price']
            pizza_id = data['pizza_id']
            restaurant_id = data['restaurant_id']

            restaurant = Restaurant.query.get(restaurant_id)
            pizza = Pizza.query.get(pizza_id)

            if not restaurant or not pizza:
                return {"errors": ["Invalid pizza_id or restaurant_id"]}, 400

            new_rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(new_rp)
            db.session.commit()

            return new_rp.to_dict(
                rules=(
                    '-pizza.restaurant_pizzas',
                    '-restaurant.restaurant_pizzas',
                )
            ), 201

        except Exception:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400
