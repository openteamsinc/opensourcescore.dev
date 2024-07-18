from concurrent.futures import ThreadPoolExecutor, as_completed

def run_in_threads(function, args_list, max_workers=26):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(function, *args) for args in args_list]
        for future in as_completed(futures):
            future.result()
