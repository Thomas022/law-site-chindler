from django.contrib.admin.forms import AdminAuthenticationForm


class EmailOrUsernameAuthenticationForm(AdminAuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Usuário ou e-mail"
