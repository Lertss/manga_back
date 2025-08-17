from allauth.account.models import EmailAddress
from rest_framework.request import Request

from users.models import CustomUser


def user_instance_func(request_user_email: str) -> CustomUser:
    """Returns a user instance by its email address, using the CustomUser model."""
    return CustomUser.objects.get(email=request_user_email)


def existing_user_func(new_email: str, user_instance: CustomUser) -> CustomUser:
    """Checks for another user at the specified new email address, except for the current user (user_instance),
    and returns the first found instance if such a user exists."""
    return CustomUser.objects.filter(email=new_email).exclude(id=user_instance.id).first()


def change_email_address(new_email: str, user_instance: CustomUser, request: Request) -> None:
    """Changes the user's email address. It updates the existing address if it exists,
    or creates a new one if there are no records in the account_emailaddress table.
    After that, it changes the user's primary email address, updates its confirmation,
    and sends a confirmation email to the new address."""
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
