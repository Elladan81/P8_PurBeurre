# Generated by Django 3.0.3 on 2020-02-13 15:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Favoris',
                'verbose_name_plural': 'Favoris',
                'ordering': ['product'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productName', models.CharField(max_length=100, unique=True)),
                ('shops', models.TextField()),
                ('brands', models.TextField()),
                ('productURL', models.URLField(unique=True, verbose_name='URL du produit')),
                ('nutriscore', models.CharField(max_length=1)),
                ('imgURL', models.URLField(null=True, verbose_name="URL de l'image du produit")),
            ],
            options={
                'verbose_name': 'Produit',
                'ordering': ['productName'],
            },
        ),
        migrations.CreateModel(
            name='UserFavoriteProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorites', models.ManyToManyField(blank=True, to='substitute_food.FavoriteProduct')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='favoriteproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoriteproduct_product', to='substitute_food.Product'),
        ),
        migrations.AddField(
            model_name='favoriteproduct',
            name='substitute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoriteproduct_substitute', to='substitute_food.Product'),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoryName', models.CharField(max_length=150, unique=True)),
                ('products', models.ManyToManyField(to='substitute_food.Product')),
            ],
            options={
                'verbose_name': 'Catégorie',
                'ordering': ['categoryName'],
            },
        ),
    ]
