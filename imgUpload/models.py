from django.db import models



class Image(models.Model):
    image = models.ImageField(upload_to='images')
    def __str__(self):
        return str(self.pk)



class Person(models.Model):
    ID_number = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)   
    surname = models.CharField(max_length=50)
    sex = models.CharField(max_length=4)
    birthdate = models.CharField(max_length=20)
    nationality = models.CharField(max_length=20)
    expire =  models.CharField(max_length=20)
    
    def __str__(self):
        return f"{str(self.name)} {str(self.surname)}"
    

class Scan(models.Model):
    person = models.ForeignKey("Person", verbose_name="Person", on_delete=models.CASCADE)
    GEO_location = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)
    image = models.ForeignKey("Image", verbose_name="Passport_Image", on_delete=models.CASCADE)
    def __str__(self):
        return f"{str(self.person.ID_number)} {str(self.date)}"



