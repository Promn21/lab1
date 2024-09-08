a = 5
b = 10

print("hello world")
print(a+b)

if a<b:
    print("a < b")
elif a == b:
    print(a == b)
else:
    print("I don't know") 


def mul_a_b(a, b):
    '''
    This function multiply a and b together.
    return a*b
    '''
    print(a * b)

mul_a_b(3, 4)



# Challenge 1
# Creating a function to calculate the area of circle.
# Users will specify number of circle
# The program will calculate the area of each circle with radius -1
# for example
# input : 5
# process : [the area of circle of radius 1-5 will be calculated].
# output : [pring all areas on the screen].

for i in range (0,10):
    print(i)

def cal_circle_area( radius ) :
    return 3.141 * radius * radius

circle_number = int(input("give me number: "))

areas = []
for i in range(1, circle_number+1):
    area = cal_circle_area(i)
    areas.append(area)

    print (f"the area of {i} is {area}")

areas.pop(0)
areas.append(10)
print(sum(areas))

# Challenge 2
# From the first challenge store all areas in an array.
# take the first area of the list, and the add 10 at the end of the array.
# Then, sum of all areas and display on screen

grades = {'Mark': 'A',
        'jib': 'B'}

print(grades ['Mark']) #A


