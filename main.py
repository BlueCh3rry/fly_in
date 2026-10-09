import parser


def main():
    m1 = parser.parser_txt()
    m1.show_links()
    print()
    m1.show_queue("hub", "corridorA")
    print()
    m1.show_all_queues()
    print()
    m1.show_all_zones()


if __name__ == "__main__":
    main()
