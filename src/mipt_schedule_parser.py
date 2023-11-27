from bs4 import BeautifulSoup
import xlrd
import requests
import os


class MIPTSchedule:
    course = 0
    group = 0
    path_to_schedule = "src/"
    optional_subjects = dict()  # unit of measurement -- half of a pair

    def __init__(self, course, group):
        self.course = course
        self.group = group

    def download_schedule(self):
        url = "https://mipt.ru/about/departments/uchebniy/schedule/study/"
        mipt_html = requests.get(url)
        soup = BeautifulSoup(mipt_html.text, "lxml")

        for link in soup.find_all('a'):
            if link.find(text=f"{self.course} курс бакалавриата, специалитета"):
                mipt_link = "https://mipt.ru" + link["href"]
                schedule = requests.get(mipt_link)

                with open(f"{self.path_to_schedule}schedule_for_course_{self.course}.xls", "wb") as file:
                    file.write(schedule.content)

    def delete_schedule(self):
        os.remove(f"{self.path_to_schedule}schedule_for_course_{self.course}.xls")

    def find_first_subject(self, day):
        wb = xlrd.open_workbook(f"{self.path_to_schedule}schedule_for_course_{self.course}.xls",
                                formatting_info=True)
        sheet = wb.sheet_by_index(0)
        num_of_group_col = -1
        for col, cell in enumerate(sheet.row(4)):
            if cell.value == self.group:
                num_of_group_col = col
        if num_of_group_col == -1:
            raise ValueError("Can't find group")

        green = (204, 255, 204)  # background

        current_day = 1
        should_skip = 0
        for row_index in range(5, sheet.nrows):
            if should_skip > 0:
                should_skip -= 1
                continue

            color = wb.colour_map[
                wb.xf_list[sheet.cell(row_index, num_of_group_col).xf_index].background.pattern_colour_index]
            current_subject = sheet.cell(row_index, num_of_group_col).value

            if color is None:
                current_day += 1
                continue

            if current_day == day:
                if current_subject in self.optional_subjects:
                    should_skip = self.optional_subjects[current_subject] - 1
                    continue

                if current_subject:
                    return sheet.cell(row_index, 1).value, current_subject

                elif color != green:
                    position = num_of_group_col - 1  # will not cause error

                    while position > 0:
                        another_subject = sheet.cell(row_index, position).value

                        # don't use "color == another_color" because colors are sometimes read incorrectly
                        if another_subject:
                            return sheet.cell(row_index, 1).value, another_subject

                        position -= 1
        return -1
