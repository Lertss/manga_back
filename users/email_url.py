from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountURL(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        url = ("http://localhost:8080/account-confirm-email/" + emailconfirmation.key)
        return url
