from __future__ import unicode_literals

from io import BytesIO

from django.core.files import File
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from PIL import Image


class Author(models.Model):
    """
    Represents an author of manga.

    Attributes:
        id (int): Primary key.
        first_name (str): Author's first name.
        last_name (str): Author's last name.
    """

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(_("First name"), max_length=50)
    last_name = models.CharField(_("Last name"), max_length=50)

    def __str__(self):
        """
        Return a string representation of the author.

        Returns:
            str: Author's full name.

        Example:
            str(author)
        """
        return f"{self.first_name}, {self.last_name}"


class Country(models.Model):
    """
    Represents a country associated with manga or author.

    Attributes:
        id (int): Primary key.
        country_name (str): Name of the country.
    """

    id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["country_name"]

    def __str__(self):
        """
        Return a string representation of the country.

        Returns:
            str: Country name.

        Example:
            str(country)
        """
        return self.country_name


class Genre(models.Model):
    """
    Represents a genre of manga.

    Attributes:
        id (int): Primary key.
        genre_name (str): Name of the genre.
    """

    id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["genre_name"]

    def __str__(self):
        """
        Return a string representation of the genre.

        Returns:
            str: Genre name.

        Example:
            str(genre)
        """
        return self.genre_name


class Tag(models.Model):
    """
    Represents a tag for manga categorization.

    Attributes:
        id (int): Primary key.
        tag_name (str): Name of the tag.
    """

    id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["tag_name"]

    def __str__(self):
        """
        Return a string representation of the tag.

        Returns:
            str: Tag name.

        Example:
            str(tag)
        """
        return self.tag_name


class Category(models.Model):
    """
    Represents a manga category.

    Attributes:
        id (int): Primary key.
        category_name (str): Name of the category.
    """

    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        """
        Return a string representation of the category.

        Returns:
            str: Category name.

        Example:
            str(category)
        """
        return self.category_name


