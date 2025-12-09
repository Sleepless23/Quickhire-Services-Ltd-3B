def select_from_list(title, items):

    print(f"\n--- {title} ---")
    
    for index, item in enumerate(items, start=1):
        print(f"[{index}] {item}")

    try:
        choice = int(input(f"Select {title} number: "))
        if 1 <= choice <= len(items):
            return items[choice - 1]
    except ValueError:
        pass

    print("Invalid choice! Operation cancelled.")
    return None
