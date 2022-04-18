def main():
    from global_code import global_all as g
    from global_code import global_function as af
    from asian.india import india_craw as c

    c.main()  # 爬虫

    g.india()  # 处理数据

    af.draw_pic('india')  # 画图


if __name__ == '__main__':
    main()
