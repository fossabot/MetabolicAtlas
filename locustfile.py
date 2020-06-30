## pip install locustio
## locust --host=https://csbi.chalmers.se

from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
    # def on_start(self):
    #     """ on_start is called when a Locust start before any task is scheduled """
        # self.login()

    # def on_stop(self):
    #     """ on_stop is called when the TaskSet is stopping """
    #     self.logout()

    # def login(self):
    #     self.client.post("/login", {"username":"ellen_key", "password":"education"})

    # def logout(self):
    #     self.client.post("/logout", {"username":"ellen_key", "password":"education"})

    @task(1)
    def index(self):
        self.client.get("/")
        self.client.get("/api/models")

    @task(2)
    def explore(self):
        self.client.get("/api/human1/gem_browser_tiles")

    @task(3)
    def explore(self):
        self.client.get("/api/human1/get_reaction/HMR_8313")

    @task(4)
    def browser(self):
        self.client.get("/api/human1/subsystem/transport_reactions/summary")

    @task(5)
    def viewer(self):
        self.client.get("/api/human1/metabolite/m00010s")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
