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
        obj_test = Product.objects.create(product_name="Test", brands='Test', product_url="http://test.com")
        response = client.get('/search/', {'product_name': "Test"}, follow=True)
        self.assertEqual(response.context['products'][0], obj_test)

    def test_find_substitute_enough_objects(self):
        """
        Test substitute search in the same category
        """
        client = Client()
        obj1 = Product.objects.create(
            product_name="Test", product_url="http://test.com")
        obj2 = Product.objects.create(
            product_name="Test2", product_url="http://test2.com")
        obj3 = Product.objects.create(
            product_name="Test3", product_url="http://test3.com")
        obj4 = Product.objects.create(
            product_name="Test4", product_url="http://test4.com")
        obj5 = Product.objects.create(
            product_name="Test5", product_url="http://test5.com")
        category = Category.objects.create(category_name="category_test")
        category.products.add(obj1)
        category.products.add(obj2)
        category.products.add(obj3)
        category.products.add(obj4)
        category.products.add(obj5)
        response = client.get('/find_substitute/test/' + str(obj2.id) + '/', follow=True)
        self.assertEqual(response.context["product_by_category"]["category_test"][0], obj1)
        self.assertEqual(response.context["product_by_category"]["category_test"][1], obj3)
        self.assertEqual(response.context["product_by_category"]["category_test"][2], obj4)
        self.assertEqual(response.context["product_by_category"]["category_test"][3], obj5)
        self.assertEqual(len(response.context["product_by_category"]["category_test"]), 4)

    def test_find_substitute_not_enough_objects(self):
        """
        Test substitute search in the same category
        """
        client = Client()
        obj1 = Product.objects.create(
            product_name="Test", product_url="http://test.com")
        obj2 = Product.objects.create(
            product_name="PIM", product_url="http://test2.com")
        obj3 = Product.objects.create(
            product_name="PAM", product_url="http://test3.com")
        category = Category.objects.create(category_name="category_test")
        category.products.add(obj1)
        category.products.add(obj2)
        category.products.add(obj3)
        response = client.get('/find_substitute/test/' + str(obj1.id) + '/', follow=True)
        self.assertEqual(response.context["product_by_category"]["category_test"][0], obj2)
        self.assertEqual(response.context["product_by_category"]["category_test"][1], obj3)
