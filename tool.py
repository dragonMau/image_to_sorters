from shutil import rmtree
import zlib
from os import mkdir, path
from sys import argv

from PIL import Image, ImagePalette

split_x, split_y = 32, 32
total_x, total_y = 32, 32
converted: Image = Image.new("RGB", (0, 0), color=(0, 0, 0))

colors = {
    (217, 157, 115):  ([0, 0], 5),
    (140, 127, 169):  ([0, 1], 5),
    (235, 238, 245):  ([0, 2], 5),
    (178, 198, 210):  ([0, 3], 5),
    (247, 203,  164): ([0, 4], 5),
    (39, 39, 39):     ([0, 5], 5),
    (141, 161, 227):  ([0, 6], 5),
    (249, 163, 199):  ([0, 7], 5),
    (119, 119, 119):  ([0, 8], 5),
    (83, 86, 92):     ([0, 9], 5),
    (203, 217, 127):  ([0, 10], 5),
    (244, 186, 110):  ([0, 11], 5),
    (243, 233, 121):  ([0, 12], 5),
    (116, 87, 206):   ([0, 13], 5),
    (255, 121, 94):   ([0, 14], 5),
    (255, 170, 95):   ([0, 15], 5),
    (255, 211, 127):  (None, 0)
}

palette_img = Image.new("P", (17, 1))
for i, p in enumerate(colors.keys()):
    palette_img.putpixel((i, 0), p)

class Point:
    x: int
    y: int
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    @classmethod
    def unpack(cls, p: int) -> object:
        return cls(p >> 16, p & 0xFFFF)
    @staticmethod
    def x(p: int) -> int:
        return p >> 16
    @staticmethod
    def y(p: int) -> int:
        return p & 0xFFFF
    
def read_chr(array: list) -> str:
    return bytes([array.pop(0)]).decode("UTF-8")

def read_num(array: list, blen: int) -> int:
    """
    bytes arguments:
        1: read_byte
        2: read_short
        4: read_int
        8: read_long
    """
    return int.from_bytes(bytes([array.pop(0) for _ in range(blen)]), "big")

def write_num(num: int, blen: int) -> list:
    """
    bytes arguments:
        1: write_byte
        2: write_short
        4: write_int
        8: write_long
    """
    return list(num.to_bytes(blen, "big"))


def read_float(array: list, bytes: int):
    """
    bytes arguments:
        4: float
        8: double
    """
    return float.from_bytes(bytes([array.pop(0) for _ in range(bytes)]), "big")

def read_utf(array: list) -> str:
    utflen = read_num(array, 2)
    chars = ""
    for _ in range(utflen):
        chars += read_chr(array)
    print(chars)
    return chars

def write_utf(chars: str) -> list:
    array = write_num(len(chars), 2)
    for chr in chars:
        array.append(list(chr.encode("UTF-8"))[0])
    return array

def parse_list(raw: str) -> list:
    raw = list(raw)
    if raw.pop(0) == "[" and raw.pop() == "]":
        return [element.strip() for element in "".join(raw).split(",")]
    else:
        return []
    
def get_block(name: str) -> str:
    return name

def map_config(block: str, value: int, position: int) -> object:
    return {"block": block, "value": value, "position": position}

def read_string(array: list) -> str:
    exists = read_num(array, 1)
    if exists:
        return read_utf(array)
    else:
        return None
    
def read_object(array: list) -> object:
    match read_num(array, 1):
        case  0: return None, 0
        case  1: return read_num(array, 4), 1
        case  2: return read_num(array, 8), 2
        case  3: return read_float(array, 4), 3
        case  4: return read_string(array), 4
        case  5: return [read_num(array, 1), read_num(array, 2)], 5
        case  6: return [read_num(array, 4) for _ in range(read_num(array, 2))], 6
        case  7: return Point(read_num(array, 4), read_num(array, 4)), 7
        case  8: return [Point.unpack(read_num(array, 4)) for _ in range(read_num(array, 1))], 8
        case  9: return [[read_num(array, 1), read_num(array, 2)]], 9
        case 10: return bool(read_num(array, 1)), 10
        case 11: return read_float(array, 8), 11
        case 12: return [read_num(array, 4)], 12
        case 13: return [read_num(array, 2)], 13
        case 14: return [read_num(array, 1) for _ in range(read_num(array, 4))], 14
        case 15: return [read_num(array, 1)], 15
        case 16: return [bool(read_num(array, 1)) for _ in range(read_num(array, 4))], 16
        case type: raise Exception(f"Unknown object type: {type}")
        


