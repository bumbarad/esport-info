from urllib.request import quote
from pathlib import Path
from bs4 import BeautifulSoup
import requests


class Liquipedia:
    """Class for handling Liquipedia API using liquipediapy interface.
    Important: There is a rate limit to a 1 request per 2 seconds! However it seems not to be working."""
    def __init__(self):
        self.team_file = str(Path(__file__).parent) + "\\static\\teams.txt"
        self.team_names = self.__get_teams()
        self.teams = {}

    @staticmethod
    def __query(page: str):
        url = 'https://liquipedia.net/counterstrike/api.php?action=parse&format=json&page=' + page
        response = requests.get(url, headers={'User-Agent': 'esport-info_school_project', 'Accept-Encoding': 'gzip'})
        if response.status_code == 200:
            try:
                page_html = response.json()['parse']['text']['*']
            except KeyError:
                raise requests.exceptions.RequestException(response.json(), response.status_code)
            return BeautifulSoup(page_html, features="lxml")
        else:
            raise requests.exceptions.RequestException(response.json(), response.status_code)

    def __save_teams(self):
        """Due to limit rate, the list of teams was made and stored in a file before launching the application"""
        soup = self.__query("Portal:Teams")
        file = open(self.team_file, "w", encoding="utf-8")
        for line in soup.find_all('span', class_="team-template-team-standard"):
            file.write(line['data-highlightingclass'] + "\n")

    def __append_team(self, team_name: str):
        soup = self.__query(team_name)

        team_dict = {'name': team_name}

        info = soup.p
        for sup in info.find_all('sup'):
            sup.decompose()
        for link in info.find_all('a'):
            link.replace_with(link.text)
        team_dict['info'] = info

        income = soup.find_all('div')
        for i in range(len(income)):
            if "Total Winnings:" in income[i].text:
                team_dict['income'] = income[i + 1].text

        players = soup.find_all('table')
        for table in players:
            if "Active Squad" in table.text:
                players = table
                break
        for sup in players.find_all('sup'):
            sup.decompose()
        for img in players.find_all('img'):
            img.decompose()
        for link in players.find_all('a'):
            link.replace_with(link['title'])
        team_dict['players'] = players

        self.teams[team_name] = team_dict

    def get_team_info(self, team_name: str):
        team_name = team_name.replace(" ", "_")
        team_name = quote(team_name)

        if team_name not in self.teams.keys():
            self.__append_team(team_name)

        return self.teams[team_name]

    def __get_teams(self) -> list:
        teams = []
        file = open(self.team_file, "r")
        for line in file:
            teams.append(line.strip("\n"))
        return teams
