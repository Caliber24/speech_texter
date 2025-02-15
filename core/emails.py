from djoser import email

class ActivationEmail(email.ActivationEmail):
    template_name = 'activation.html'

class ConfirmationEmail(email.ConfirmationEmail):
    template_name = 'confirmation.html'

class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'password_reset.html'

class PasswordChangedConfirmationEmail(email.PasswordChangedConfirmationEmail):
    template_name = 'password_changed_confirmation.html'

