import string
import random

def code_generator(size=16, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))
