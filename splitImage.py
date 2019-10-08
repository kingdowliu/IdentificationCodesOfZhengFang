from PIL import Image
from matplotlib import pyplot as plt
import os

def GrayscaleAndBinarization(image):
    '''
    灰度并二值化图片
    :param image:
    :return:
    '''
    threshold = 17  # 需要自己调节阈值

    tmp_image = image.convert('L')  # 灰度化
    new_image = Image.new('L', tmp_image.size, 0)

    # 初步二值化
    for i in range(tmp_image.size[1]):
        for j in range(tmp_image.size[0]):
            if tmp_image.getpixel((j, i)) > threshold:
                new_image.putpixel((j, i), 255)
            else:
                new_image.putpixel((j, i), 0)

    # new_image.show()    # 去噪前

    # 去噪，去除独立点，将前后左右等九宫格中灰度通道值均为255的像素点的通道值设为255
    for i in range(1, new_image.size[1] - 1):
        for j in range(1, new_image.size[0] - 1):
            if new_image.getpixel((j, i)) == 0 and new_image.getpixel((j - 1, i)) == 255 and new_image.getpixel((j + 1, i)) == 255 and \
                    new_image.getpixel((j, i - 1)) == 255 and new_image.getpixel((j - 1, i - 1)) == 255 and new_image.getpixel((j + 1, i - 1)) == 255 and\
                new_image.getpixel((j, i + 1)) == 255 and new_image.getpixel((j - 1, i + 1)) == 255 and new_image.getpixel((j + 1, i + 1)) == 255:
                new_image.putpixel((j, i), 255)
    # new_image.show()    # 去噪后

    return new_image

def SplitImage(image):
    '''
    切割图像并保存，关键在于寻找切割位置
    :param image:
    :return:
    '''
    splitSite = [0, 16, 28, 41]
    plt.imshow(image)
    for item in splitSite[1:]:
        plt.plot([item for i in range(image.size[1])], [i for i in range(image.size[1])])
    # plt.show()
    splitSite.append(image.size[0])

    # 对图片进行切割
    new_image = []
    for index in range(1, len(splitSite)):
        box = (splitSite[index - 1], 0, splitSite[index], image.size[1])
        new_image.append(image.crop(box))
        # new_image.save('./images/{}.gif'.format(str(index)))
    return new_image

def GetFileName(filePath):
    '''
    返回文件名
    :param filePath:
    :return:
    '''
    filenames = []
    for filename in os.listdir(filePath):
        filenames.append(filename)

    return filenames

def SplitAllImage():
    # 9、o、z是空的
    dict = {
        '0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0,
        'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0,
        'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0
    }
    filenames = GetFileName('./data_biaoji')
    for item in filenames:
        image = Image.open('./data_biaoji/{}'.format(item))
        tmp_image = GrayscaleAndBinarization(image)
        data_image = SplitImage(tmp_image)
        for i in range(len(data_image)):
            dict[item[i]] = dict[item[i]] + 1
            data_image[i].save('./data/{}/{}.jpg'.format((item[i]), dict[item[i]]))
    print(dict)


# image_after_GscaleAndBinarization = GrayscaleAndBinarization(image) # 转灰度并二值化
# image_after_GscaleAndBinarization.save('test.gif')
# SplitImage(image_after_GscaleAndBinarization)   # 分割图片
SplitAllImage()

