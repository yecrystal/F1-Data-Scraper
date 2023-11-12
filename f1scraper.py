import requests
from bs4 import BeautifulSoup
import time


def get_page(url):
    page = requests.get(url, headers={
        "User-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.328"
                      "2.186 Safari/537.36"})
    doc = BeautifulSoup(page.content, "html.parser")
    return doc


def get_information(doc):
    site_wrapper = doc.find(class_="site-wrapper")
    main = site_wrapper.find(class_="template template-resultsarchive")
    inner_class = main.find(class_="inner-wrap ResultArchiveWrapper")
    result_archive = inner_class.find(class_="ResultArchiveContainer")
    results_archive_wrapper = result_archive.find(class_="resultsarchive-wrapper")
    content = results_archive_wrapper.table
    tbody = content.tbody
    return tbody


def get_driver_name(tbody):
    current_season_drivers = []
    tds_for_names = tbody.find_all("a", class_="dark bold ArchiveLink")
    for tds_for_names in tds_for_names:
        names = tds_for_names.find_all(True, {"class": {"hide-for-tablet", "hide-for-mobile"}})
        name = names[0].text + " " + names[1].text
        current_season_drivers.append(name)
    return current_season_drivers


def get_driver_points(tbody):
    current_season_points = []
    tds_for_points = tbody.find_all("td", class_="dark bold")
    for tds_for_points in tds_for_points:
        point = tds_for_points.string
        current_season_points.append(point)
    return current_season_points


def get_team_name(tbody):
    current_season_teams = []
    tds_for_teams = tbody.find_all("a", class_="grey semi-bold uppercase ArchiveLink")
    for tds_for_teams in tds_for_teams:
        team = tds_for_teams.string
        current_season_teams.append(team)
    return current_season_teams


def save(path, year, names, points, team):
    lines = []
    for i in range(len(names)):
        each_line = (str(i + 1) + "-" + names[i] + " " * (25 - len(names[i])) + points[i] + " " * (10 - len(points[i]))
                     + team[i])
        lines.append(each_line)
    with open(path, "a", encoding="utf-8") as file:
        text = "-"*20 + str(year) + " Driver Standings" + "-"*60 + "\n"
        file.write(text)
        for line in lines:
            file.write(line)
            file.write("\n")
    file.close()


def save_as_sql(path, year, names, point, teams):
    lines = [str(year)]
    for i in range(len(names)):
        each_line = names[i] + "," + point[i] + "," + teams[i]
        lines.append(each_line)
    with open(path, "a", encoding="utf-8") as file:
        for line in lines:
            file.write(line)
            file.write("\n")
    file.close()


def get_user_input():
    year = []
    ipt = input("Please enter the year that you would like to view (If multiple, please separate with a comma):")
    ipt = ipt.split(",")
    if len(ipt) > 1:
        while int(ipt[0]) < 1950 or int(ipt[1]) > 2023:
            ipt = input(
                "No such year. Dates should be given between 1950 and 2023.\n")
            ipt = ipt.split(",")
        for y in range(int(ipt[0]), int(ipt[1])+1):
            year.append(y)
    else:
        while int(ipt[0]) < 1950 or int(ipt[0]) > 2023:
            ipt = input(
                "No such year. Dates should be given between 1950 and 2023.\n")
            ipt = ipt.split(",")
        year.append(int(ipt[0]))
    return year


dict_person = {}
dict_team = {}


def update_dict(name, team, point, flag):
    global dict_person, dict_team
    if flag == 0:
        for i in range(len(name)):
            driver = name[i]
            if driver in dict_person:
                dict_person[driver] += float(point[i])
            else:
                dict_person[driver] = float(point[i])
    else:
        for i in range(len(team)):
            key = team[i]
            if key in dict_team:
                dict_team[key] += float(point[i])
            else:
                dict_team[key] = float(point[i])


def save_dictionary(path, dictionary, flag):
    if flag == 1:
        sorted_dict = sorted(dictionary.items(), key=lambda x: x[0], reverse=False)
    else:
        sorted_dict = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)
    with open(path, "a", encoding="utf-8") as output:
        txt = "-"*24 + " Total points collected by drivers/teams during this period" + "-"*30 + "\n"
        output.write(txt)
        for row in sorted_dict:
            output.write(str(row[0]) + " " * (25-len(row[0])) + str(row[1]) + "\n")


def main():
    global dict_team, dict_person
    open("F1_data.txt", "w").close()
    year = get_user_input()
    len_year = len(year)
    for y in year:
        print("Scraping year", y)
        url = "https://www.formula1.com/en/results.html/" + \
            str(y)+"/drivers.html"
        doc = get_page(url)
        tbody = get_information(doc)
        name = get_driver_name(tbody)
        point = get_driver_points(tbody)
        team = get_team_name(tbody)
        save("F1_data.txt", y, name, point, team)
        update_dict(None, team, point, 1)
        if len_year > 1:
            update_dict(name, None, point, 0)
        time.sleep(1)
    if len_year > 1:
        save_dictionary("F1_data.txt", dict_person, 0)
    save_dictionary("F1_data.txt", dict_team, 1)
    print("Process Finished Successfully")


main()
