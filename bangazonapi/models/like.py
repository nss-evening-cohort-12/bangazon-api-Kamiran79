from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from .customer import Customer
from .product import Product

class Like(models.Model):
  customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
  product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
