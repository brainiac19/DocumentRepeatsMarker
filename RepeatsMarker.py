import tkinter as tk
from collections import defaultdict
from tkinter import filedialog


class FileLoader:
    def __init__(self):
        self.encoding_try_list = ["utf-8", "utf-16", "gbk", "big5"]

    @staticmethod
    def prompt_get_file_path() -> str:
        root = tk.Tk()
        root.withdraw()
        return filedialog.askopenfilename()

    def read_lines_at_path(self, file_path) -> list:
        for encoding in self.encoding_try_list:
            try:
                with open(file_path, encoding=encoding) as file:
                    return file.readlines()
            except UnicodeDecodeError:
                continue
        else:
            raise Exception("didn't find a matched encoding")

    def choose_file_read_lines(self):
        file_path = self.prompt_get_file_path()
        if file_path == "":
            return None
        return self.read_lines_at_path(file_path)


class RepeatsMarker:

    @staticmethod
    def calculate_diffs(l):
        if len(l) < 2:
            raise Exception("list needs to be longer than 2 to calculate diff")
        temp_list = []
        for i in range(1, len(l)):
            temp_list.append((l[i] - l[i - 1]))
        return temp_list

    @staticmethod
    def find_repeated_lines_with_indices(lines_iterable, ignore_lines_with_less_than_characters = 3, ignore_blank_lines = True):
        duplicates_dict = defaultdict(list)
        for i, item in enumerate(lines_iterable):
            duplicates_dict[item].append(i)
        return ((key, indices) for key, indices in duplicates_dict.items() if len(indices) > 1 and len(key) >= ignore_lines_with_less_than_characters and (not ignore_blank_lines or not str(key).isspace()))

    @staticmethod
    def locate_repeated_blocks(repeats_with_indices_iterable, ignore_blocks_with_less_than_lines = 3) -> list:
        temp_list = []
        line_index_temp = -2
        diffs_temp = []
        for line_with_indices in repeats_with_indices_iterable:
            diffs = RepeatsMarker.calculate_diffs(line_with_indices[1])
            if not diffs == diffs_temp or not line_with_indices[1][0] == line_index_temp + 1:
                diffs_temp = diffs
                temp_list.append([[index, index] for index in line_with_indices[1]])

            line_index_temp = line_with_indices[1][0]
            for i, item in enumerate(line_with_indices[1]):
                temp_list[len(temp_list) - 1][i][1] = item

        #filter blocks with too few lines
        range_list = []
        for _range in temp_list:
            if RepeatsMarker.calculate_diffs(_range[0])[0] >= ignore_blocks_with_less_than_lines - 1:
                range_list.append(_range)

        return range_list

    @staticmethod
    def generate_readable_dict(repeated_blocks_list:list, file_lines_list:list, show_first_last_lines_count = 3, index_increment = 1) -> dict:
        result_dict = {}
        for blocks_range_list in repeated_blocks_list:
            key = "\n"
            if blocks_range_list[0][1] - blocks_range_list[0][0] > show_first_last_lines_count * 2:
                for i in range(show_first_last_lines_count):
                    key += str(file_lines_list[blocks_range_list[0][0] + i]).strip("\n") + "\n"

                key += "\n......\n\n"

                for i in range(-show_first_last_lines_count , 0):
                    key += str(file_lines_list[blocks_range_list[0][1] + i]).strip("\n") + "\n"

            else:
                for i in range(blocks_range_list[0][0], blocks_range_list[0][1] + 1):
                    key += file_lines_list[i]
            key += "\n\n\n"
            result_dict[key] = list([[index + index_increment for index in _range] for _range in blocks_range_list])
        return result_dict

    @staticmethod
    def generate_readable_string(index_range_dict: dict) -> str:
        readable_string = ""
        for key in index_range_dict.keys().__reversed__():
            readable_string += str(index_range_dict[key])
            readable_string += str(key)
        return readable_string

    @staticmethod
    def find_repeats(file_lines:list):
        repeated_lines_with_range = RepeatsMarker.find_repeated_lines_with_indices(file_lines)
        return RepeatsMarker.locate_repeated_blocks(repeated_lines_with_range)


def usage_example():
    file_lines = FileLoader().choose_file_read_lines()
    if file_lines is None:
        return

    repeated_blocks = RepeatsMarker.find_repeats(file_lines)
    readable_dict = RepeatsMarker.generate_readable_dict(repeated_blocks, file_lines)
    readable_string = RepeatsMarker.generate_readable_string(readable_dict)

    with open("check results.txt", "w") as writer:
        writer.write("no repeats found" if readable_string == "" else readable_string)


if __name__ == "__main__":
    usage_example()

