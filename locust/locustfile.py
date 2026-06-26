from locust import HttpUser, task, between, events
import random
import string
import json


class URLShortenerUser(HttpUser):
    wait_time = between(0.1, 0.5)
    short_codes = []

    def on_start(self):
        for _ in range(5):
            self._create_url()

    def _create_url(self):
        domain = random.choice([
            "google.com", "github.com", "python.org",
            "stackoverflow.com", "wikipedia.org", "amazon.com",
        ])
        path = "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
        url = f"https://www.{domain}/{path}"
        with self.client.post(
            "/shorten",
            json={"url": url},
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.short_codes.append(data["short_code"])
                resp.success()
            elif resp.status_code == 429:
                resp.success()  
            else:
                resp.failure(f"Failed to create URL: {resp.status_code}")

    @task(5)
    def redirect(self):
        if not self.short_codes:
            return
        code = random.choice(self.short_codes)
        with self.client.get(
            f"/{code}",
            allow_redirects=False,
            catch_response=True,
        ) as resp:
            if resp.status_code in (301, 302):
                resp.success()
            elif resp.status_code == 429:
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(2)
    def create_url(self):
        self._create_url()

    @task(1)
    def get_analytics(self):
        if not self.short_codes:
            return
        code = random.choice(self.short_codes)
        with self.client.get(f"/analytics/{code}", catch_response=True) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Analytics error: {resp.status_code}")

    @task(1)
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def get_qr(self):
        if not self.short_codes:
            return
        code = random.choice(self.short_codes)
        with self.client.get(f"/qr/{code}", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 429:
                resp.success()
            else:
                resp.failure(f"QR error: {resp.status_code}")
