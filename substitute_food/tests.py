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
        product = Product(product_name="Pizza")
        self.assertEqual(str(product), product.product_name)


class TestSearch(TestCase):
    """
    Tests for the searchs functionnalities
    """

    def test_search_one_object(self):
        """
        Test one object search
        """
        client = Client()
        Product.objects.create(product_name="Test")
        response = client.post(
            '/search/', {"product_name": "Test"}, follow=True)
        self.assertContains(response, "Test")

    def test_find_substitute(self):
        """
        Test substitute search in the same category
        """
        client = Client()
        obj1 = Product.objects.create(
            product_name="Test", product_url="http://test.com")
        obj2 = Product.objects.create(
            product_name="Test2", product_url="http://test2.com")
        category = Category.objects.create(category_name="categoryTest")
        category.products.add(obj1)
        category.products.add(obj2)
        response = client.post(
            '/find_substitute/test/' + str(obj2.id) + '/', follow=True)
        self.assertEqual(
            response.context['product_by_category']["categoryTest"][0], obj1)
        self.assertNotContains(
            response.context['product_by_category']["categoryTest"][0], obj2)
