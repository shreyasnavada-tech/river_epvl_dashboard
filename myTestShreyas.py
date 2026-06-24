# import os
# import time


# # class Framehandler:
# #     def __init__(self, excelFile , excelFile2 , logFile1,txtfile1):
# #         self.excelFile = excelFile
# #         self.excelFile2= excelFile2
# #         self.logFile1 = logFile1
# #         self.txtfile1 = txtfile1

# #     def excelDataLoader(self):
# #         print(f"Frame created by loading data from {self.excelFile} and {self.excelFile2}")
# #         return f"{self.excelFile} and {self.excelFile2} data is passed  and DF is created"

# #     def dataFrameHandler(self):
# #         print("Data Frame handling unit")
# #         return True

# #     def multiTypePlotting(self):
# #         return True

# #     def ui(self):
# #         return True

# #     def api(self):
# #         return True

# # class DataFrame(Framehandler):
# #     """
# #     File Read
# #     File Write
# #     File Append
# #     """

# #     filepath = r"C:\Users\shreyasnavada_rideri\Downloads\testFileSample.txt"
# #     def excelDataLoader(self):
# #         print("excelDataLoader")
# #         try:
# #             excelDataFile = open(self.filepath ,"r+")
# #             content = print(excelDataFile.read())
# #             excelDataFile.write("hello file reader")
# #             return content
# #         finally:
# #             excelDataFile.close()

# #     def multiTypePlotting(self):
# #         print("multiTypePlotting child class method")
# #         with open(self.filepath, "w") as excelDataFile1:
# #             excelDataFile1.write("hello file reader")
# #         return super().multiTypePlotting()


# #     def ui(self):
# #         print("multi-UI-Plotting")
# #         return super().ui()

# #     def api(self):
# #         print("The api backend")
# #         return super().api()


# # datafile = DataFrame("Value1","Value2" , "Value3" , "value4")
# # datafile.excelDataLoader()
# # datafile.ui()
# # datafile.multiTypePlotting()
# # datafile.api()


# # # s = "GeeksforGeeks"
# # # print(s[1:4])    # characters from index 1 to 3
# # # print(s[:3])     # from start to index 2
# # # print(s[3:])     # from index 3 to end
# # # print(s[::-1])   # reverse string

# # # for char in s:
# # #     print(char)
# # 10 , 5,5,2.5,2.5,5,8,12.5,8 ,40
# #List and List Types .


# b = [ 40 , 8 , 12.5 , 8 , 10 , 2.5 , 2.5 , 5 , 5,5,14,2.25,1.5]
# sum = 0
# for num in b:
#     #sum = sum + a
#     # print(num)
#     # print(type(num))
#     sum = sum + num

# print(f"The value of b is {b}")
# print(f"Total sum value is {sum}")

# a = []
# a.append(10)
# print("After append(10):", a)

# a.insert(0, 5)
# a.insert(2,345)
# a.insert(-3,400)
# print("After insert:", a)

# a.extend([15, 20, 25])
# a.extend([0,0,33, 55,99,100])
# print("After extend:", a)
# # a.clear()
# # print("After clear():", a)

# # a = [10, 20, 30, 40, 50]
# # a.remove(30)
# # a.remove(10)
# # print("After remove:", a)

# popped_val = a.pop(1)
# print("Popped element:", popped_val)
# print("After pop(1):", a)

# del a[0]
# print("After del:", a)

# print(f"The value of a is {a}")
# print(f"The value of b is {b}")
# c = a+ b
# print(f"The value of c is {c}")
# print(len(c))

# squares = [x**2 for x in c]
# print(squares)

# fruits = ["apple", "banana", "cherry"]
# uppercase_fruits = [fruit.upper() for fruit in fruits]
# # Output: ['APPLE', 'BANANA', 'CHERRY']

# numbers = [1, 2, 3, 4, 5]
# evenodd=["even" if n % 2 ==0 else "odd" for n in numbers ]

# x=(1,2,3,3,6,7,66,77,8,0)
# y = tuple(c)
# print(print(f"The Value of converted tuple  is {y}"))
# z = list(y)
# print(f"The Value of converted list is {z}")


# tup = (5, 'Welcome', 7, 'Geeks')
# print(tup)

# # Creating a Tuple with nested tuples
# tup1 = (0, 1, 2, 3)
# tup2 = ('python', 'geek')
# tup3 = (tup1, tup2)
# print(tup3)

# # Creating a Tuple with repetition
# tup1 = ('Geeks') * 3
# print(tup1)

# tup = (1, 2, 3, 4, 5)

# m, *n, o = tup

# print(m)
# print(n)
# print(o)

