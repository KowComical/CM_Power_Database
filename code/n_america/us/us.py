def main():
    from n_america.us import us_workflow as uc
    from global_code import global_all as g
    from global_code import global_function as af

    # 爬虫
    uc.main()

    # 处理数据
    g.us()
    # 作图
    af.draw_pic('us')


if __name__ == '__main__':
    main()
