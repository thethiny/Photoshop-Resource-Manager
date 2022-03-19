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
    def __init__(self, f):
        self.asset_name = read_fixed_string(f)
        
        self.width_raster = PhotoshopDimensionType(f)
        self.height_raster = PhotoshopDimensionType(f)
        self.width_svg = PhotoshopDimensionType(f)
        self.height_svg = PhotoshopDimensionType(f)

        self.offset = PhotoshopMetaType(f)
        self.size = PhotoshopMetaType(f)

    def __str__(self):
        return f"{self.asset_name}:\n" \
        f"\tRaster Low: {self.width_raster.low_res}x{self.height_raster.low_res}\n" \
        f"\tRaster High: {self.width_raster.high_res}x{self.height_raster.high_res}\n" \
        f"\tSVG Low: {self.width_svg.low_res}x{self.height_svg.low_res}\n" \
        f"\tSVG High: {self.width_svg.high_res}x{self.height_svg.high_res}\n" \
        f"\tRaster Offsets: {self.offset.low_res} | {self.offset.high_res}\n" \
        f"\tSVG Offsets: {self.offset.low_res_svg} | {self.offset.high_res_svg}\n" \
        f"\tRaster Sizes: {self.size.low_res} | {self.size.high_res}\n" \
        f"\tSVG Sizes: {self.size.low_res_svg} | {self.size.high_res_svg}\n"


class PhotoshopDimensionType:
    def __init__(self, f):
        self.low_res = read_int(f)
        self.high_res = read_int(f)
        self.unk_1 = read_int(f)
        self.unk_2 = read_int(f)

class PhotoshopMetaType:
    def __init__(self, f):
        self.low_res = read_value_set(f, 8)
        self.high_res = read_value_set(f, 8)
        self.low_res_svg = read_value_set(f, 8)
        self.high_res_svg = read_value_set(f, 8)

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
    low_res_name = read_photoshop_string(f)
    high_res_name = read_photoshop_string(f)
    low_res_svg_name = read_photoshop_string(f)
    high_res_svg_name = read_photoshop_string(f)

    print("Version:", version_string)
    print("Low res name:", low_res_name)
    print("High res name:", high_res_name)
    print("Low res svg name:", low_res_svg_name)
    print("High res svg name:", high_res_svg_name)

    low_res_file = get_resource_handle(low_res_name)
    high_res_file = get_resource_handle(high_res_name)
    low_res_svg_file = get_resource_handle(low_res_svg_name)
    high_res_svg_file = get_resource_handle(high_res_svg_name)

    while f.tell() < size:
        asset = PhotoshopIndexAsset(f)
        print(asset)
        # asset_name = read_fixed_string(f)
        # print("Asset name:", asset_name)

        # low_res_width = read_int(f)
        # high_res_width = read_int(f)
        # unk_1 = read_int(f)
        # unk_2 = read_int(f)

        # low_res_height = read_int(f)
        # high_res_height = read_int(f)
        # unk_3 = read_int(f)
        # unk_4 = read_int(f)

        # low_res_svg_width = read_int(f)
        # high_res_svg_width = read_int(f)
        # unk_5 = read_int(f)
        # unk_6 = read_int(f)

        # low_res_svg_height = read_int(f)
        # high_res_svg_height = read_int(f)
        # unk_7 = read_int(f)
        # unk_8 = read_int(f)
        
        # low_res_offsets = read_4_values(f, 8)
        # high_res_offsets = read_4_values(f, 8)
        # low_res_svg_offsets = read_4_values(f, 8)
        # high_res_svg_offsets = read_4_values(f, 8)

        # low_res_size = read_4_values(f, 8)
        # high_res_size = read_4_values(f, 8)
        # low_res_svg_size = read_4_values(f, 8)
        # high_res_svg_size = read_4_values(f, 8)