from PIL import Image, ImageDraw, ImageColor
from random import uniform, randint, choice
import os, argparse, json, requests
from hashlib import sha256

ps = 64
s = 0.96
used_palettes = []
randskin = ["#A68C69", "#6B4E4B", "#ffc79f", "#FBC4AC"]

matrix_test = ["0000000000000000",
               "0000000000000000",
               "0000000002211000",
               "00000000G2221100",
               "00000000G5556100",
               "00000000095961F0",
               "00000000055566F0",
               "0022100005AA6FF0",
               "0E59600067778000",
               "0E55A00000778000",
               "0077776000335000",
               "0057800000334000",
               "0087800000CBDBB0",
               "005B6BB0000BBBB0",
               "000BBBB000000000",
               "0000000000000000"]


def shade(color):
    c = ImageColor.getrgb(color) if type(color) is str else color
    d = (*[int(c[i]*s) for i in range(3)],)
    return c, d


def gradient(color, y):
    return (*[color[i] - y - 1 for i in range(3)],)


def main(args):
    num = args.N
    img = Image.new('RGB', (16*ps,16*ps))
    draw = ImageDraw.Draw(img)
    
    counter = 0
    rare_counter = 0
    alone_counter = [0,0]
    gender_counter_big = [0,0]
    gender_counter_bb = [0,0]
    

    if not os.path.isdir("output"):
        os.mkdir("output")

    if not os.path.isdir("metadata"):
        os.mkdir("metadata")

    while counter != args.N:

        base_properties = {"external_url": "https:/chaucha.art/abasho/",
	                        "image": "https://ipfs.io/ipfs/TEMP/%i.png",
	                        "name": "Abasho #%s",
	                        "description": "",
	                        "attributes": []
	                        }

        palette_request = requests.post("http://colormind.io/api/", data='{"model":"default"}').json()
        
        new_palette = []
        for color in palette_request["result"]:
            new_palette.append(''.join('{:02X}'.format(n) for n in color))
        
        darkest_color = False

        for color in new_palette:
            c_tuple = ImageColor.getrgb("#" + color)
            if sum(c_tuple) < 200:
                darkest_color = True

        if darkest_color:
            continue

        gender_bb = randint(0,1)
        gender_adulto = randint(0,1)
        skintone1_rng = randint(0, len(randskin)-1)
        skintone2_rng = randint(0, len(randskin)-1)

        rare_flag = True if randint(0, 10) > 9 or counter % 100 == 0 else False
        rare_flag = True

        alone_flag = True if randint(1, 100) >= 95 else False

        if rare_flag:
            skintone1 = "#" + new_palette[3]
            skintone2 = "#" + new_palette[3]
        else:
            skintone1 = randskin[skintone1_rng]
            skintone2 = randskin[skintone2_rng]

        if alone_flag:
            new_matrix = []
            for row in matrix_test:
                new_matrix.append("0" * 4 + row[7:] + "0"* 3)
            used_matrix = new_matrix
        else:
            used_matrix = matrix_test


        shirt, shirt_shade = shade("#" + new_palette[0])
        pants, pants_shade = shade("#" + new_palette[1])
        hair, hair_shade = shade("#" + new_palette[2])

        skin1, skin_shade1 = shade(skintone1)
        _, lips1 = shade(skin_shade1)
        _, lips1 = shade(lips1)

        skin2, skin_shade2 = shade(skintone2)
        _, lips2 = shade(skin_shade2)
        _, lips2 = shade(lips2)

        bg, bg_shadow = shade("#" + new_palette[3])
        _, bg_shadow = shade(bg_shadow)

        shoes, shoes_shade = shade("#333333")
        eyes = shoes

        for y in range(16):
            for x in range(16):
                if used_matrix[y][x] == "0":
                    if y < 11:
                        color = gradient(bg, x+y)
                    else:
                        color = gradient(bg_shadow, x+y)

                elif used_matrix[y][x] == "1":
                    color = hair_shade
                elif used_matrix[y][x] == "2":
                    color = hair
                elif used_matrix[y][x] == "3":
                    color = pants
                elif used_matrix[y][x] == "4":
                    color = pants_shade
                elif used_matrix[y][x] == "5":
                    color = skin2 if x >= 8 and not alone_flag else skin1
                elif used_matrix[y][x] == "6":
                    color = skin_shade2 if x >= 8 and not alone_flag else skin_shade1
                elif used_matrix[y][x] == "7":
                    color = shirt
                elif used_matrix[y][x] == "8":
                    color = shirt_shade
                elif used_matrix[y][x] == "9":
                    color = eyes
                elif used_matrix[y][x] == "A":
                    color = lips2 if x >= 8 and not alone_flag else lips1
                elif used_matrix[y][x] == "B":
                    color = gradient(bg_shadow, x+y+3)
                elif used_matrix[y][x] == "C":
                    color = shoes
                elif used_matrix[y][x] == "D":
                    color = shoes_shade

                elif used_matrix[y][x] == "E":
                    if gender_bb == 1:
                        color = hair
                    else:
                        color = gradient(bg, y)

                elif used_matrix[y][x] == "F":
                    if gender_adulto == 1:
                        color = hair_shade
                    else:
                        color = gradient(bg, x+y)

                elif used_matrix[y][x] == "G":
                    if gender_adulto == 1:
                        color = hair
                    else:
                        color = gradient(bg, x+y)

                draw.rectangle((x*ps, y*ps, x*ps + ps, y*ps + ps), color)

        filename = "output/%i.png" % counter
        img.save(filename)
        with open(filename,"rb") as f:
            readable_hash = sha256(f.read()).hexdigest();
            print(readable_hash)

        if rare_flag:
            rare_counter += 1

        if alone_flag:
            alone_counter[gender_adulto] += 1

        gender_counter_bb[gender_bb] += 1
        gender_counter_big[gender_adulto] += 1


        print(rare_flag, counter, gender_bb, gender_adulto, skintone1, skintone2)

        gender_adulto = "Madre" if gender_adulto == 1 else "Padre"
        gender_bb = "Hija" if gender_bb == 1 else "Hijo"
        compo = "%s e %s" % (gender_adulto, gender_bb) if not alone_flag else "%s" % gender_adulto

        race = "Aliens" if rare_flag else "Humanos"
        race = race[:-1] + " Solitario" if alone_flag else race

        base_properties["attributes"].append({"trait_type": "Family Type", "value": race})
        base_properties["attributes"].append({"trait_type": "Parent Gender", "value": gender_adulto})

        if not alone_flag:
            base_properties["attributes"].append({"trait_type": "Child Gender", "value": gender_bb})

        base_properties["image"] = base_properties["image"] % counter
        base_properties["name"] = base_properties["name"] % counter
        base_properties["description"] = "Abrazo Pixel-Art de %s (%s), generado aleatoriamente por el equipo de chaucha.art" % (compo, race)

        with open('metadata/%i' % counter, 'w') as f:
            json.dump(base_properties, f)

        counter += 1

    print("rare count total:", rare_counter)
    print("alone counter:", alone_counter)
    print("gender_counter_big:", gender_counter_big)
    print("gender_counter_bb:", gender_counter_bb)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("N", help="Number of generations", type=int)
    args = parser.parse_args()

    main(args)

