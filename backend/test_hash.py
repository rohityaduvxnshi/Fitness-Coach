#!/usr/bin/env python
from app.utils.password_hash import hash_password, verify_password

password = "test123"
hashed = hash_password(password)
print(f'✅ Hash works: {hashed[:30]}...')
is_valid = verify_password(password, hashed)
print(f'✅ Verify works: {is_valid}')
