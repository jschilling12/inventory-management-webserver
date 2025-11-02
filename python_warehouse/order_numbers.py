import random
import string

order_id = {}

def random_string_generator(size= 5, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(email):
    while True:
        order_new_id = random_string_generator()
        if order_new_id not in order_id:
            order_id[email] = order_new_id
            return order_new_id