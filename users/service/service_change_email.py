from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
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
        email_address = email_addresses.first()
        email_address.email = new_email
        email_address.save()
    else:
        # Create a new record in the account_emailaddress table
        EmailAddress.objects.create(user=user_instance, email=new_email, primary=True, verified=False)

    # Change the user's email to a new one
    user_instance.email = new_email
    user_instance.save()

    # Send a confirmation email to the new address
    user_instance.emailaddress_set.filter(primary=True).update(email=new_email, verified=False)
    send_email_confirmation(request, user_instance)
