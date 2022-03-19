import os

index_file = "resources\\IconResources.idx"
os.makedirs("extracted", exist_ok = True)

def bytes_to_int(bytes):
    return int.from_bytes(bytes, "little")

def read_int(f):
    return bytes_to_int(f.read(4))

def read_qword(f):
    return bytes_to_int(f.read(8))

def read_value_set(f, amt):
    return [read_int(f) for _ in range(amt)]

def read_photoshop_string(f):
    string = b""
    c = f.read(1)
    while c != b"\x0A":
        string += c
        c = f.read(1)
    return string.decode().strip().strip("\x00")

def read_fixed_string(f, size = 0x30):
    return f.read(size).decode().strip().strip("\x00")

class PhotoshopIndexAsset:
    def __init__(self, f, files):
        self.files = files

        self.asset_name = read_fixed_string(f)
        
        self.width = PhotoshopDimensionType(f, files)
        self.height = PhotoshopDimensionType(f, files)
        self.width_resize = PhotoshopDimensionType(f, files)
        self.height_resize = PhotoshopDimensionType(f, files)

        self.offset = PhotoshopMetaType(f, files)
        self.size = PhotoshopMetaType(f, files)

    def __str__(self):
        string = f"{self.asset_name}:\n"
        for idx, file in enumerate(self.files):
            string += f"\t{file}:\n"
            string += f"\t\tDimensions: {self.width.data[idx]}x{self.height.data[idx]}\n"
            string += f"\t\tResize: {self.width_resize.data[idx]}x{self.height_resize.data[idx]}\n"
            string += f"\t\tOffsets: {self.offset.data[idx]}\n"
            string += f"\t\tSizes: {self.size.data[idx]}\n"
        return string
class PhotoshopDimensionType:
    def __init__(self, f, files):
        self.data = [read_int(f) for _ in range(len(files))]
class PhotoshopMetaType:
    def __init__(self, f, files):
        self.data = [read_value_set(f, 8) for _ in range(len(files))]
class PhotoshopDataType:
    def __init__(self, f, size):
        self.data = f.read(size)

def get_resource_handle(name):
    return open(f"resources\\{name}", "rb")

with open(index_file, "rb") as f:

    f.seek(0, 2)
    size = f.tell()
    f.seek(0, 0)

    version_string = read_photoshop_string(f)
    files_count = 4 # Hardcoded
    files = [read_photoshop_string(f) for _ in range(files_count)]


    print("Version:", version_string)
    print("Files:")
    for file in files:
        print(f"\t{file}")

    handles = [get_resource_handle(file) for file in files]

    while f.tell() < size:
        asset = PhotoshopIndexAsset(f, files)
        print(asset)