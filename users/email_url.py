from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountURL(DefaultAccountAdapter):
    """
    Custom account adapter for generating email confirmation URLs.
    """

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Generate the email confirmation URL for a user.

        Args:
            request: The HTTP request object.
            emailconfirmation: The email confirmation instance.

        Returns:
            str: The email confirmation URL.

        Example:
            CustomAccountURL().get_email_confirmation_url(request, emailconfirmation)
        """
        url = "http://localhost:8080/account-confirm-email/" + emailconfirmation.key
        return url
