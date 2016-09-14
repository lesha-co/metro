import unittest
from main import Metro


class MapAnalyticsTestCase(unittest.TestCase):
    def test_transfer_stations(self):
        m = Metro('data.json')
        s = m.get_transfer_stations()

        self.assertIn("191", s)
        self.assertNotIn("105", s)

    def test_non_transfer_stations(self):
        m = Metro('data.json')
        s = m.get_not_transfer_stations()

        self.assertNotIn("191", s)
        self.assertIn("105", s)

    def test_get_neighbours(self):
        m = Metro('data.json')
        station_no = 106
        neighbours = m.get_neighbours(station_no)
        line_neighbours_ids = [link["otherStationId"] for link in neighbours if link["type"] == "link"]
        transfer_neighbours_ids = [link["otherStationId"] for link in neighbours if link["type"] == "transfer"]
        self.assertIn(105, line_neighbours_ids)
        self.assertIn(191, transfer_neighbours_ids)

    def test_line_neighbours_count(self):
        m = Metro('data.json')
        station_ids = m.get_all_station_ids()

        station = m.get_stations_by_name("Киевская", line=4)
        except_station_no = list(station.keys())[0]

        for station_id in station_ids:
            neighbours = m.get_neighbours(station_id)
            line_neighbours = [link["otherStationId"] for link in neighbours if link["type"] == "link"]
            if station_id != except_station_no:
                self.assertTrue(len(line_neighbours) in [1, 2])
            else:
                self.assertTrue(len(line_neighbours) == 3)

        # testing get_neighbours for junction stations

    def test_get_stations_by_name(self):
        name = "Киевская"
        m = Metro('data.json')
        result = m.get_stations_by_name(name)
        self.assertEqual(3, len(result.items()))
        result = m.get_stations_by_name(name, line=4)
        self.assertEqual(1, len(result.items()))

if __name__ == '__main__':
    unittest.main()
