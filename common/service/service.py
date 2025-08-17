from common.models import Comment, MangaRating


def comment_object_filter(model: str, slug) -> Comment:
    """
    Retrieve comments filtered by model type (manga or chapter) and slug.

    Args:
        model (str): The type of model ('manga' or 'chapter').
        slug (str): The slug identifier for the manga or chapter.

    Returns:
        Comment: QuerySet of filtered Comment objects.

    Raises:
        None

    Example:
        comment_object_filter('manga', 'naruto')
    """
    if model == "manga":
        return Comment.objects.filter(manga__slug=slug)
    elif model == "chapter":
        print(Comment.objects.filter(chapter__slug=slug))
        return Comment.objects.filter(chapter__slug=slug)
    else:
        return Comment.objects.none()


def mangarating_object_filter(
    manga_id,
    user_id,
) -> MangaRating:
    """
    Retrieve the manga rating for a specific user and manga.

    Args:
        manga_id: The ID of the manga.
        user_id: The ID of the user.

    Returns:
        MangaRating: The MangaRating object or None if not found.

    Raises:
        None

    Example:
        mangarating_object_filter(1, 42)
    """
    return MangaRating.objects.filter(manga=manga_id, user=user_id).first()
