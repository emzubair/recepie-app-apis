from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase


from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recepie.serializers import TagSerializer


TAGS_URL = reverse('recepie:tag-list')


class PublicTagsAPITest(TestCase):
    """Test public APIs for of tags"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """test login is required to fetch tag lists"""

        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """Test the authoried user Tags APIs"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email='test@example.com', password='admin12345'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """ Test retrieving tags"""

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test user can retrieve only their tags"""

        user_2 = get_user_model().objects.create_user(
            email='admin@example.com', password='admin12345'
        )

        Tag.objects.create(user=user_2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
