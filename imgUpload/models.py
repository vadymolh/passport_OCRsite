from django.db import models



class Image(models.Model):
    #title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images')
    #done_image = models.ImageField(upload_to='done_images')
    def __str__(self):
        return self.pk