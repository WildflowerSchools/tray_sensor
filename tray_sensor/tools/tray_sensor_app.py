from tray_sensor import scanner

def main():
    sc = scanner.Scanner()
    sc.find_new_tags()
    print(sc.tags)
    sc.run()

if __name__ == "__main__":
    main()