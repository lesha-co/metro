import unittest
from main import Metro, dict_to_list

STATION_NAMES = [
    "Новоясеневская",
    "Ясенево",
    "Тёплый Стан",
    "Коньково",
    "Беляево",
    "Калужская",
    "Новые Черёмушки",
    "Профсоюзная",
    "Академическая",
    "Ленинский проспект",
]
LINE_ID = 6


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

    def test_get_line_neighbour_ids(self):
        m = Metro('data.json')
        station = dict_to_list(m.get_stations_by_name("Киевская", line=4))[0]
        neighbour_a = dict_to_list(m.get_stations_by_name("Смоленская", line=4))[0]
        neighbour_b = dict_to_list(m.get_stations_by_name("Студенческая", line=4))[0]
        neighbour_c = dict_to_list(m.get_stations_by_name("Выставочная", line=4))[0]
        station_id = station["key"]
        neighbours = m.get_line_neighbour_ids(station_id)
        self.assertIn(neighbour_a["key"], neighbours)
        self.assertIn(neighbour_b["key"], neighbours)
        self.assertIn(neighbour_c["key"], neighbours)

    def test_line_neighbours_count(self):
        m = Metro('data.json')
        station_ids = m.get_all_station_ids()

        station = dict_to_list(m.get_stations_by_name("Киевская", line=4))[0]
        except_station_id = station["key"]

        for station_id in station_ids:
            line_neighbours = m.get_line_neighbour_ids(station_id)
            if station_id != except_station_id:
                self.assertTrue(len(line_neighbours) in [1, 2])
            # testing get_neighbours for junction stations
            else:
                self.assertTrue(len(line_neighbours) == 3)

    def test_get_stations_by_name(self):
        name = "Киевская"
        m = Metro('data.json')
        result = dict_to_list(m.get_stations_by_name(name))
        self.assertEqual(3, len(result))

    def test_get_stations_by_name_line(self):
        name = "Киевская"
        m = Metro('data.json')
        result = dict_to_list(m.get_stations_by_name(name, line=4))
        self.assertEqual(1, len(result))

    def test_continue_line(self):
        m = Metro('data.json')
        st1 = dict_to_list(m.get_stations_by_name("Новоясеневская"))[0]
        st2 = dict_to_list(m.get_stations_by_name("Ясенево"))[0]
        st3 = dict_to_list(m.get_stations_by_name("Тёплый Стан"))[0]
        st3_id = m.continue_line(st1["key"], st2["key"])
        self.assertEqual(st3_id, st3["key"])

    def test_continue_line_end(self):
        m = Metro('data.json')
        st1 = dict_to_list(m.get_stations_by_name("Новоясеневская"))[0]
        st2 = dict_to_list(m.get_stations_by_name("Ясенево"))[0]
        st_none_id = m.continue_line(st2["key"], st1["key"])
        self.assertIsNone(st_none_id)

    def test_continue_line_junction(self):
        m = Metro('data.json')
        st1 = dict_to_list(m.get_stations_by_name("Киевская", line=4))[0]
        st2 = dict_to_list(m.get_stations_by_name("Смоленская", line=4))[0]
        st_none_id = m.continue_line(st2["key"], st1["key"])
        self.assertIsNone(st_none_id)

    def test_each_link_has_formed_key(self):
        m = Metro('data.json')
        links = m.links
        for link in links:
            _from = link[:-3]
            _to = link[-3:]
            self.assertEqual(int(_from), links[link]["fromStationId"])
            self.assertEqual(int(_to), links[link]["toStationId"])


class MapRoutingTestCase(unittest.TestCase):
    def test_continue_line_until_transfer_or_end(self):
        m = Metro('data.json')

        station_ids = [dict_to_list(m.get_stations_by_name(station_name, line=LINE_ID))[0]["key"]
                       for station_name in STATION_NAMES]

        stack = m.continue_line_until_transfer_or_end(station_ids[0], station_ids[1])
        self.assertListEqual(stack, station_ids)
        stack = m.continue_line_until_transfer_or_end(station_ids[-1], station_ids[-2])
        self.assertListEqual(stack, station_ids[::-1])

    def test_get_line_segment_from_station(self):
        m = Metro('data.json')
        station_ids = [dict_to_list(m.get_stations_by_name(station_name, line=LINE_ID))[0]["key"]
                       for station_name in STATION_NAMES]
        non_transfer_station_ids = [station_id for station_id in station_ids
                                    if not m.is_station_a_transfer_station(station_id)]
        for station_id in non_transfer_station_ids:
            stack = m.get_line_segment_from_station(station_id)
            self.assertSetEqual(set(stack), set(station_ids))

    def test_get_links(self):
        m = Metro('data.json')
        st1 = dict_to_list(m.get_stations_by_name("Новоясеневская"))[0]
        st2 = dict_to_list(m.get_stations_by_name("Ясенево"))[0]
        st3 = dict_to_list(m.get_stations_by_name("Битцевский парк"))[0]

        links = m.get_links(st1["key"], st2["key"], include_transfers=False)
        self.assertEqual(len(links), 1)
        self.assertTrue(m.are_stations_adjacent(st1["key"], st2["key"], include_transfers=False))

        links = m.get_links(st1["key"], st3["key"], include_transfers=False)
        self.assertEqual(len(links), 0)
        self.assertFalse(m.are_stations_adjacent(st1["key"], st3["key"], include_transfers=False))

        links = m.get_links(st1["key"], st3["key"], include_transfers=True)
        self.assertEqual(len(links), 1)
        self.assertTrue(m.are_stations_adjacent(st1["key"], st3["key"], include_transfers=True))


if __name__ == '__main__':
    unittest.main()
