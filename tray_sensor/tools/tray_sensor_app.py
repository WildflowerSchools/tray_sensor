from tray_sensor import scanner

def main():
    s = scanner.Scanner()
    s.find_new_tags()
    print(s.tags)
    import pdb;pdb.set_trace()

if __name__ == "__main__":
    main()