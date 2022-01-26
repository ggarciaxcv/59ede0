import unittest

from prospects import ProspectCreate

# test failed due to ImportError (circular import)
# /api/crud/user.py imports api.core.security
#   UserCrud.create_user() references security.get_password_hash()
# /api/core/security.py imports api.crud.user.UserCrud
#   authenticate_user() references UserCrud.get_user_by_email()
# Note: Error not present when called from main.py
class TestProspectCreate(unittest.TestCase):
    def test_init_1(self):
        email = "ggarciaxcv@gmail.com"
        first = "Gilberto"
        last = "Garcia"
        prospect = ProspectCreate(email=email, first_name=first, last_name=last)

        print(prospect.email)
        print(prospect.first_name)
        print(prospect.last_name)
        self.assertEqual(prospect.email, email)
        self.assertEqual(prospect.first_name, first)
        self.assertEqual(prospect.last_name, last)


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()