class Manga(models.Model):
    """
    Represents a manga title with its metadata and relations.

    Attributes:
        category (Category): Manga category.
        name_manga (str): Manga name.
        name_original (str): Original name.
        english_only_field (str): Unique English field.
        author (Author): Authors of the manga.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Update timestamp.
        country (Country): Countries associated.
        tags (Tag): Tags associated.
        genre (Genre): Genres associated.
        decency (bool): Adult content flag.
        review (str): Review text.
        avatar (Image): Avatar image.
        thumbnail (Image): Thumbnail image.
        slug (str): Unique slug.
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    name_manga = models.CharField(_("name_manga"), max_length=100, blank=False)
    name_original = models.CharField(_("name_original"), max_length=100, blank=True)
    english_only_field = models.CharField(max_length=255, unique=True, blank=False)
    author = models.ManyToManyField(Author, related_name="authors", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    country = models.ManyToManyField(Country, related_name="country", blank=False)
    tags = models.ManyToManyField(Tag, related_name="tags", blank=False)
    genre = models.ManyToManyField(Genre, related_name="genre", blank=False)
    decency = models.BooleanField(default=False, help_text="For adults? yes/no")
    review = models.TextField(max_length=1000, blank=False)
    avatar = models.ImageField(
        upload_to="static/images/avatars/",
        default="default/none_avatar.png/",
        blank=True,
    )
    thumbnail = models.ImageField(upload_to="media/products/miniava", blank=True, null=True)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        """
        Return a string representation of the manga.

        Returns:
            str: Manga name.

        Example:
            str(manga)
        """
        return self.name_manga

    def average_rating(self):
        """
        Calculate the average rating for the manga.

        Returns:
            float or None: Average rating or None if no ratings exist.

        Example:
            manga.average_rating()
        """
        return self.ratings.aggregate(Avg("rating"))["rating__avg"]

    def get_avatar_url(self):
        """
        Get the URL of the avatar image.

        Returns:
            str: URL of the avatar or empty string if not set.

        Example:
            manga.get_avatar_url()
        """
        if self.avatar:
            return self.avatar.url
        return ""

    def get_url(self):
        """
        Get the URL for the manga detail page.

        Returns:
            str: URL.

        Example:
            manga.get_url()
        """
        return f"/{self.slug}/"

    def save(self, *args, **kwargs):
        """
        Save the manga instance, generate slug if new, and update thumbnail if avatar changed.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None

        Example:
            manga.save()
        """
        if not self.slug:
            self.slug = slugify(self.english_only_field)
        avatar_changed = False
        if self.pk:
            orig = Manga.objects.get(pk=self.pk)
            avatar_changed = orig.avatar != self.avatar
        super().save(*args, **kwargs)
        if (not self.thumbnail and self.avatar) or avatar_changed:
            self.generate_thumbnail()

    def generate_thumbnail(self):
        """
        Generate and save a thumbnail image for the manga avatar.

        Raises:
            ValueError: If thumbnail generation fails.

        Returns:
            None

        Example:
            manga.generate_thumbnail()
        """
        try:
            if not self.avatar or not self.avatar.name.lower().endswith((".png", ".jpg", ".jpeg")):
                return
            with Image.open(self.avatar) as img:
                img = img.resize((120, 170))
                thumb_io = BytesIO()
                img.save(thumb_io, format="PNG", quality=85)
                thumb_file = File(thumb_io, name=f"thumb_{self.avatar.name}")
                self.thumbnail.save(thumb_file.name, thumb_file, save=False)
                super().save(update_fields=["thumbnail"])
        except Exception as e:
            raise ValueError(f"Error generating thumbnail: {e}")

    def get_thumbnail_url(self):
        """
        Get the URL of the thumbnail image without generating it.

        Returns:
            str: URL of the thumbnail or empty string if not set.

        Example:
            manga.get_thumbnail_url()
        """
        return self.thumbnail.url if self.thumbnail else ""


class Chapter(models.Model):
    """
    Represents a chapter of a manga.

    Attributes:
        manga (Manga): Related manga.
        title (str): Chapter title.
        chapter_number (int): Chapter number.
        volume (int): Volume number.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Update timestamp.
        slug (str): Unique slug.
    """

    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(_("title"), max_length=100, blank=True)
    chapter_number = models.IntegerField(_("chapter_number"), blank=False)
    volume = models.IntegerField(_("volume"), blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["manga", "volume", "chapter_number"],
                name="unique_chapter_per_manga",
            )
        ]

    def __str__(self):
        """
        Return a string representation of the chapter.

        Returns:
            str: Manga name and chapter number.

        Example:
            str(chapter)
        """
        return f"{self.manga.name_manga} - Chapter {self.chapter_number}"

    def data_g(self):
        """
        Get the creation date of the chapter in MM/DD/YYYY format.

        Returns:
            str: Formatted date string.

        Example:
            chapter.data_g()
        """
        return self.created_at.strftime("%m/%d/%Y")

    def save(self, *args, **kwargs):
        """
        Save the chapter instance and generate a slug based on manga, volume, and chapter number.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None

        Example:
            chapter.save()
        """
        self.slug = slugify(f"{self.manga.english_only_field}-{self.volume}-{self.chapter_number}")
        super().save(*args, **kwargs)


class Page(models.Model):
    """
    Represents a page in a manga chapter.

    Attributes:
        chapter (Chapter): Related chapter.
        image (Image): Page image.
        page_number (int): Page number in chapter.
    """

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="pages")  # r
    image = models.ImageField(upload_to="media/manga/pages/")
    page_number = models.PositiveIntegerField(_("page_number"))

    class Meta:
        constraints = [models.UniqueConstraint(fields=["chapter", "page_number"], name="unique_page_per_chapter")]
        ordering = ["page_number"]

    def get_image(self):
        """
        Get the URL of the page image.

        Returns:
            str: URL of the image or empty string if not set.

        Example:
            page.get_image()
        """
        if self.image:
            return self.image.url
        return ""

    def save(self, *args, **kwargs):
        """
        Save the page instance and auto-assign page number if not set.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None

        Example:
            page.save()
        """
        if not self.page_number:
            last_page = Page.objects.filter(chapter__id=self.chapter_id).order_by("-page_number").first()
            if last_page:
                self.page_number = last_page.page_number + 1
            else:
                self.page_number = 1
        super().save(*args, **kwargs)
