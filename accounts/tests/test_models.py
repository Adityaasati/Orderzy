from django.test import TestCase
from accounts.models import User, UserProfile,ContactMessage
from django.contrib.gis.geos import Point


class UserModelTest(TestCase):
    
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'john@example.com')
        self.assertIsNone(user.phone_number)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_with_phone(self):
        user = User.objects.create_user(
            first_name='Jane',
            last_name='Doe',
            username='1234567890',  # Phone number as username
            password='testpass123'
        )
        self.assertEqual(user.phone_number, '1234567890')
        self.assertIsNone(user.email)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            username='adminuser',
            password='superpass123'
        )
        self.assertTrue(superuser.is_superadmin)
        self.assertTrue(superuser.is_staff)

    def test_user_role(self):
        user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123',
            role=User.RESTAURANT
        )
        self.assertEqual(user.get_role(), 'Restaurant')



class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
        # self.profile = UserProfile.objects.create(user=self.user)
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)


    def test_profile_str_method(self):
        # profile = UserProfile.objects.get_or_create(user=self.user)
        self.assertEqual(str(self.profile), 'john@example.com')

    def test_profile_str_no_user(self):
        # profile = UserProfile.objects.get_or_create(user=self.user)
        profile = UserProfile.objects.create(user=None)
        self.assertEqual(str(profile), 'No user')

    def test_save_location(self):
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.latitude = '12.34'
        profile.longitude = '56.78'
        profile.save() 
        self.assertEqual(profile.location.x, 56.78)  
        self.assertEqual(profile.location.y, 12.34) 


class ContactMessageModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
        # self.profile = UserProfile.objects.create(user=self.user)

    def test_contact_message_str_method(self):
        message = ContactMessage.objects.create(
            user=self.user,
            name='John Doe',
            message='This is a test message'
        )
        self.assertEqual(
            str(message), 
            f'Message from John Doe at {message.sent_at}'
        )
