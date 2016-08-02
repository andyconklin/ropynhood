import requests
import json

class Robinhood:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._headers = {"User-Agent": "Andy's Robinhood thing 0.1"}
        self._cache = {}
        self._accounts = {}
    def _robin_get(self, endpoint):
        print "_robin_get called on %s" % (endpoint)
        return requests.get(endpoint if "api.robinhood.com" in endpoint else "https://api.robinhood.com%s" % (endpoint), headers=self._headers)
    def _robin_post(self, endpoint, data={}):
        print "_robin_post called on %s" % (endpoint)
        return requests.post(endpoint if "api.robinhood.com" in endpoint else "https://api.robinhood.com%s" % (endpoint), data=data, headers=self._headers)
    def _assert_200(self, r):
        if r.status_code != 200:
            raise Exception("HTTP %d: %s" % (r.status_code, r.text))
        return True
    def login(self):
        """Log into Robinhood with the username and password from the constructor"""
        r = self._robin_post("/api-token-auth/", {"username":self._username, "password":self._password})
        self._assert_200(r)
        self._headers["Authorization"] = "Token %s" % (json.loads(r.text)["token"])
        r = self._robin_get("/accounts/")
        self._assert_200(r)
        self._accounts = json.loads(r.text)
        return True
    def logout(self):
        """Log out of Robinhood. Must be logged in."""
        r = self._robin_post("/api-token-logout/", data={})
        self._assert_200(r)
        del self._headers["Authorization"]
        return True
    def get_all_filled_orders(self):
        """Actually only gets the first page of orders."""
        r = self._robin_get("/orders/")
        self._assert_200(r)
        # get only the filled orders
        orders = [x for x in json.loads(r.text)["results"] if x["state"] == "filled"]
        for x in orders:
            # get instrument data and swap it into the order object
            instrument = x["instrument"]
            if instrument not in self._cache:
                instresp = self._robin_get(instrument)
                self._assert_200(instresp)
                self._cache[instrument] = json.loads(instresp.text)
            x["instrument"] = self._cache[instrument]
        # clear the instrument cache afterward because they could change before the next call
        self._cache = {}
        return orders
    def get_portfolio(self):
        """Get the user's portfolio information."""
        r = self._robin_get("/portfolios/%s/" % (self._accounts["results"][0]["account_number"]))
        self._assert_200(r)
        return json.loads(r.text)
    def get_portfolio_historicals(self, interval):
        """Get the user's historical portfolio performance."""
        r = self._robin_get("/portfolios/historicals/%s/?interval=%s" % (self._accounts["results"][0]["account_number"], interval))
        self._assert_200(r)
        return json.loads(r.text)

username = ""
password = ""

with open("mydeets.txt", mode="r") as f:
    username, password = f.read().split(" ")

robin = Robinhood(username, password)
