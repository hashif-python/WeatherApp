from django.db import models

class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.FloatField(null=True)
    humidity = models.FloatField(null=True)
    wind = models.FloatField(null=True)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set when created

    def __str__(self):
        return self.city
    

    
