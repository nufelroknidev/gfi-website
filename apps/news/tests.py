from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.news.models import Post


class PostModelTests(TestCase):

    def test_post_str(self):
        post = Post.objects.create(
            title='Test Announcement',
            slug='test-announcement',
            content='<p>Test content.</p>',
            published_date=timezone.now(),
            is_published=True,
        )
        self.assertEqual(str(post), 'Test Announcement')

    def test_get_absolute_url(self):
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='<p>Content.</p>',
            published_date=timezone.now(),
            is_published=True,
        )
        self.assertIn('test-post', post.get_absolute_url())


class NewsViewTests(TestCase):

    def setUp(self):
        Post.objects.create(
            title='Published Post',
            slug='published-post',
            content='<p>Visible content.</p>',
            published_date=timezone.now(),
            is_published=True,
        )
        Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='<p>Hidden content.</p>',
            published_date=timezone.now(),
            is_published=False,
        )

    def test_news_list_returns_200(self):
        response = self.client.get('/en/news/')
        self.assertEqual(response.status_code, 200)

    def test_news_list_shows_only_published(self):
        response = self.client.get('/en/news/')
        self.assertContains(response, 'Published Post')
        self.assertNotContains(response, 'Draft Post')

    def test_news_detail_returns_200(self):
        response = self.client.get('/en/news/published-post/')
        self.assertEqual(response.status_code, 200)

    def test_news_detail_unpublished_returns_404(self):
        response = self.client.get('/en/news/draft-post/')
        self.assertEqual(response.status_code, 404)
