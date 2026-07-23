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
def get_valid_mark():
    while True:
        try:
            mark = int(input('Enter your mark (0-100): '))
        except ValueError:
            print('Please enter a whole number.')
            continue
        if 0 <= mark <= 100:
            return mark
        print('Enter valid mark (0-100). Please try again.')
grade_cache = {}

def get_grade_with_cache(mark):
    try:
        if mark in grade_cache:
            print(f'Retrieved from cache: grade {grade_cache[mark]} for mark {mark}')
            return grade_cache[mark]
        grade = calculate_grade(mark)
        grade_cache[mark] = grade
        return grade
    except Exception as e:
        print('Error while computing grade:', e)
        raise


if __name__ == '__main__':
    try:
        print('Welcome to student grade system')
        mark = get_valid_mark()
        get_grade_with_cache(mark)
    except KeyboardInterrupt:
        print('\nOperation cancelled by user.')
    except Exception as e:
        print('An unexpected error occurred:', e)