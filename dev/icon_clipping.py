from PIL import Image
import os


for file in os.listdir(os.getcwd()):
    if not file.endswith(".jpg"):
        continue
    image = Image.open(file)
    if not image.size == (52, 52):
        print("Image {} has size {}".format(file, image.size))
        continue
    print("Considering image {}".format(file))
    if not (250, 250, 250) <= image.getpixel((51, 51)) <= (255, 255, 255):
        print("Skipping image {} because of pixel {}".format(file, image.getpixel((51, 51))))
        continue
    image = image.crop((0, 0, 50, 50))
    image.save(file)

