from tray_sensor import scanner

def main():
    s = scanner.Scanner()
    scan_entries = s.find_new_tags()
    print(scan_entries)

if __name__ == "__main__":
    main()