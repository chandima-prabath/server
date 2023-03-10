import unittest
from accounts import UserAccountSystem

class TestUserAccountSystem(unittest.TestCase):

    def setUp(self):
        self.uas = UserAccountSystem(host="192.168.65.6",user="hanskingdom",password="06J3LND9NFH",database="hanskingdom")
        self.uas.conn.autocommit = True

    def test_register_user(self):
        email = "testuser@test.com"
        username = "testuser"
        password = "testpassword"
        profile_picture = "static/default_profile.png"

        # Test case where profile_picture is provided
        self.assertTrue(self.uas.register_user(email, username, password, profile_picture))

        # Test case where profile_picture is not provided
        self.assertTrue(self.uas.register_user(email, username, password, None))

        # Test case where email already exists
        self.assertFalse(self.uas.register_user(email, "new_username", "new_password", profile_picture))

    def test_authenticate_user(self):
        email = "testuser@test.com"
        password = "testpassword"
        self.assertTrue(self.uas.authenticate_user(email, password))

        # Test case where email or password is incorrect
        self.assertFalse(self.uas.authenticate_user(email, "wrongpassword"))
        self.assertFalse(self.uas.authenticate_user("wrongemail@test.com", password))

    def test_delete_user(self):
        email = "testuser@test.com"
        self.uas.delete_user(email)

        # Verify that user has been deleted
        users = self.uas.list_users()
        self.assertNotIn((email, "testuser"), users)

    def test_update_password(self):
        email = "testuser@test.com"
        new_password = "newpassword"
        self.uas.update_password(email, new_password)

        # Verify that password has been updated
        self.assertTrue(self.uas.authenticate_user(email, new_password))

    def test_list_users(self):
        users = self.uas.list_users()
        self.assertIsInstance(users, list)

    def test_update_username(self):
        email = "testuser@test.com"
        new_username = "newusername"
        self.uas.update_username(email, new_username)

        # Verify that username has been updated
        self.assertEqual(self.uas.get_username(email), new_username)

    def test_update_profile_picture(self):
        email = "testuser@test.com"
        profile_picture = "static/default_profile.png"
        self.uas.update_profile_picture(email, profile_picture)

        # Verify that profile picture has been updated
        cursor = self.uas.conn.cursor()
        cursor.execute("SELECT profile_picture FROM users WHERE email=%s", (email,))
        row = cursor.fetchone()
        self.assertIsNotNone(row[0])

if __name__ == '__main__':
    unittest.main()