def read(schematic_name):
    with open(f"./{schematic_name}.msch", "rb") as f:
        header = "".join([f.read(1).decode("UTF-8") for _ in range(4)])
        version = list(f.read(1))[0]
        array = list(zlib.decompress(f.read()))
        width = read_num(array, 2)
        height = read_num(array, 2)
        tags = read_num(array, 1)
        tags_map = {}
        for _ in range(tags):
            tag, value = read_utf(array), read_utf(array)
            tags_map[tag] = value
        tags_map["labels"] = parse_list(tags_map["labels"])
        
        blocks = []
        length = read_num(array, 1)
        for _ in range(length):
            blocks.append(read_utf(array))
        
        
        tiles = []
        total = read_num(array, 4)
        # input(f"{total = }")
        for _ in range(total):
            #         new_list += write_num(0, 1)
            #         new_list += write_num(x, 2) + write_num(y, 2)
            #         config = colors[img_y.getpixel((x, y))]
            #         new_list += write_num(config[1], 1)
            #         if config[1] != 0:
            #             new_list += write_num(config[0][0], 1) + write_num(config[0][1], 2)
            #         write_num(0, 1)
            t = read_num(array, 1)
            # print(f"{t = }")
            block = blocks[t]
            position = read_num(array, 4)
            log = -1
            if version == 0:
                config = read_num(array, 4)
            else:
                config, log = read_object(array) # reads 1 byte as byte, if 5 reads 1 byte as byte and 2 bytes as short
            # input(f"{config, log = }")
            rotation = read_num(array, 1)
            tiles.append(" ".join((f"{block = }", f"position = {Point.x(position), Point.y(position)}", f"{config = }", f"{rotation = }")))
        # input(f"{tiles[-1] = }")
        
        
    print(f"{header = }\n{version = }\n{width = }\n{height = }")
    print(f"map = {tags_map}\ntiles: \n"+"\n".join(tiles))

def reform_photo(imageB: Image, width: int, height: int):
    global converted
    image = imageB.resize((width, height)).convert("RGB")
    t = image.quantize(
        palette=palette_img,
        method=Image.Quantize.FASTOCTREE,
        dither=Image.Dither.NONE)
    converted = t.convert("RGB")
        
    
def generate(schematic_name):
    errors = []
    width, height = total_x, total_y
    list_converted = []
    # print(f"{width, height = }")
    for x0 in range(0, width, split_x):
        list_converted.append([])
        for y0 in range(0, height, split_y):
            box = (x0, y0,
                    x0+split_x if x0+split_x <  width else  width,
                    y0+split_y if y0+split_y < height else height)
            # print(box)
            list_converted[-1].append(converted.transpose(Image.Transpose.FLIP_TOP_BOTTOM).crop(box).convert("RGB"))
    # print(list_converted)
    list_schemes = {}
    for ix, img_x in enumerate(list_converted):
        for iy, img_y in enumerate(img_x):
            width, height = img_y.size
            #print(f"{width, height = }")
            new_list  = write_num(width, 2) + write_num(height, 2) + write_num(3, 1)
            new_list += write_utf("name") + write_utf(schematic_name+f"_{ix}_{iy}")
            new_list += write_utf("description") + write_utf("")
            new_list += write_utf("labels") + write_utf("[art]")
            new_list += [1] + write_utf("sorter") + write_num(width * height, 4)
            # print(f"{img_y}")
            # img_y.show()
            for x in range(width):
                for y in range(height):
                    new_list += write_num(0, 1)
                    new_list += write_num(x, 2) + write_num(y, 2)
                    try:
                        config = colors[img_y.getpixel((x, y))]
                    except KeyError as e:
                        log_e = f"Key Error: {e} at {(x,y)}"
                        errors.append(log_e)
                        config = colors[(39, 39, 39)] # black (coal)
                    new_list += write_num(config[1], 1)
                    if config[1] != 0:
                        new_list += write_num(config[0][0], 1) + write_num(config[0][1], 2)
                    new_list += write_num(0, 1)
            list_schemes[f"{schematic_name}_{ix}_{iy}"] = new_list
    
    for name, s_bytes in list_schemes.items():
        with open(f"./out/{schematic_name}/{name}.msch", "wb") as f:
            f.write(b'msch\x01' + zlib.compress(bytes(s_bytes)))
    return "done", errors
            
    
if __name__ == "__main__":
    if len(argv) == 1:
        argv.append(input("choose mode(r/w): "))
    mode = argv[1]
    
    if mode in ("read", "r", "-r"):
        if len(argv) == 2:
            argv.append(input("choose schematic(<filename>.mshc): "))
        read(argv[2].removesuffix(".msch"))
        
        
    if mode in ("write", "w", "-w"):
        if "split" in argv:
            split_x, split_y = map(int, input(
                "change splitting from {split_x}x{split_y} pieces to(<int>x<int>): ").split("x"))
            argv.remove("split")
        if len(argv) == 2:
            argv.append(input("choose image(<filename>): "))
        if len(argv) == 3:
            argv.append(input("choose output width(<int>): "))
            argv.append(input("and height(<int>): "))
        if not path.isdir("./out"):
            mkdir("./out")
        if len(argv) == 5:
            argv.append(input("schematic file-name(<str>): "))
        if path.isdir("./out/"+argv[5]):
            if len(argv) == 6:
                argv.append(input("this already exists, overwrite?(yes/no): "))
            if argv[6] in ("yes", "y", "1", "overwrite"):
                rmtree("./out/"+argv[5])
        
        mkdir("./out/"+argv[5])
        x, y = int(argv[3]), int(argv[4])
        with Image.open(argv[2]) as image:
            total_x, total_y = image.width if x == 0 else x, image.height  if y == 0 else y
            reform_photo(image, total_x, total_y)
            print(generate(argv[5]))
    
    elif True: # put "True" to test methods
        from os import system, getcwd
        system(f"start python")
    