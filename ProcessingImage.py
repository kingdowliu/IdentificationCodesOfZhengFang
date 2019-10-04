from PIL import Image


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


    # 去噪，去除独立点，将前后左右等九宫格中灰度通道值均为255的像素点的通道值设为255
    for i in range(1, new_image.size[1] - 1):
        for j in range(1, new_image.size[0] - 1):
            if new_image.getpixel((j, i)) == 0 and new_image.getpixel((j - 1, i)) == 255 and new_image.getpixel((j + 1, i)) == 255 and \
                    new_image.getpixel((j, i - 1)) == 255 and new_image.getpixel((j - 1, i - 1)) == 255 and new_image.getpixel((j + 1, i - 1)) == 255 and \
                new_image.getpixel((j, i + 1)) == 255 and new_image.getpixel((j - 1, i + 1)) == 255 and new_image.getpixel((j + 1, i + 1)) == 255:
                new_image.putpixel((j, i), 255)

    return new_image


def SplitImage(image):
    '''
    切割图像并保存，关键在于寻找切割位置
    :param image:
    :return:
    '''
    splitSite = [0, 16, 28, 41]
    splitSite.append(54)

    # 对图片进行切割
    new_image = []
    for index in range(1, len(splitSite)):
        box = (splitSite[index - 1], 0, splitSite[index], image.size[1])
        new_image.append(image.crop(box))
    return new_image


def featuretransfer(image):
    '''
    返回特征向量
    :param image: 图像
    :param label: 图像所属标签
    :return: 特征向量
    '''
    features = []
    image = image.resize((14, 27))
    for i in range(image.size[1]):
        for j in range(image.size[0]):
            features.append(image.getpixel((j, i)))

    return features


