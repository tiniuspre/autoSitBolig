from requests import get, post
from time import sleep
import json


class SitBuildings:
    def __init__(self, not_available=False, city='Trondheim'):
        self.not_available = not_available
        self.url = "https://as-portal-api-prodaede2914.azurewebsites.net/graphql"
        self.unit = "HK23-33"
        if city == "*":
            self.queryes = {
                "all_housing": {"operationName": "GetHousingIds", "variables": {
                    "input": {"location": [{"parent": "Trondheim", "children": []}, {"parent": "Ålesund", "children": []}, {"parent": "Gjøvik", "children": []}],
                              "availableMaxDate": "2022-05-02T00:00:00.000Z", "showUnavailable": not_available,
                              "categories": ["Sbolig"], "offset": 0, "pageSize": 999999999}},
                                "query": "query GetHousingIds($input: GetHousingsInput!) {\n  housings(filter: $input) {\n    rentalObjectId\n    isAvailable\n    availableFrom\n    availableTo\n    hasActiveReservation\n    __typename\n  }\n}\n"}
                }
        else:
            self.queryes = {
                "all_housing": {"operationName":"GetHousingIds","variables":{"input":{"location":[{"parent":f"{city}","children":[]}],"availableMaxDate":"2022-05-02T00:00:00.000Z","showUnavailable":not_available, "categories":["Sbolig"], "offset":0, "pageSize":999999999}}, "query": "query GetHousingIds($input: GetHousingsInput!) {\n  housings(filter: $input) {\n    rentalObjectId\n    isAvailable\n    availableFrom\n    availableTo\n    hasActiveReservation\n    __typename\n  }\n}\n"}

            }

    def residentQuery(self, units):
        return {"operationName":"GetHousingIds","variables":{"input":{"rentalObjectIds":units,"showUnavailable":self.not_available, "reservationCode": ""}}, "query": "query GetHousingIds($input: GetHousingsInput!) {\n  housings(filter: $input) {\n    rentalObjectId\n    isAvailable\n    availableFrom\n    availableTo\n    hasActiveReservation\n    __typename\n  }\n}\n"}

    def adress(self, unit):
        return get(f"https://bolig.sit.no/page-data/no/unit/{unit.lower()}/page-data.json").json()['result']['data']['sanityEnhet']['building']['address']

    def request(self, unit,):
        return post(url=self.url, json=self.residentQuery(unit)).json()

    def is_available(self, resident_object):
        return bool(resident_object['data']['housings'][0]['isAvailable'])

    def all_resideses(self):
        residenses = []
        for resident in post(url=self.url, json=self.queryes['all_housing']).json()['data']['housings']:
            residenses.append(resident['rentalObjectId'])
        return self.request(residenses)['data']['housings']

    def filter_residenses_available(self):
        self.not_available = True
        ledige = 0
        opptatte = 0
        total = 0
        for house in self.all_resideses():
            if house['isAvailable']:
                ledige += 1
            elif not house['isAvailable']:
                opptatte += 1
            else:
                feil_bolig.append(house)
            total+=1

        return {
            "total": total,
            "ledige": ledige,
            "opptatte": opptatte
        }

    def rooms_unit_all(self):
        unit_info = {}
        count = 0
        all_resident = self.all_resideses()
        lengde = len(all_resident)
        for unit in all_resident:
            taken = False
            adress = self.adress(unit['rentalObjectId'])
            count+=1
            print(f"{count} av {lengde} | mangler {lengde-count}| {unit['rentalObjectId']}")
            for info in unit_info:
                if info == adress:
                    taken = True

            if taken:
                existing_units = unit_info[adress]['navn']
                existing_units.append(unit['rentalObjectId'])
                unit_info.update({
                    adress: {
                        'navn': existing_units
                    }
                })
            else:
                unit_info.update({
                    adress: {
                        'navn': [unit['rentalObjectId']]
                    }
                })

        with open('bolig.json', 'w') as json_file:
            json.dump(unit_info, json_file)
        return unit_info

    def getAvailableHouse(self, adress_to_find):
        with open('bolig.json', 'r') as f:
            data = json.load(f)
        is_available_data = {}
        for adress in data:
            if adress == adress_to_find:
                house = self.request(data[adress]['navn'])['data']['housings']
                available_count = 0
                for unit in house:
                    print(unit)
                    if unit['isAvailable']:
                        available_count +=1
                    is_available_data.update({unit['rentalObjectId']: unit['isAvailable']})
                if available_count == len(house):
                    is_available_data.update({"all_available": True})
                else:
                    is_available_data.update({"all_available": False})

        return is_available_data

    def allGetAvailableHouse(self):
        available_list = []
        with open('new_bolig.json', 'r') as f:
            data = json.load(f)

        for adress in data:
            if self.getAvailableHouse(adress)['all_available']:
                available_list.append(self.getAvailableHouse(adress))

        return available_list


sit = SitBuildings(not_available=True, city='*')

sit.rooms_unit_all()

print(sit.allGetAvailableHouse())
print(len(sit.all_resideses()))

