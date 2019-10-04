from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
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
            if new_image.getpixel((j, i)) == 0 and new_image.getpixel((j - 1, i)) == 255 and new_image.getpixel(
                    (j + 1, i)) == 255 and \
                    new_image.getpixel((j, i - 1)) == 255 and new_image.getpixel(
                (j - 1, i - 1)) == 255 and new_image.getpixel((j + 1, i - 1)) == 255 and \
                    new_image.getpixel((j, i + 1)) == 255 and new_image.getpixel(
                (j - 1, i + 1)) == 255 and new_image.getpixel((j + 1, i + 1)) == 255:
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
    splitSite.append(54)

    # 对图片进行切割
    new_image = []
    for index in range(1, len(splitSite)):
        box = (splitSite[index - 1], 0, splitSite[index], image.size[1])
        new_image.append(image.crop(box))
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
    '''
    分割所有图片
    :return:
    '''
    # 9、o、z是空的
    dict = {
        '0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0,
        'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0,
        'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0
    }
    filenames = GetFileName('./images/data_biaoji')
    for item in filenames:  # 图片名称
        image = Image.open('./images/data_biaoji/{}'.format(item))
        tmp_image = GrayscaleAndBinarization(image)
        data_image = SplitImage(tmp_image)
        for i in range(len(data_image)):  # 此处值为4，对切割后的四张图片进行处理
            dict[item[i]] = dict[item[i]] + 1
            data_image[i] = data_image[i].resize((14, 27))
            data_image[i].save('./images/data/{}/{}.jpg'.format((item[i]), dict[item[i]]))  # 总共获取了1884张图片

    print(dict)


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


def returnDataAndLabel(path='./images/data'):
    '''
    返回全部数据
    :param path: 图片路径
    :return: data 和 label
    '''
    raw = []
    datas = []
    labels = []
    for item1 in os.listdir(path):  # 文件路径
        label = item1
        for item2 in os.listdir(path + '/' + item1):
            data = []
            image = Image.open(path + '/' + item1 + '/' + item2).resize((14, 27))
            for i in range(image.size[1]):  # 读取像素通道值
                for j in range(image.size[0]):
                    data.append(image.getpixel((j, i)))
            data.append(label)  # 一张图片的数据
            if len(data) == (14 * 27 + 1):  # 图片尺寸
                raw.append(data)

    for i in range(len(raw)):
        tmp_data = raw[i][: -1]
        tmp_label = raw[i][-1]
        labels.append(tmp_label)
        datas.append(tmp_data)

    return datas, labels


def trainModel(datas, labels, isSave=True, path='./model/clf1.model'):
    '''
    训练模型
    :param datas: 数据集
    :param labels: 标签
    :return: 模型
    '''
    X_train, X_test, y_train, y_test = train_test_split(datas, labels, test_size=0.3, random_state=30)
    clf = RandomForestClassifier(n_estimators=500, max_depth=10, min_samples_split=10, random_state=0)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    score = accuracy_score(y_test, y_pred)
    print('Accuracy score:', score)
    if isSave:
        joblib.dump(clf, path)

    return clf


if __name__ == '__main__':
    # SplitAllImage()
    datas, labels = returnDataAndLabel()
    clf = trainModel(datas, labels)

