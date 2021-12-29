import io
import tkinter as tk
from tkinter import filedialog
import numpy as np

class RepeatsMarker:
    def __init__(self):
        self.ignore_lines_with_less_than_characters = 10
        self.show_first_last_lines_count = 3
        self.ignore_blocks_with_less_than_lines = 3
        self.encoding_try_list = ["utf-8", "utf-16", "gbk", "big5"]

    def get_file_path(self) -> str:
        root = tk.Tk()
        root.withdraw()
        return filedialog.askopenfilename()
    
    def read_text_lines(self, file_path: str) -> np.ndarray:
        for encoding in self.encoding_try_list:
            try:
                file = open(file_path, encoding=encoding)
                return np.array(file.readlines())
            except UnicodeDecodeError:
                continue
        else:
            raise Exception("didn't find a matched encoding")

    def calculate_diffs(self, l: list or tuple):
        if len(l) < 2:
            raise Exception("list needs to be longer than 2 to calculate diff")
        temp_list = []
        for i in range(1, len(l)):
            temp_list.append((l[i] - l[i - 1]))
        return temp_list

    def find_earliest_occurrence_key(self, dictionary: dict):
        return min(dictionary, key=lambda x: dictionary.get(x)[0])
    
    def find_repeated_lines_with_indices(self, lines_array:np.ndarray) -> dict:
        unique_lines = np.unique(lines_array)
        line_indices_dict = {}
        for line in unique_lines:
            if str(line).isspace() or len(line) < self.ignore_lines_with_less_than_characters:
                continue
            indices = np.where(lines_array == line)[0]
            if len(indices) > 1:
                line_indices_dict[line] = tuple(indices)
        return line_indices_dict
    
    def locate_repeated_blocks(self, repeat_indices_dict:dict) -> list:
        result_list = []
        while len(repeat_indices_dict) > 0:
            base_key = self.find_earliest_occurrence_key(repeat_indices_dict)
            base_value = repeat_indices_dict.pop(base_key)
            base_diff = self.calculate_diffs(base_value)
            delta_temp = 1

            while len(repeat_indices_dict) > 0:
                key = self.find_earliest_occurrence_key(repeat_indices_dict)
                if self.calculate_diffs(repeat_indices_dict[key]) == base_diff and repeat_indices_dict[key][0] == base_value[
                    0] + delta_temp:
                    repeat_indices_dict.pop(key)
                    delta_temp += 1
                else:
                    break

            if delta_temp >= self.ignore_blocks_with_less_than_lines:
                result_list.append([[index, index + delta_temp] for index in base_value])

        return result_list

    def generate_text_block_to_index_range_dict(self, result_list:list, file_lines_np_arr:np.ndarray) -> dict:
        result_dict = {}
        for ls in result_list:
            key = "\n"
            if ls[0][1] - ls[0][0] > 6:
                for i in range(self.show_first_last_lines_count):
                    key += str(file_lines_np_arr[ls[0][0] + i]).strip("\n")

                key += "\n......\n"
                for i in range(-self.show_first_last_lines_count + 1, 1):
                    key += str(file_lines_np_arr[ls[0][1] + i]).strip("\n")

            else:
                for i in range(ls[0][0], ls[0][1]):
                    key += file_lines_np_arr[i]
            key += "\n\n\n"
            result_dict[key] = ls
        return  result_dict

    def generate_readable_string(self, index_range_dict:dict) -> str:
        readable_string = ""
        for key in index_range_dict.keys().__reversed__():
            readable_string += str(index_range_dict[key])
            readable_string += str(key)
        return readable_string

    def main(self):
        file_path = self.get_file_path()
        if file_path == "":
            return
        file_lines_np_array = self.read_text_lines(file_path)

        line_indices_dict = self.find_repeated_lines_with_indices(file_lines_np_array)
        repeated_blocks = self.locate_repeated_blocks(line_indices_dict)
        text_to_index_range_dict = self.generate_text_block_to_index_range_dict(repeated_blocks, file_lines_np_array)
        readable_string = self.generate_readable_string(text_to_index_range_dict)

        writer = open("check results.txt", "w")
        writer.write(readable_string)

if __name__ == "__main__":
    rm = RepeatsMarker()
    #set custom parameters, or leave it default
    rm.main()

