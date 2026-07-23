#student grade system

def calculate_grade(mark):
    if mark >= 90:
        print('very good you have secure A grade')
        return 'A'
    elif mark >= 80:
        print('you have secure B grade')
        return 'B'
    elif mark >= 70:
        print('you have secure C grade')
        return 'C'
    elif mark >= 60:
        print('you have secure D grade')
        return 'D'
    else:
        print('you have secure F grade')
        return 'F'

print('Welcome to student grade system')
try:
    mark = int(input('Enter your mark(1-100): '))
    if mark < 0 or mark > 100:
            print("Invalid score. Please enter a score between 0 and 100.")
    else:
         calculate_grade(mark)
except ValueError:
    print("Invalid input. Please enter a valid score between 1 and 100.")


