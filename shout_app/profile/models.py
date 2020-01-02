from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(
            'authentication.User', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    supports = models.ManyToManyField('shouts.Shout', related_name='supported_by')

    def __str__(self):
        return self.user.username

    @property
    def is_verified(self):
        return self.user.account_verified()

    def support(self, shout):
        self.supports.add(shout)

    def not_support(self, shout):
        self.supports.remove(shout)

    def has_supported(self, shout):
        return self.supports.filter(slug=shout.slug).exists()
