from common.models import Comment
from common.service.service import comment_object_filter
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from manga.models import Author, Category, Chapter, Country, Genre, Manga, Tag
from users.models import CustomUser


class CommentObjectFilterTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser1", gender="Male", adult=True)

        self.genre = Genre.objects.create(genr_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(counts="Afghanistan")
        self.category = Category.objects.create(cat_name="Manga")
        self.author = Author.objects.create(first_name="John", last_name="Doe")

        self.manga = Manga.objects.create(
            category=self.category,
            name_manga="manga-1",
            name_original="Original Name",
            english_only_field="manga-1",
            decency=True,
            review="Test Review 1",
            avatar=SimpleUploadedFile("test_avatar_1.png", b"", content_type="image/png"),
            thumbnail=SimpleUploadedFile("test_thumbnail_1.png", b"", content_type="image/png"),
            slug="manga-1",
        )

        self.manga.author.add(self.author)
        self.manga.counts.add(self.country)
        self.manga.genre.add(self.genre)
        self.manga.tags.add(self.tag)

        self.chapter = Chapter.objects.create(
            manga=self.manga,
            title="Chapter Title",
            chapter_number=1,
            volume=1,
            time_prod=timezone.now(),
            slug=None,
        )

        self.manga_comment_1 = Comment.objects.create(user=self.user, manga=self.manga, content="Comment 1 for Manga")
        self.manga_comment_2 = Comment.objects.create(user=self.user, manga=self.manga, content="Comment 2 for Manga")
        self.chapter_comment_1 = Comment.objects.create(
            user=self.user, chapter=self.chapter, content="Comment 1 for Chapter"
        )
        self.chapter_comment_2 = Comment.objects.create(
            user=self.user, chapter=self.chapter, content="Comment 2 for Chapter"
        )

    def test_comment_object_filter_manga(self):

        filtered_comments = comment_object_filter("manga", slug="manga-1")

        self.assertEqual(filtered_comments.count(), 2)
        self.assertIn(self.manga_comment_1, filtered_comments)
        self.assertIn(self.manga_comment_2, filtered_comments)
        self.assertNotIn(self.chapter_comment_1, filtered_comments)
        self.assertNotIn(self.chapter_comment_2, filtered_comments)

    def test_comment_object_filter_chapter(self):

        filtered_comments = comment_object_filter("chapter", slug="manga-1")

        self.assertEqual(filtered_comments.count(), 2)
        self.assertIn(self.chapter_comment_1, filtered_comments)
        self.assertIn(self.chapter_comment_2, filtered_comments)
        self.assertNotIn(self.manga_comment_1, filtered_comments)
        self.assertNotIn(self.manga_comment_2, filtered_comments)

    def test_comment_object_filter_invalid_model(self):

        filtered_comments = comment_object_filter("invalid_model", slug="manga-1")

        self.assertEqual(filtered_comments.count(), 0)
