import time
import threading

def task1():
    print("Starting task 1...")
    time.sleep(2)
    print("Task 1 completed")

def task2():
    print("Starting task 2...")
    time.sleep(3)
    print("Task 2 completed")

# Using threads
start_time = time.time()

# Create thread objects
thread1 = threading.Thread(target=task1)
thread2 = threading.Thread(target=task2)

# Start threads
thread1.start()
thread2.start()

# Wait for threads to complete
thread1.join()
thread2.join()

end_time = time.time()

print(f"Total time (threaded): {end_time - start_time} seconds")
