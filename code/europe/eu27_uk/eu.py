def main():
    from europe.eu27_uk import eu_craw as c
    from europe.eu27_uk import uk_bmrs as u
    from global_code import global_all as g
    from global_code import global_function as af

    c.main()  # 爬取entose数据

    u.main()  # 爬取bmrs数据

    g.eu()  # 处理数据

    af.draw_pic('eu27_uk')  # 作图


if __name__ == '__main__':
    main()
