#student grade system

def calculate_grade(score):
    if score >= 90:
        print('very good you have secure A grade')
        return 'A'
    elif score >= 80:
        print('you have secure B grade')
        return 'B'
    elif score >= 70:
        print('you have secure C grade')
        return 'C'
    elif score >= 60:
        print('you have secure D grade')
        return 'D'
    else:
        print('you have secure F grade')    
        return 'F'
print('Welcome to student grade system')
mark = int(input('Enter your mark(1-100): '))
calculate_grade(mark)