# tp = (1 , 2, 3, 4,5 ,6,7,8,99)
# tp2 = (1 , 3,4,5,6,7,8,00)
# tp3 = tp + tp2
# print(tp3)

# print(tp3[::-2]) # in steps of 2 , print
# print(tp3[::2])
# print(tp3[:2])

# tpp = (tp, tp2 , tp3)
# print(type(tpp))

# d = {1: 'Geeks', 2: 'For', 3: 'Geeks', 'age':22}

# # Using del
# del d["age"]
# print(d)

# # Using pop()
# val = d.pop(1)
# print(val)

# # Using popitem()
# key, val = d.popitem()
# print(f"Key: {key}, Value: {val}")

# # Using clear()
# d.clear()
# print(d)

# d = {1: 'Geeks', 2: 'For', 'age':22 , 3:"global" , 4:"core" , 5 : "Test",6 :"Seven"}

# # Iterate over key-value pairs
# for key, value in d.items():
#     print(f"the values are {key}: {value}")

# for key,value in d.items():
#     print(f"The values present in the column is {key}: {value}")

# e = {1: 'Geeks', 2: 'For', 3: {'A': 'Welcome', 'B': 'To', 'C': 'Geeks'}}
# print(e)
# for key,value in e.items():
#     print(f"The values present in the column is {key}: {value}")


# e = {1: 'Geeks', 2: 'For', 3: {'A': 'Welcome', 'B': 'To', 'C': 'Geeks'}}
# print(e)
# for key,value in e.items():
#     print(f"The values present in the column is {key}: {value}")

# data ={ 1 : 'PDF1', 2 : "PDF2" , 3 :"PDF3" }
# print(data)
# print(data[1])

# for key in data.keys():
#     print(f"the key value are {key}")

# for key,value in data.items():
#     print(f"{key} and {value}")


# d = {1: 'Geeks', 2: 'For', 3: {'A': 'Welcome', 'B': 'To', 'C': 'Geeks'}}
# print(d)

# for i,j in d.items():
#     print(f"{i}  and {j}")
#     print(f"{i}")
#     print(f"{j}")

# def print_details(**kwargs):
#     """Prints key-value pairs of details."""
#     for key, value in kwargs.items():
#         print(f"{key}: {value}")

# print_details(name="John", age=30, country="USA")
# # Output:
# # name: John
# # age: 30
# # country: USA

# list1 = ["A" , 1 , 2, 3,5,6,70,889,9.6,5.4,"Motordata"]
# tuple1 = tuple(list1)
# dict1= {}

# print(list1)
# print(tuple1)
# print(dict1)
# print(dict1)
# print(dict1)


# # #z  #######################################################
# # import os
# # import json
# # from pathlib import Path


# # def read_text_file(filepath: str) -> str:
# #     """Reads content from a text file and returns it as a string."""
# #     try:
# #         # Use 'with open' for automatic file closure
# #         with open(filepath, 'r', encoding='utf-8') as file:
# #             return file.read()
# #     except FileNotFoundError:
# #         print(f"Error: The file '{filepath}' does not exist.")
# #         return FileNotFoundError
# #     except Exception as e:
# #         print(f"An error occurred while reading the file: {e}")
# #         return f"An error occurred while reading the file: {e}"

# # def write_text_file(filepath: str, content: str, mode: str = 'w'):
# #     """Writes content to a text file. Mode 'w' overwrites, 'a' appends."""
# #     try:
# #         # 'w' mode creates the file if it doesn't exist, and overwrites if it does
# #         with open(filepath, mode='w', encoding='utf-8') as file:
# #             file.write(content)
# #         print(f"Content successfully written to '{filepath}' in mode '{mode}'.")
# #     except Exception as e:
# #         print(f"An error occurred while writing to the file: {e}")

# # def read_json_file(filepath: str):
# #     """Reads data from a JSON file and returns a Python object."""
# #     try:
# #         with open(filepath, 'r', encoding='utf-8') as file:
# #             data = json.load(file)
# #             return data
# #     except FileNotFoundError:
# #         print(f"Error: The file '{filepath}' does not exist.")
# #         return None
# #     except json.JSONDecodeError:
# #         print(f"Error: Could not decode JSON from the file '{filepath}'.")
# #         return None
# #     except Exception as e:
# #         print(f"An error occurred while reading the JSON file: {e}")
# #         return None

# # def write_json_file(filepath: str, data: dict):
# #     """Writes a Python object to a JSON file."""
# #     try:
# #         with open(filepath, 'w', encoding='utf-8') as file:
# #             json.dump(data, file, indent=4)
# #         print(f"Data successfully written to JSON file '{filepath}'.")
# #     except Exception as e:
# #         print(f"An error occurred while writing the JSON file: {e}")

