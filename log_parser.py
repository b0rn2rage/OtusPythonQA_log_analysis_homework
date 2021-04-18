import argparse
import os
import re
import json
from collections import Counter
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process access.log")
    parser.add_argument("-path", type=is_dir_or_file, action="store", help="Full path to logfile or dir")
    return parser.parse_args().path


def is_dir_or_file(path):
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")


def select_files(path):
    files = list()
    if os.path.isfile(path):
        return [path]
    if os.path.isdir(path):
        print("Список файлов в папке:", os.listdir(path))
        while True:
            x = input("Введите название файла, который нужно добавить к искомым. Для выхода введите 'end': ")
            if x == "end":
                break
            files.append(os.path.join(x))
        print("Список файлов, по которым будет происходить поиск:", files)
    return files


def collect_data(log_files: list):
    count_requests = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0}
    top_10_ip = Counter()
    exec_time = defaultdict(int)
    client_errors = defaultdict(int)
    server_errors = defaultdict(int)
    for file in log_files:
        print(list(log_files))
        with open(file) as f:
            for index, line in enumerate(f.readlines()):
                try:
                    ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line).group()
                    method = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD)", line).groups()[0]
                    execution_time = re.search(r"\d+$", line).group()
                    request_time = re.search(r'\d{1,2}/\w+/\d{4}:\d{2}:\d{2}:\d{2}', line).group()
                    url = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD) (\S+)", line).groups()[1]
                    code = re.search(r'(HTTP\/\d.\d") ([1-5]\d{2})', line).groups()[1]
                except AttributeError:
                    pass
                count_requests[method] += 1
                top_10_ip[ip] += 1
                key_for_exec_time = method + " " + ip + " " + url + " " + request_time
                key_for_errors = method + " " + code + " " + url + " " + ip

                exec_time[key_for_exec_time] = execution_time
                if code.startswith("4"):
                    client_errors[key_for_errors] += 1

                if code.startswith("5"):
                    server_errors[key_for_errors] += 1


        result = {"total_requests": count_requests,
                  "top_10_ip": top_10_ip.most_common(10),
                  "top_10_execution_time": dict(sorted(exec_time.items(), key=lambda x: x[1], reverse=True)[:10]),
                  "client_errors": dict(sorted(client_errors.items(), key=lambda x: x[1], reverse=True)[:10]),
                  "server_errors": dict(sorted(server_errors.items(), key=lambda x: x[1], reverse=True)[:10])
                  }

        return result


def write_to_file(data):
    with open("result.json", "w") as file:
        file.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    path_files = parse_arguments()
    selected_files = select_files(path_files)
    data_for_writing = collect_data(selected_files)
    write_to_file(data_for_writing)
