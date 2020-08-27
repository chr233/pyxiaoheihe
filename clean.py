import os


def clear(filepath):
    files = os.listdir(filepath)
    for fd in files:
        cur_path = os.path.join(filepath, fd)
        if os.path.isdir(cur_path):
            if fd == "__pycache__":
                for f in os.listdir(cur_path):
                    os.remove(os.path.join(cur_path, f))
                os.removedirs(cur_path)
                print(f'删除 {cur_path}')
            else:
                clear(cur_path)


if __name__ == "__main__":
    clear("./")
