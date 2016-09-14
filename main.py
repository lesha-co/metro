import json
from typing import List, Dict
list_of_dicts_T = List[Dict]


def dict_to_list(d):
    return [{**v} for (k, v) in d.items()]


def print_link(link):
    return "{{{}-{}}}".format(link["fromStationId"], link["toStationId"])


class LineSegment:
    def __init__(self):
        self.stations = []
        self.transfers = []

    def get_length(self):
        pass


class Metro:
    """
    :type links: Dict[Dict[type:str]]
    """
    def run_checks(self, d):
        assert "stations" in d
        assert "links" in d

    def __init__(self, full_map):
        if type(full_map) is dict:
            pass
        elif type(full_map) is str:
            with open(full_map, encoding="utf8") as data_file:
                full_map = json.load(data_file)
        else:
            raise TypeError("full_map should be either a str or dict, not {}".format(type(full_map)))

        self.run_checks(full_map)

        self.links = full_map["links"]
        self.stations = full_map['stations']
        # preparing
        for (station_id, station) in self.stations.items():
            station["linkIds"] = [str(link_id) for link_id in station["linkIds"]]
            station["key"] = station_id
        for (link_id, link) in self.links.items():
            link["fromStationId"] = str(link["fromStationId"])
            link["toStationId"] = str(link["toStationId"])

    def print_station(self, station_no):
        station = self.get_station_by_id(station_no)
        return "[{}-({})]".format(station["name"], station["key"])

    def get_transfer_stations(self):
        return [station_id for (station_id, station) in self.stations.items()
                if "isTransferStation" in station and station["isTransferStation"]]

    def get_not_transfer_stations(self):
        transfer_stations = self.get_transfer_stations()
        return [station_id for station_id in self.get_all_station_ids()
                if station_id not in transfer_stations]

    def get_all_station_ids(self):
        return [station_id for (station_id, station) in self.stations.items()]

    def get_station_by_id(self, station_id: str) -> dict:
        return self.stations[str(station_id)]

    def get_stations_by_name(self, name: str, line: int=None) -> dict:
        candidates = {station_id: station for (station_id, station) in self.stations.items()
                      if station["name"] == name}
        if line:
            candidates = {station_id: station for (station_id, station) in candidates.items()
                          if station['lineId'] == line}

        return candidates

    def get_neighbours(self, station_id: str, link_type: str=None) -> list_of_dicts_T:
        """
        Return link objects for line neighbours and transfer neighbours
        :param station_id:
        :return:
        """
        station = self.get_station_by_id(station_id)
        link_ids = station["linkIds"]
        links = []
        for link_id in link_ids:
            link = self.links[link_id]
            if link_type and link["type"] != link_type:
                continue
            other_station_id = self.follow_link(station_id, link)
            new_link = {**link, "otherStationId": other_station_id}
            links.append(new_link)
        return links

    def get_line_neighbour_links(self, station_id:str):
        return self.get_neighbours(station_id, link_type="link")

    def get_line_neighbour_ids(self, station_id: str):
        return [link["otherStationId"] for link in self.get_line_neighbour_links(station_id)]

    def is_station_a_transfer_station(self, station_id):
        neighbours = self.get_neighbours(station_id, link_type="transfer")
        transfer_neighbours_ids = [link["otherStationId"] for link in neighbours]
        return len(transfer_neighbours_ids) > 0

    def is_station_a_termination_station(self, station_id):
        neighbours = self.get_line_neighbour_ids(station_id)
        return len(neighbours) == 1

    def is_station_a_junction_station(self, station_id):
        neighbours = self.get_line_neighbour_ids(station_id)
        return len(neighbours) > 2

    def get_next_link_in_line(self, station_id_a: str, station_id_b: str) -> dict:
        if self.is_station_a_junction_station(station_id_b):
            return None

        if self.is_station_a_transfer_station(station_id_b):
            return None

        b_neighbours = self.get_line_neighbour_links(station_id_b)
        assert len(b_neighbours) in [1, 2]
        next_link = [link for link in b_neighbours if link["otherStationId"] != station_id_a]
        assert len(next_link) in [0, 1]
        if len(next_link) == 0:
            return None
        if len(next_link) == 1:
            return next_link[0]

    def get_next_station_in_line(self, station_id_a: str, station_id_b: str) -> str:
        """
        Return id of station C in line:
            ? -- A -- B -- C -- ?
        Return None if B is the last station or if B is the junction station

        :param station_id_a:
        :param station_id_b:
        :return:
        """
        next_link=self.get_next_link_in_line(station_id_a, station_id_b)
        if next_link:
            return next_link["otherStationId"]
        else:
            return None

    def follow_link(self, station_id_a: str, link_a_b: dict) -> str:
        if link_a_b["fromStationId"] == station_id_a or link_a_b["toStationId"] == station_id_a:
            return [link_a_b[k] for k in ["fromStationId", "toStationId"] if link_a_b[k] != station_id_a][0]
        else:
            return None

    def get_route_until_transfer_or_end(self, station_id_a: str, link_a_b: dict):
        stack = [station_id_a, self.follow_link(station_id_a, link_a_b)]
        links = [link_a_b]
        while True:
            next_link = self.get_next_link_in_line(stack[-2], stack[-1])
            if next_link:
                next_station = self.follow_link(stack[-1], next_link)
                if next_station != station_id_a:
                    stack.append(next_station)
                    links.append(next_link)
            else:
                break
        return {
            "stations": stack,
            "links": links
        }

    def continue_line_until_transfer_or_end(self, station_id_a: str, link_a_b: dict):
        data = self.get_route_until_transfer_or_end(station_id_a, link_a_b)
        return data["stations"]

    def get_line_segment_from_station(self, station_id):
        """
        Return metro line segment (list of ids) between two transfer stations containing said station,
        including transfer stations
        Return [station_id] if station_id is transfer station

        Junction stations (currently only Киевская) are counted as transfer stations
        :param station_id:
        :return:
        """
        station = self.get_station_by_id(station_id)
        if "isTransferStation" in station and station["isTransferStation"]:
            return [station_id]
        else:
            if (self.is_station_a_junction_station(station_id) or
                    self.is_station_a_transfer_station(station_id)):
                return [station_id]
            else:
                neighbour_links = self.get_line_neighbour_links(station_id)
                assert len(neighbour_links) in [1, 2]
                stacks = []
                links = []
                for neighbour_link in neighbour_links:
                    data = self.get_route_until_transfer_or_end(station_id, neighbour_link)
                    stacks.append(data["stations"])
                    links.extend(data["links"])
                # line :      A - B ->C<- D - E
                # stacks[0]   C - D - E
                # stacks[1]   C - B - A
                result_segment = stacks[0]
                if len(stacks) == 2:
                    second_stack = stacks[1][:0:-1]
                    result_segment = second_stack+result_segment

                return {
                    "stations": result_segment,
                    "links": links
                }

    def get_links(self, station_id_a, station_id_b, include_transfers=False):
        station_id_a = str(station_id_a)
        station_id_b = str(station_id_b)
        # every link has key like
        #     XXXYYY or XXYYY
        # where X and Y are station ids (Y has leading zeroes)
        fmt = "{a}{b:0>3}"
        possible_keys = [fmt.format(a=station_id_a, b=station_id_b),
                         fmt.format(a=station_id_b, b=station_id_a)]

        cur_links = [self.links[key] for key in possible_keys if key in self.links]

        if not include_transfers:
            cur_links = [link for link in cur_links if link["type"] == "link"]

        return cur_links

    def are_stations_adjacent(self, station_id_a, station_id_b, include_transfers=False):
        return self.get_links(station_id_a, station_id_b, include_transfers) != []

    def get_sum_length_of_links(self, links):
        return sum([link["weightTime"] for link in links])