import requests
import unittest


class TestArtists(unittest.TestCase):

    artist_count = 1000
    pagination_start = 111
    pagination_limit = 222


    def setUp(self):
        pass


    def test_artist_all(self):
        response = requests.get("http://127.0.0.1:5000/artists/all").json()
        self.assertEqual(len(response), self.artist_count)

    def test_artist_all_pagination_start(self):

        payload = {"start": self.pagination_start}
        response = requests.get("http://127.0.0.1:5000/artists/all", params=payload).json()

        for api_object in response:
            self.assertGreaterEqual(api_object["id"], self.pagination_start)

    def test_artist_all_pagination_limit(self):

        payload = {"amount": self.pagination_limit}
        response = requests.get("http://127.0.0.1:5000/artists/all", params=payload).json()

        self.assertLessEqual(len(response), self.pagination_limit)

    def test_artist_id(self):

        for i in range(471, 474):

            request_url = "http://127.0.0.1:5000/artists/id/{}".format(i)
            response = requests.get(request_url).json()

            self.assertEqual(response["id"], i)

if __name__ == '__main__':
    unittest.main()