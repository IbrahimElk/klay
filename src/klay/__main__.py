import argparse
import os

def include_dir() -> str:
    "Return the path to the klay include directory"
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "include")

def cmake_dir() -> str:
    "Return the path to the klay CMake module directory."
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "cmake")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmake_dir", action="store_true")
    parser.add_argument("--include_dir", action="store_true")
    args = parser.parse_args()

    if args.cmake_dir:
        print(cmake_dir())

    if args.include_dir:
        print(include_dir())

if __name__ == "__main__":
    main()
