import tkinter as tk
from collections import defaultdict
from tkinter import filedialog
import regex as re


class FileLoader:
    @staticmethod
    def prompt_get_file_path() -> str:
        root = tk.Tk()
        root.withdraw()
        return filedialog.askopenfilename()

    @staticmethod
    def read_lines_at_path(file_path, encodings_list, string_post_process):
        for encoding in encodings_list:
            try:
                with open(file_path, encoding=encoding) as file:
                    return tuple(string_post_process(line) for line in file.readlines())
            except UnicodeDecodeError:
                continue
        else:
            raise Exception("didn't find a matching encoding")

    @staticmethod
    def line_post_process(line: str):
        return line.strip()

    @staticmethod
    def choose_file_read_lines(encodings_list):
        file_path = FileLoader.prompt_get_file_path()
        if file_path == "":
            return None
        return FileLoader.read_lines_at_path(file_path, encodings_list, FileLoader.line_post_process)


class RepeatsMarker:

    @staticmethod
    def ignore_line(line):
        if re.match(r'^[_\W]*$', line) is None:
            return False
        else:
            return True

    @staticmethod
    def should_start_new_block(last_line_indices, new_line_indices, invalid_lines_dict):
        if not len(last_line_indices) == len(new_line_indices):
            return True
        else:
            for i in range(len(last_line_indices)):
                if not new_line_indices[i] == last_line_indices[i] + 1 and (
                        last_line_indices[i] + 1 not in invalid_lines_dict or
                        not invalid_lines_dict[last_line_indices[i] + 1] + 1 == new_line_indices[i]):
                    return True
            else:
                return False

    @staticmethod
    def find_repeated_lines_with_indices(lines_iterable, ignore_lines_with_less_than_characters=3,
                                         ignore_lines_appeared_less_than_times=2):
        duplicate_lines_dict = defaultdict(list)
        invalid_lines_range_dict = {}
        current_key = -1
        for i, item in enumerate(lines_iterable):
            if not RepeatsMarker.ignore_line(item):
                duplicate_lines_dict[item].append(i)
            else:
                if current_key == -1 or not i == invalid_lines_range_dict[current_key] + 1:
                    current_key = i
                invalid_lines_range_dict[current_key] = i
        return ((key, indices) for key, indices in duplicate_lines_dict.items() if
                len(indices) >= ignore_lines_appeared_less_than_times and len(
                    key) >= ignore_lines_with_less_than_characters), invalid_lines_range_dict

    @staticmethod
    def locate_repeated_blocks(repeated_lines_with_indices_iterable, invalid_lines_dict,
                               ignore_blocks_with_less_than_lines=3):
        temp_list = []
        last_line_indices = []
        for line_with_indices in repeated_lines_with_indices_iterable:
            if RepeatsMarker.should_start_new_block(last_line_indices, line_with_indices[1], invalid_lines_dict):
                temp_list.append([[index, index] for index in line_with_indices[1]])

            else:
                for i, item in enumerate(line_with_indices[1]):
                    temp_list[len(temp_list) - 1][i][1] = item

            last_line_indices = line_with_indices[1]

        # filter blocks with too few lines
        return (_range for _range in temp_list if _range[0][1] - _range[0][0] >= ignore_blocks_with_less_than_lines - 1)

    @staticmethod
    def generate_readable_dict(repeated_blocks_iterable, file_lines_list: list or tuple, show_first_last_lines_count=3,
                               index_increment=1) -> dict:
        result_dict = {}
        for blocks_range_list in repeated_blocks_iterable:
            key = "\n"
            if blocks_range_list[0][1] - blocks_range_list[0][0] > show_first_last_lines_count * 2:
                for i in range(show_first_last_lines_count):
                    key += str(file_lines_list[blocks_range_list[0][0] + i]).strip("\n") + "\n"

                key += "\n......\n\n"

                for i in range(-show_first_last_lines_count + 1, 1):
                    key += str(file_lines_list[blocks_range_list[0][1] + i]).strip("\n") + "\n"

            else:
                for i in range(blocks_range_list[0][0], blocks_range_list[0][1] + 1):
                    key += file_lines_list[i].strip("\n") + "\n"
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
    def find_repeats(file_lines, ignore_lines_with_less_than_characters=3, ignore_lines_appeared_less_than_times=2,
                     ignore_blocks_with_less_than_lines=3):
        repeated_lines, invalid_lines = RepeatsMarker.find_repeated_lines_with_indices(file_lines,
                                                                                       ignore_lines_with_less_than_characters,
                                                                                       ignore_lines_appeared_less_than_times)
        return RepeatsMarker.locate_repeated_blocks(repeated_lines, invalid_lines, ignore_blocks_with_less_than_lines)


def usage_example():
    encoding_try_list = ["utf-8", "gb18030"]
    file_lines = FileLoader().choose_file_read_lines(encoding_try_list)
    if file_lines is None:
        return

    repeated_blocks = RepeatsMarker.find_repeats(file_lines)
    readable_dict = RepeatsMarker.generate_readable_dict(repeated_blocks, file_lines)
    readable_string = RepeatsMarker.generate_readable_string(readable_dict)
    print(readable_string)


if __name__ == "__main__":
    usage_example()
