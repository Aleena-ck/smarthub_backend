import sys
sys.path.append('.')
from utils.security import get_password_hash

print(get_password_hash("123456"))