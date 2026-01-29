from locust import HttpUser, task, between
from helpers import create_random_string

class AppUser(HttpUser):
    wait_time = between(2, 5)

   # @task 
    def random_text(self):
        myText = create_random_string(10)
        self.client.get("/text/"+ myText)

    @task 
    def hello_world(self):
        self.client.get("/")