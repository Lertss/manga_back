from allauth.account.models import EmailAddress
from rest_framework.request import Request

from users.models import CustomUser


def user_instance_func(request_user_email: str) -> CustomUser:
    """
    Retrieve a user instance by its email address using the CustomUser model.

    Args:
        request_user_email (str): The email address of the user.

    Returns:
        CustomUser: The user instance with the specified email.

    Raises:
        CustomUser.DoesNotExist: If no user with the given email exists.

    Example:
        user_instance_func('user@example.com')
    """
    return CustomUser.objects.get(email=request_user_email)


def existing_user_func(new_email: str, user_instance: CustomUser) -> CustomUser:
    """
    Check for another user at the specified new email address, excluding the current user.

    Args:
        new_email (str): The new email address to check.
        user_instance (CustomUser): The current user instance.

    Returns:
        CustomUser or None: The first found user instance with the new email, or None if not found.

    Example:
        existing_user_func('new@example.com', user_instance)
    """
    return CustomUser.objects.filter(email=new_email).exclude(id=user_instance.id).first()


def change_email_address(new_email: str, user_instance: CustomUser, request: Request) -> None:
    """
    Change the user's email address and send a confirmation email to the new address.

    Updates the existing address if it exists, or creates a new one if there are no records
    in the account_emailaddress table. Then updates the user's primary email address,
    resets its confirmation, and sends a confirmation email to the new address.

    Args:
        new_email (str): The new email address to set.
        user_instance (CustomUser): The user instance whose email is being changed.
        request (Request): The current request object.

    Returns:
        None

    Example:
        change_email_address('new@example.com', user_instance, request)
    """
    # Get records in the account_emailaddress table for the user
    email_addresses = EmailAddress.objects.filter(user=user_instance)

    if email_addresses.exists():
        # Update the existing email address
        email_address = email_addresses.first()
        email_address.email = new_email
        email_address.verified = False  # Reset verification status
        email_address.primary = True
        email_address.save()
    else:
        # Create a new record in the account_emailaddress table
        email_address = EmailAddress.objects.create(user=user_instance, email=new_email, primary=True, verified=False)

    # Update the user's email field
    user_instance.email = new_email
    user_instance.save()

    # Send a confirmation email to the new address
    email_address.send_confirmation(request)
