
from file_tools import (
    create_directory,
    write_file,
    read_file,
    list_files,
)

print("1. CREATE DIRECTORY")
print(create_directory("portfolio"))

print("\n2. WRITE FILE")
print(write_file(
    "portfolio/index.html",
    "<!doctype html><html><body><h1>My Portfolio</h1></body></html>"
))

print("\n3. READ FILE")
print(read_file("portfolio/index.html"))

print("\n4. LIST FILES")
print(list_files("portfolio"))

print("\n5. SECURITY TEST")
print(create_directory("../../outside"))


