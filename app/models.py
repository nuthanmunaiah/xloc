from django.db import models


class Function(models.Model):
    name = models.CharField(max_length=255, blank=False)
    file = models.CharField(max_length=255, blank=False)
    sloc = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'file')
        db_table = 'function'

    @property
    def identity(self):
        return '{0}@{1}'.format(self.name, self.file)

    def __str__(self):
        return self.identity

    def __repr__(self):
        return self.identity

    def __hash__(self):
        return hash(self.identity)

    def __eq__(self, other):
        return self.identity == other.identity

    def __ne__(self, other):
        return self.identity != other.identity
