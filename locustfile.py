from locust import between
from locust.user.users import HttpUser
from locust.user.task import task


class SampleHttpUser(HttpUser):

    host = 'https://example.com'

    wait_time = between(1, 5)

    @task
    def root(self):
        self.client.get("/")
