from django.db import models
from oasis import settings
from app.Models.posts import Post

STATUS =[
    ('pending', 'Pending'),
    ('inreview', 'InReview'),
    ('approved', 'Approved'),
]


class ReportingAndComplains(models.Model):
    reportedBy = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportedBy')
    reportedUser= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportedUser')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=200)    
    adminAction = models.CharField(max_length=300, null=True, blank=True)
    status= models.CharField(max_length=80, choices=STATUS, default='pending')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reportedUser} is reported by {self.reportedBy}"
