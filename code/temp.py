import matplotlib.pyplot as plt  # plt 用于显示图片
import matplotlib.image as mpimg  # mpimg 用于读取图片

file_path = 'K:\\Github\\Python\\Work\\林晓娟\\Image Store\\2022\\04-05\\p1\\'


def search_file(file_path):
    import os
    file_name = []
    for parent, surnames, filenames in os.walk(file_path):
        for fn in filenames:
            file_name.append(os.path.join(parent, fn))
    return file_name


file_name = search_file(file_path)

good_list = []  # 好的结果保存在这里
bad_list = []  # 坏的结果保存在这里
for f in file_name:
    plt.figure(figsize=(15, 15))
    img = mpimg.imread(f)
    plt.imshow(img)
    plt.show()
    kow = input('保留吗: ')  # 显示完图片之后 输入Y或者N来决定参数去留
    if kow == 1:
        good_list.append(f)
    else:
        bad_list.append(f)
        print('不保留')
    plt.clf()  # will make the plot window empty
    plt.close()
