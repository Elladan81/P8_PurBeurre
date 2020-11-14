from django.test import TestCase, Client
from .models import Product, Category


class ProductModelTest(TestCase):
    """
    Tests for the product model
    """

    def test_string_representation(self):
        """
        Test the return of the product model
        """
        product = Product(productName="Pizza")
        self.assertEqual(str(product), product.productName)


class TestSearch(TestCase):
    """
    Tests for the searchs functionnalities
    """

    def test_search_one_object(self):
        """
        Test one object search
        """
        client = Client()
        Product.objects.create(productName="Test")
        response = client.post(
            '/search/', {"product_name": "Test"}, follow=True)
        self.assertContains(response, "Test")

    def test_find_substitute(self):
        """
        Test substitute search in the same category
        """
        client = Client()
        obj1 = Product.objects.create(
            productName="Test", productURL="http://test.com")
        obj2 = Product.objects.create(
            productName="Test2", productURL="http://test2.com")
        category = Category.objects.create(categoryName="categoryTest")
        category.products.add(obj1)
        category.products.add(obj2)
        response = client.post(
            '/find_substitute/Test/2', follow=True)
        self.assertEqual(
            response.context['product_by_category']['categoryTest'][0], obj1)
