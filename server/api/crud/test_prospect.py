import unittest

from api import schemas
from prospect import ProspectCrud

from fastapi import Depends
from sqlalchemy.orm.session import Session
from api.dependencies.db import get_db

# test failed due to ImportError (circular import)
# /api/crud/user.py imports api.core.security
#   UserCrud.create_user() references security.get_password_hash()
# /api/core/security.py imports api.crud.user.UserCrud
#   authenticate_user() references UserCrud.get_user_by_email()
# Note: Error not present when called from main.py
class TestCreateProspect(unittest.TestCase):
    def test_create_prospect_1(self):
        test_id = 12345
        email = "ggarciaxcv@gmail.com"
        first = "Gilberto"
        last = "Garcia"
        prospect_input = schemas.ProspectCreate(
            email=email, first_name=first, last_name=last
        )

        db = Depends(get_db)
        prospect = ProspectCrud.create_prospect(db, test_id, prospect_input)
        if prospect is None:
            print("error: no prospect created!")

        print(prospect.id)
        print(prospect.created_at)
        print(prospect.updated_at)

        self.assertEqual(prospect.email, email)
        self.assertEqual(prospect.first_name, first)
        self.assertEqual(prospect.last_name, last)


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()
