"""View module for handling requests about products"""
from django.db.models import fields
from bangazonapi.models.like import Like
import base64
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import Product, Customer, ProductCategory
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser


class ProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'number_sold', 'description',
                  'quantity', 'created_date', 'location', 'image_path',
                  'average_rating', 'can_be_rated', )
        depth = 1


class Products(ViewSet):
    """Request handlers for Products in the Bangazon Platform"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /products POST new product
        @apiName CreateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {String} name Short form name of product
        @apiParam {Number} price Cost of product
        @apiParam {String} description Long form description of product
        @apiParam {Number} quantity Number of items to sell
        @apiParam {String} location City where product is located
        @apiParam {Number} category_id Category of product
        @apiParamExample {json} Input
            {
                "name": "Kite",
                "price": 14.99,
                "description": "It flies high",
                "quantity": 60,
                "location": "Pittsburgh",
                "category_id": 4
            }

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        new_product = Product()
        new_product.name = request.data["name"]
        new_product.price = request.data["price"]
        new_product.description = request.data["description"]
        new_product.quantity = request.data["quantity"]
        new_product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        new_product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        new_product.category = product_category

        if "image_path" in request.data:
            format, imgstr = request.data["image_path"].split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{new_product.id}-{request.data["name"]}.{ext}')

            new_product.image_path = data

        try:
            new_product.clean_fields(exclude="image_path")
            new_product.save()
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(
            new_product, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /products/:id GET product
        @apiName GetProduct
        @apiGroup Product

        @apiParam {id} id Product Id

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /products/:id PUT changes to product
        @apiName UpdateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        product = Product.objects.get(pk=pk)
        product.name = request.data["name"]
        product.price = request.data["price"]
        product.description = request.data["description"]
        product.quantity = request.data["quantity"]
        product.created_date = request.data["created_date"]
        product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        product.category = product_category
        product.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /products/:id DELETE product
        @apiName DeleteProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            product = Product.objects.get(pk=pk)
            product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """
        @api {GET} /products GET all products
        @apiName ListProducts
        @apiGroup Product

        @apiSuccess (200) {Object[]} products Array of products
        @apiSuccessExample {json} Success
            [
                {
                    "id": 101,
                    "url": "http://localhost:8000/products/101",
                    "name": "Kite",
                    "price": 14.99,
                    "number_sold": 0,
                    "description": "It flies high",
                    "quantity": 60,
                    "created_date": "2019-10-23",
                    "location": "Pittsburgh",
                    "image_path": null,
                    "average_rating": 0,
                    "category": {
                        "url": "http://localhost:8000/productcategories/6",
                        "name": "Games/Toys"
                    }
                }
            ]
        """
        products = Product.objects.all()

        # Support filtering by category and/or quantity
        category = self.request.query_params.get('category', None)
        quantity = self.request.query_params.get('quantity', None)
        order = self.request.query_params.get('order_by', None)
        direction = self.request.query_params.get('direction', None)
        number_sold = self.request.query_params.get('number_sold', None)
        min_price = self.request.query_params.get('min_price', None)
        location = self.request.query_params.get('location', None)


        if order is not None:
            order_filter = order

            if direction is not None:
                if direction == "desc":
                    order_filter = f'-{order}'

            products = products.order_by(order_filter)

        if min_price is not None:
            def price_filter(product):
                if product.price >= float(min_price):
                    return True
                return False                
            products = filter(price_filter, products)

        if category is not None:
            products = products.filter(category__id=category)

        if quantity is not None:
            products = products.order_by("-created_date")[:int(quantity)]

        if number_sold is not None:
            def sold_filter(product):
                if product.number_sold >= int(number_sold):
                    return True
                return False

            products = filter(sold_filter, products)

        if location is not None:
            products = products.filter(location__contains=location)

        serializer = ProductSerializer(
            products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def liked(self, request):
        """
        using the function name liked to be use in URL when getting
        http://localhost:8000/products/liked
        and details = false on action because we getting multiple products

        this is what will return array of object Like:
        [
            {
                "id": 3,
                "product": {
                    "url": "http://localhost:8000/products/2",
                    "deleted": null,
                    "name": "Golf",
                    "price": 653.59,
                    "description": "1994 Volkswagen",
                    "quantity": 4,
                    "created_date": "2019-07-10",
                    "location": "Zhongshan",
                    "image_path": null,
                    "customer": "http://localhost:8000/customers/4",
                    "category": "http://localhost:8000/productcategories/2"
                }
            }
        ]

        """
        customer = Customer.objects.get(user=request.auth.user)
        liked_products = Like.objects.filter(customer=customer)
        serializer = LikeProductSerializer(
        liked_products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'], detail=True)
    def like(self, request, pk=None):
        """
        finction above name like so the url will be:
        /products/1/like and the number 1 for the pk for the product that we want to like
        @api {POST} /products/1/like POST new like_product
        @api {DELETE} /products/1/like DELETE like_product product id = 1
        for the current user that has liked(post) or dislike(delete)
        {
            "id": 4,
            "product": {
                "url": "http://localhost:8000/products/3",
                "deleted": null,
                "name": "Durango",
                "price": 541.17,
                "description": "1998 Dodge",
                "quantity": 2,
                "created_date": "2019-05-16",
                "location": "Górki Wielkie",
                "image_path": null,
                "customer": "http://localhost:8000/customers/6",
                "category": "http://localhost:8000/productcategories/2"
            }
        }        
        """
        customer = Customer.objects.get(user=request.auth.user)
        product = Product.objects.get(pk=pk)
        if request.method == "POST":
            try:
                like = Like.objects.get(customer=customer, product=product)
                print(like)
            except Like.DoesNotExist as ex:
                new_like = Like()
                new_like.customer = customer
                new_like.product = product
                new_like.save()
                serializer = LikeProductSerializer(new_like, many=False, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            try:
                like = Like.objects.get(customer=customer, product=product)
                like.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Like.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


class LikeProductSerializer(serializers.HyperlinkedModelSerializer)  :
    """JSON serializer for like product

    """
    class Meta:
        model = Like
        fields = ('id', 'product',)
        depth = 1
