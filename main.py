import json


def dict_to_list(d):
    return [{**v, "key": k} for (k, v) in d.items()]


class Metro:
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
        for (link_id, link) in self.links.items():
            link["fromStationId"] = str(link["fromStationId"])
            link["toStationId"] = str(link["toStationId"])

    def get_transfer_stations(self):
        return [station_id for (station_id, station) in self.stations.items()
                if "isTransferStation" in station and station["isTransferStation"]]

    def get_not_transfer_stations(self):
        transfer_stations = self.get_transfer_stations()
        return [station_id for station_id in self.get_all_station_ids()
                if station_id not in transfer_stations]

    def get_all_station_ids(self):
        return [station_id for (station_id, station) in self.stations.items()]

    def get_station_by_id(self, station_id):
        return self.stations[str(station_id)]

    def get_stations_by_name(self, name, line=None):
        candidates = {station_id: station for (station_id, station) in self.stations.items()
                      if station["name"] == name}
        if line:
            candidates = {station_id: station for (station_id, station) in candidates.items()
                          if station['lineId'] == line}

        return candidates

    def get_neighbours(self, station_id):
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
            other_station_id = [link[k] for k in ["fromStationId", "toStationId"] if link[k] != station_id][0]
            new_link = {**link, "otherStationId": other_station_id}
            links.append(new_link)
        return links

    def get_line_neighbour_ids(self, station_id):
        neighbours = self.get_neighbours(station_id)
        return [link["otherStationId"] for link in neighbours if link["type"] == "link"]

    def is_station_a_transfer_station(self, station_id):
        neighbours = self.get_neighbours(station_id)
        transfer_neighbours_ids = [link["otherStationId"] for link in neighbours if link["type"] == "transfer"]
        return len(transfer_neighbours_ids) > 0

    def is_station_a_termination_station(self, station_id):
        neighbours = self.get_line_neighbour_ids(station_id)
        return len(neighbours) == 1

    def is_station_a_junction_station(self, station_id):
        neighbours = self.get_line_neighbour_ids(station_id)
        return len(neighbours) > 2

    def continue_line(self, station_id_a, station_id_b):
        """
        Return id of station C in line:
            ? -- A -- B -- C -- ?
        Return None if B is the last station or if B is the junction station

        :param station_id_a:
        :param station_id_b:
        :return:
        """
        if self.is_station_a_junction_station(station_id_b):
            return None

        if self.is_station_a_transfer_station(station_id_b):
            return None

        b_neighbours = self.get_line_neighbour_ids(station_id_b)
        assert len(b_neighbours) in [1, 2]
        other_station = [st_id for st_id in b_neighbours if st_id != station_id_a]
        assert len(other_station) in [0, 1]
        if len(other_station) == 0:
            return None
        if len(other_station) == 1:
            return other_station[0]

    def continue_line_until_transfer_or_end(self, station_id_a, station_id_b):
        stack = [station_id_a, station_id_b]
        while True:
            next_station = self.continue_line(stack[-2], stack[-1])
            if next_station and next_station != station_id_a:
                stack.append(next_station)
            else:
                break
        return stack

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
                neighbours = self.get_line_neighbour_ids(station_id)
                assert len(neighbours) in [1, 2]
                stacks = []
                for neighbour in neighbours:
                    stack = self.continue_line_until_transfer_or_end(station_id, neighbour)
                    stacks.append(stack)
                # line :      A - B ->C<- D - E
                # stacks[0]   C - D - E
                # stacks[1]   C - B - A
                result_segment = stacks[0]
                if len(stacks) == 2:
                    second_stack = stacks[1][1:]
                    result_segment = second_stack+result_segment
                return result_segment

    def get_links(self, station_id_a, station_id_b, include_transfers=False):
        station_id_a = str(station_id_a)
        station_id_b = str(station_id_b)
        # every link has key like
        #     XXXYYY or XXYYY
        # where X and Y are station ids (Y has leading zeroes)
        fmt = "{a}{b:0>3}"
        possible_keys = [fmt.format(a=station_id_a, b=station_id_b),
                         fmt.format(a=station_id_b, b=station_id_a)]

        links = [self.links[key] for key in possible_keys if key in self.links]

        if not include_transfers:
            links = [link for link in links if link["type"] == "link"]

        return links

    def are_stations_adjacent(self, station_id_a, station_id_b, include_transfers=False):
        return self.get_links(station_id_a, station_id_b, include_transfers) != []



