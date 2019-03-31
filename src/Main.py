from multiprocessing import cpu_count, Process, Manager
from sys import argv
from sys import exit as exit_program
from time import perf_counter_ns as clock
from time import sleep


def run(time, initial, offset, dictionary):
    """
    This is a worker processes that will be spawned to match your CPU thread count.
    :param time: how long this process will run for
    :param initial: the initial value to compute (2^initial)
    :param offset: the next power of two to compute each time, 2^x == 2^initial+offset
    :param dictionary: the shared variable to return the results of their findings
    :return: the buffer in the dictionary
    """
    buffer = []
    x = initial
    processed = 0

    def check_even(n):
        while n > 0:
            digit = n % 10
            if digit % 2 != 0:
                return False
            n //= 10
        return True

    def generate_and_check(n):
        if check_even(2 ** n):
            buffer.append(n)

    start_time = clock()
    while ((clock() - start_time) / 1_000_000_000) <= time:
        generate_and_check(x)
        x += offset
        processed += 1
    dictionary[initial] = buffer
    dictionary[f"p{initial}"] = processed
    dictionary[f"b{initial}"] = x * -1
    return dictionary


def main(time, thread):
    """
    The program itself, manages processes, a shared dictionary variable, and printing found values.
    :param time: the time to run the program
    :param thread: how many threads the program will use (how many processes are spawned)
    """
    manager = Manager()
    dictionary = manager.dict()
    processes = []
    for x in range(thread):
        processes.append(Process(target=run, args=(time, x, thread, dictionary)))
    for process in processes:
        process.start()
    sleep(time)
    for process in processes:
        process.join()
        process.terminate()
    found_buffer = []
    total_processed = 0
    largest_processed = 0
    for value in dictionary.values():
        if not isinstance(value, int):
            for buffer in value:
                found_buffer.append(buffer)
        else:
            if not value < 0:
                total_processed += value
            else:
                if largest_processed > value:
                    largest_processed = value
    found_buffer.sort()
    for found in found_buffer:
        print(f"Found: 2^{found}")
    print(f"\nTotal powers of two processed: {total_processed}")
    print(f"Largest power of two processed: {largest_processed * -1}")


if __name__ == "__main__":
    length = len(argv)
    if length == 2:
        time_to_run = argv[1]
        thread_count = cpu_count()
    elif length == 3:
        time_to_run = argv[1]
        thread_count = argv[2]
    else:
        time_to_run = 60
        thread_count = cpu_count()
    if time_to_run == 1:
        sec = "second"
    else:
        sec = "seconds"
    print(f"Running for {time_to_run} {sec}\n")
    main(time_to_run, thread_count)
    input("\nPress any key to exit the program...")
    exit_program()
