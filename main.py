import json


def dict_to_list(d):
    return [{**v, "key": k} for (k, v) in d.items()]


class Metro:
    def run_checks(self, d):
        assert "stations" in d
        assert "links" in d

    def __init__(self, full_map):
        if type(full_map) is dict:
            self.run_checks(full_map)
            self.full_map = full_map
        elif type(full_map) is str:
            with open(full_map, encoding="utf8") as data_file:
                full_map = json.load(data_file)
                self.run_checks(full_map)
                self.full_map = full_map

    def get_transfer_stations(self):
        return [station_no for (station_no, station) in self.full_map['stations'].items()
                if "isTransferStation" in station and station["isTransferStation"]]

    def get_not_transfer_stations(self):
        transfer_stations = self.get_transfer_stations()
        return [station_no for station_no in self.get_all_station_ids()
                if station_no not in transfer_stations]

    def get_all_station_ids(self):
        return [station_no for (station_no, station) in self.full_map['stations'].items()]

    def get_station_by_no(self, station_no):
        return self.full_map['stations'][str(station_no)]

    def get_stations_by_name(self, name, line=None):
        candidates = {station_no: station for (station_no, station) in self.full_map['stations'].items()
                      if station["name"] == name}
        if line:
            candidates = {station_no: station for (station_no, station) in candidates.items()
                          if station['lineId'] == line}

        return candidates

    def get_neighbours(self, station_no):
        station = self.get_station_by_no(station_no)
        link_ids = station["linkIds"]
        links = []
        for link_id in link_ids:
            link = self.full_map["links"][str(link_id)]
            other_station_id = [link[k] for k in ["fromStationId", "toStationId"] if link[k] != int(station_no)][0]
            new_link = {**link, "otherStationId": other_station_id}
            links.append(new_link)
        return links

    # def get_closest_transfer_stations(self, station_no):
    #    station = self.get_station(station_no)


def run():
    pass


if __name__ == "__main__":
    run()