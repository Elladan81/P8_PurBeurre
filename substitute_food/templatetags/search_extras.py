from django import template

register = template.Library()


def dictLenght(value):
    """
    Function filter to calculate the lenght of all list inside of a dict
    """
    if isinstance(value, dict):
        lenght = 0
        for keys in value:
            for val in value[keys]:
                lenght += 1
    return lenght


register.filter('dictLenght', dictLenght)
