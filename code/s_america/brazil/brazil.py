def main():
    from global_code import global_all as g
    from global_code import global_function as af
    from s_america.brazil import brazil_craw as bc

    # 爬虫
    bc.main()
    # 处理数据
    g.brazil()
    # 作图
    af.draw_pic('brazil')


if __name__ == '__main__':
    main()
