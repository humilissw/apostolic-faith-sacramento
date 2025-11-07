import random

def create_random_string(length):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    random_string = ""
    for i in range(length):
        random_string += random.choice(chars)
    return random_string