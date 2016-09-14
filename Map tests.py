import unittest
from main import Metro,dict_to_list


class MapAnalyticsTestCase(unittest.TestCase):
    def test_transfer_stations(self):
        m = Metro('data.json')
        s = m.get_transfer_stations()
        st1 = dict_to_list(m.get_stations_by_name("Новоясеневская"))[0]
        st2 = dict_to_list(m.get_stations_by_name("Ясенево"))[0]
        self.assertIn(st1["key"], s)
        self.assertNotIn(st2["key"], s)

    def test_non_transfer_stations(self):
        m = Metro('data.json')
        s = m.get_not_transfer_stations()
        st1 = dict_to_list(m.get_stations_by_name("Новоясеневская"))[0]
        st2 = dict_to_list(m.get_stations_by_name("Ясенево"))[0]
        self.assertNotIn(st1["key"], s)
        self.assertIn(st2["key"], s)

    def test_get_neighbours(self):
        m = Metro('data.json')

        st1 = dict_to_list(m.get_stations_by_name("Новоясеневская"))[0]
        st2 = dict_to_list(m.get_stations_by_name("Ясенево"))[0]
        st3 = dict_to_list(m.get_stations_by_name("Битцевский парк"))[0]
        neighbours = m.get_neighbours(st1['key'])
        line_neighbours_ids = [link["otherStationId"] for link in neighbours if link["type"] == "link"]
        transfer_neighbours_ids = [link["otherStationId"] for link in neighbours if link["type"] == "transfer"]
        self.assertIn(int(st2['key']), line_neighbours_ids)
        self.assertIn(int(st3['key']), transfer_neighbours_ids)

    def test_line_neighbours_count(self):
        m = Metro('data.json')
        station_ids = m.get_all_station_ids()

        station = dict_to_list(m.get_stations_by_name("Киевская", line=4))[0]
        except_station_no = station["key"]

        for station_id in station_ids:
            neighbours = m.get_neighbours(station_id)
            line_neighbours = [link["otherStationId"] for link in neighbours if link["type"] == "link"]
            if station_id != except_station_no:
                self.assertTrue(len(line_neighbours) in [1, 2])
            # testing get_neighbours for junction stations
            else:
                self.assertTrue(len(line_neighbours) == 3)

    def test_get_stations_by_name(self):
        name = "Киевская"
        m = Metro('data.json')
        result = dict_to_list(m.get_stations_by_name(name))
        self.assertEqual(3, len(result))
        result = dict_to_list(m.get_stations_by_name(name, line=4))
        self.assertEqual(1, len(result))

if __name__ == '__main__':
    unittest.main()