# # def delete_file(filepath: str):
# #     """Deletes a file if it exists."""
# #     try:
# #         if os.path.exists(filepath):
# #             os.remove(filepath)
# #             print(f"File '{filepath}' deleted successfully.")
# #         else:
# #             print(f"Error: The file '{filepath}' does not exist.")
# #     except Exception as e:
# #         print(f"An error occurred while deleting the file: {e}")

# # def list_files_in_directory(directory_path: str):
# #     """Lists all files in a given directory using the pathlib module."""
# #     path = Path(directory_path)
# #     if path.is_dir():
# #         print(f"Files in directory '{directory_path}':")
# #         for entry in path.iterdir():
# #             if entry.is_file():
# #                 print(f"- {entry.name}")
# #     else:
# #         print(f"Error: '{directory_path}' is not a valid directory.")


# # # main_script.py


# # # Example 1: Write and Read a text file
# # filename_txt = "sample.txt"
# # file_utils.write_text_file(filename_txt, "Hello, world!\nThis is a test.")
# # content = file_utils.read_text_file(filename_txt)
# # print(f"\nRead from file: {content}")

# # # Example 2: Write and Read a JSON file
# # filename_json = "data.json"
# # data_to_write = {"name": "Alice", "age": 30, "city": "New York"}
# # file_utils.write_json_file(filename_json, data_to_write)
# # data_read = file_utils.read_json_file(filename_json)
# # print(f"\nRead from JSON: {data_read}")

# # # Example 3: List files in the current directory
# # file_utils.list_files_in_directory(".")

# # # Example 4: Clean up by deleting the files
# # file_utils.delete_file(filename_txt)
# # file_utils.delete_file(filename_json)


# # with open("geek.txt", "w") as file:
# #     file.write("Hello, Python!\n")
# #     file.write("File handling is easy with Python.")

# # print("File written successfully")


# try:
#     #x = int("str") # This will cause ValueError
#     inv = 1 / x    # Inverse calculation
#     div = 5 / 0
# except ValueError:
#     print("Not Valid!")

# except ZeroDivisionError:
#     print("Zero has no inverse!")

# except Exception as e:
#     print(f"the error is {e}")

# listA = []
# for num in range(1,1000000000):
#     if num %2 ==0:
#         listA.append(num)
#     else:
#         pass
# print(listA)

# import numpy as np

# listcomprehension =[value for value in range (1,10000000000000000) if value%2 ==0]
# print(listcomprehension)


# # numpy library
# listnp = np.arange(1, 10000000000000000000000000)
# print(listnp)


# numpy library
# ctype library


import time

# importing required packages
import numpy

# size of arrays and lists

size = 10000

# declaring lists

list1 = [value for value in range(size) if value % 2 == 0]
print(list1)
list2 = [value for value in range(size) if value % 2 == 0]
print(list2)

# declaring arrays
array1 = numpy.arange(size)
array2 = numpy.arange(size)

# capturing time before the multiplication of Python lists
initialTime = time.time()

# multiplying elements of both the lists and stored in another list
resultantList = [(a * b) for a, b in zip(list1, list2)]

# calculating execution time
print(
    "Time taken by Lists to perform multiplication:",
    (time.time() - initialTime),
    "seconds",
)

# capturing time before the multiplication of Numpy arrays
initialTime = time.time()

# multiplying elements of both the Numpy arrays and stored in another Numpy array
resultantArray = array1 * array2

# calculating execution time
print(
    "Time taken by NumPy Arrays to perform multiplication:",
    (time.time() - initialTime),
    "seconds",
)


class Triangle:
    def __init__(self, base=0, height=0):
        if base and height:
            self.base = base
            self.height = height
        else:  # No arguments
            self.base = 0
            self.height = 0

    def areaoftriangle(self):
        return self.base * self.height * 0.5

    def display_info(self):
        print(
            f"base: {self.base}, Height: {self.height}, Area: {self.areaoftriangle()}"
        )


# Create instances using different "constructors"
rect1 = Triangle(10, 20)  # Two arguments     # One argument (treated as square)
rect3 = Triangle()  # No arguments

# Display the rectangles' information
rect1.display_info()
rect3.display_info()


def testing():
    x = 5
    print(x)
    print(f"global variable is {y}")


y = 3
z = testing()
print(z)


class MotorRun:
    motor1 = "DC"  # Class Variable
    motor2 = "Dyno"  # Class Variables

    def __init__(self, input1, input2):
        self.input1 = input1  # instance variable
        self.input2 = input2  # instance variable

    def motorrun(self):
        return f"The value  is {self.input1*self.input2}"


s1 = MotorRun(3, 4)
print(s1.motorrun())
print(s1.motor1)
print(s1.motor2)
