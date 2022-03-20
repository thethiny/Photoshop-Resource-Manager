import os

index_file = "resources\\IconResources.idx"
os.makedirs("extracted", exist_ok=True)


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


def read_fixed_string(f, size=0x30):
    return f.read(size).decode().strip().strip("\x00")


class PhotoshopIndexAsset:
    def __init__(self, f, files, handles):
        self.files = files
        self.handles = handles

        self.asset_name = read_fixed_string(f)

        self.width = PhotoshopDimensionType(f, files)
        self.height = PhotoshopDimensionType(f, files)
        self.width_resize = PhotoshopDimensionType(f, files)
        self.height_resize = PhotoshopDimensionType(f, files)

        self.offset = PhotoshopMetaType(f, files)
        self.size = PhotoshopMetaType(f, files)

        self.data = PhotoshopDataType(self.size, self.offset, self.handles)

        self.write()

    def write(self, keep = True):
        for i in range(len(self.files)):
            path = os.path.join("extracted", self.files[i].rsplit(".")[0])
            os.makedirs(path, exist_ok=True)
            for j in range(len(self.data.data[i])):
                data = self.data.data[i][j]
                if not data:
                    continue
                file_name = f"{self.asset_name}_{j}"
                if data[1:4] == b"PNG":
                    ext = ".png"
                elif data[:4] == b"<svg":
                    ext = ".svg"
                else:
                    ext = ".bin" # Unkown type
                full_path = os.path.join(path, file_name + ext)
                with open(full_path, "wb") as f:
                    f.write(data)
                    if not keep:
                        del self.data


    def __str__(self):
        string = f"{self.asset_name}:\n"
        for idx, file in enumerate(self.files):
            string += f"\t{file}:\n"
            string += (
                f"\t\tDimensions: {self.width.data[idx]}x{self.height.data[idx]}\n"
            )
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
    def __init__(self, sizes, offsets, handles):
        self.data = []
        for idx, handle in enumerate(handles): # incorrect, size and offset are lists of lists
            cur_data = []
            for i in range(len(sizes.data[idx])):
                offset = offsets.data[idx][i]
                size = sizes.data[idx][i]
                handle.seek(offset, 0)
                cur_data.append(handle.read(size))
            self.data.append(cur_data)



def get_resource_handle(name):
    return open(f"resources\\{name}", "rb")


with open(index_file, "rb") as f:

    f.seek(0, 2)
    size = f.tell()
    f.seek(0, 0)

    version_string = read_photoshop_string(f)
    files_count = 4  # Hardcoded
    files = [read_photoshop_string(f) for _ in range(files_count)]

    print("Version:", version_string)
    print("Files:")
    for file in files:
        print(f"\t{file}")

    handles = [get_resource_handle(file) for file in files]

    while f.tell() < size:
        asset = PhotoshopIndexAsset(f, files, handles)
        print(asset)
