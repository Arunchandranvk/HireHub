from django.core.management.base import BaseCommand
from django.db import transaction
from college_admin.models import Subject, Question, Option

PYTHON_QUESTIONS = [
    {
        'text': 'What is the output of 2 + 2?',
        'difficulty': 'easy',
        'options': [
            {'text': '3', 'is_correct': False},
            {'text': '4', 'is_correct': True},
            {'text': '5', 'is_correct': False},
            {'text': '6', 'is_correct': False}
        ]
    },
    {
        'text': 'Which of the following is a valid way to declare a list in Python?',
        'difficulty': 'easy',
        'options': [
            {'text': 'list = []', 'is_correct': True},
            {'text': 'list = ()', 'is_correct': False},
            {'text': 'list = {}', 'is_correct': False},
            {'text': 'list = [[]]', 'is_correct': False}
        ]
    },
    {
        'text': 'What does the len() function do?',
        'difficulty': 'easy',
        'options': [
            {'text': 'Adds two numbers', 'is_correct': False},
            {'text': 'Returns the length of an object', 'is_correct': True},
            {'text': 'Converts a string to lowercase', 'is_correct': False},
            {'text': 'Multiplies numbers', 'is_correct': False}
        ]
    },
    {
        'text': 'Which method is used to add an element to the end of a list?',
        'difficulty': 'easy',
        'options': [
            {'text': 'list.add()', 'is_correct': False},
            {'text': 'list.insert()', 'is_correct': False},
            {'text': 'list.append()', 'is_correct': True},
            {'text': 'list.extend()', 'is_correct': False}
        ]
    },
    {
        'text': 'What is the result of 7 // 3?',
        'difficulty': 'medium',
        'options': [
            {'text': '2.333', 'is_correct': False},
            {'text': '2', 'is_correct': True},
            {'text': '3', 'is_correct': False},
            {'text': '7/3', 'is_correct': False}
        ]
    },
    {
        'text': 'Which of these is NOT a valid Python data type?',
        'difficulty': 'medium',
        'options': [
            {'text': 'int', 'is_correct': False},
            {'text': 'float', 'is_correct': False},
            {'text': 'string', 'is_correct': True},
            {'text': 'complex', 'is_correct': False}
        ]
    },
    {
        'text': 'What does the "global" keyword do?',
        'difficulty': 'hard',
        'options': [
            {'text': 'Creates a global variable', 'is_correct': False},
            {'text': 'Allows modification of a global variable inside a function', 'is_correct': True},
            {'text': 'Imports global modules', 'is_correct': False},
            {'text': 'Defines a global class', 'is_correct': False}
        ]
    },
    {
        'text': 'What is a decorator in Python?',
        'difficulty': 'hard',
        'options': [
            {'text': 'A way to decorate functions', 'is_correct': False},
            {'text': 'A function that modifies another function', 'is_correct': True},
            {'text': 'A type of list comprehension', 'is_correct': False},
            {'text': 'A method to create objects', 'is_correct': False}
        ]
    },
    {
        'text': 'Which method is used to remove the last element from a list?',
        'difficulty': 'easy',
        'options': [
            {'text': 'list.remove()', 'is_correct': False},
            {'text': 'list.pop()', 'is_correct': True},
            {'text': 'list.delete()', 'is_correct': False},
            {'text': 'list.clear()', 'is_correct': False}
        ]
    },
    {
        'text': 'What does the "is" operator do?',
        'difficulty': 'medium',
        'options': [
            {'text': 'Checks for equality', 'is_correct': False},
            {'text': 'Checks for identity', 'is_correct': True},
            {'text': 'Assigns a value', 'is_correct': False},
            {'text': 'Compares types', 'is_correct': False}
        ]
    },
    {
        'text': 'How do you create a tuple?',
        'difficulty': 'easy',
        'options': [
            {'text': 'tuple = []', 'is_correct': False},
            {'text': 'tuple = ()', 'is_correct': True},
            {'text': 'tuple = {}', 'is_correct': False},
            {'text': 'tuple = ""', 'is_correct': False}
        ]
    },
    {
        'text': 'What is list comprehension?',
        'difficulty': 'medium',
        'options': [
            {'text': 'A way to create lists in one line', 'is_correct': True},
            {'text': 'A method to sort lists', 'is_correct': False},
            {'text': 'A function to merge lists', 'is_correct': False},
            {'text': 'A way to delete list elements', 'is_correct': False}
        ]
    },
    {
        'text': 'Which function is used to convert a string to an integer?',
        'difficulty': 'easy',
        'options': [
            {'text': 'str()', 'is_correct': False},
            {'text': 'int()', 'is_correct': True},
            {'text': 'float()', 'is_correct': False},
            {'text': 'convert()', 'is_correct': False}
        ]
    },
    {
        'text': 'What does the "yield" keyword do?',
        'difficulty': 'hard',
        'options': [
            {'text': 'Stops a function', 'is_correct': False},
            {'text': 'Creates a generator function', 'is_correct': True},
            {'text': 'Defines a return value', 'is_correct': False},
            {'text': 'Checks a condition', 'is_correct': False}
        ]
    },
    {
        'text': 'How do you open a file in Python?',
        'difficulty': 'medium',
        'options': [
            {'text': 'file.open()', 'is_correct': False},
            {'text': 'open(filename, mode)', 'is_correct': True},
            {'text': 'file(filename)', 'is_correct': False},
            {'text': 'create(filename)', 'is_correct': False}
        ]
    }
]

WEB_DEVELOPMENT_QUESTIONS = [
    {
        'text': 'What does HTML stand for?',
        'difficulty': 'easy',
        'options': [
            {'text': 'Hyper Text Markup Language', 'is_correct': True},
            {'text': 'High Tech Modern Language', 'is_correct': False},
            {'text': 'Hyper Transfer Markup Language', 'is_correct': False},
            {'text': 'Hyper Text Modern Language', 'is_correct': False}
        ]
    },
    {
        'text': 'Which tag is used to define an unordered list in HTML?',
        'difficulty': 'easy',
        'options': [
            {'text': '<ol>', 'is_correct': False},
            {'text': '<ul>', 'is_correct': True},
            {'text': '<list>', 'is_correct': False},
            {'text': '<li>', 'is_correct': False}
        ]
    },
    {
        'text': 'What does CSS stand for?',
        'difficulty': 'easy',
        'options': [
            {'text': 'Computer Style Sheets', 'is_correct': False},
            {'text': 'Cascading Style Sheets', 'is_correct': True},
            {'text': 'Creative Style Sheets', 'is_correct': False},
            {'text': 'Colorful Style Sheets', 'is_correct': False}
        ]
    },
    {
        'text': 'Which property is used to change the text color in CSS?',
        'difficulty': 'easy',
        'options': [
            {'text': 'font-color', 'is_correct': False},
            {'text': 'text-color', 'is_correct': False},
            {'text': 'color', 'is_correct': True},
            {'text': 'background-color', 'is_correct': False}
        ]
    },
    {
        'text': 'What is the correct JavaScript syntax to change content?',
        'difficulty': 'medium',
        'options': [
            {'text': 'document.getElement("p").innerHTML = "Hello"', 'is_correct': False},
            {'text': 'document.getElementById("demo").innerHTML = "Hello"', 'is_correct': True},
            {'text': '#demo.innerHTML = "Hello"', 'is_correct': False},
            {'text': 'document.getElementByName("p").innerHTML = "Hello"', 'is_correct': False}
        ]
    },
    {
        'text': 'Which HTTP method is used to send data to a server?',
        'difficulty': 'medium',
        'options': [
            {'text': 'GET', 'is_correct': False},
            {'text': 'POST', 'is_correct': True},
            {'text': 'SEND', 'is_correct': False},
            {'text': 'SUBMIT', 'is_correct': False}
        ]
    },
    {
        'text': 'What is Bootstrap?',
        'difficulty': 'medium',
        'options': [
            {'text': 'A programming language', 'is_correct': False},
            {'text': 'A CSS framework', 'is_correct': True},
            {'text': 'A JavaScript library', 'is_correct': False},
            {'text': 'A database system', 'is_correct': False}
        ]
    },
    {
        'text': 'Which attribute is used to make an input field required?',
        'difficulty': 'easy',
        'options': [
            {'text': 'must', 'is_correct': False},
            {'text': 'require', 'is_correct': False},
            {'text': 'required', 'is_correct': True},
            {'text': 'mandatory', 'is_correct': False}
        ]
    },
    {
        'text': 'What does API stand for?',
        'difficulty': 'medium',
        'options': [
            {'text': 'Advanced Programming Interface', 'is_correct': False},
            {'text': 'Application Programming Interface', 'is_correct': True},
            {'text': 'Automated Program Interface', 'is_correct': False},
            {'text': 'Automated Programming Interface', 'is_correct': False}
        ]
    },
    {
        'text': 'Which method stops event bubbling in JavaScript?',
        'difficulty': 'hard',
        'options': [
            {'text': 'stopPropagation()', 'is_correct': True},
            {'text': 'stopEvent()', 'is_correct': False},
            {'text': 'preventBubble()', 'is_correct': False},
            {'text': 'cancelEvent()', 'is_correct': False}
        ]
    },
    {
        'text': 'What is the purpose of the <meta> tag?',
        'difficulty': 'medium',
        'options': [
            {'text': 'To create hyperlinks', 'is_correct': False},
            {'text': 'To define metadata about an HTML document', 'is_correct': True},
            {'text': 'To style web pages', 'is_correct': False},
            {'text': 'To create JavaScript functions', 'is_correct': False}
        ]
    },
    {
        'text': 'Which selector selects all elements in CSS?',
        'difficulty': 'easy',
        'options': [
            {'text': 'all', 'is_correct': False},
            {'text': '*', 'is_correct': True},
            {'text': 'select-all', 'is_correct': False},
            {'text': 'everything', 'is_correct': False}
        ]
    },
    {
        'text': 'What is the correct way to write a JavaScript array?',
        'difficulty': 'easy',
        'options': [
            {'text': 'var colors = "red", "green", "blue"', 'is_correct': False},
            {'text': 'var colors = (1:"red", 2:"green", 3:"blue")', 'is_correct': False},
            {'text': 'var colors = ["red", "green", "blue"]', 'is_correct': True},
            {'text': 'var colors = {red, green, blue}', 'is_correct': False}
        ]
    },
    {
        'text': 'What does the z-index property do?',
        'difficulty': 'medium',
        'options': [
            {'text': 'Rotates an element', 'is_correct': False},
            {'text': 'Specifies the stack order of an element', 'is_correct': True},
            {'text': 'Zooms an image', 'is_correct': False},
            {'text': 'Sets the opacity', 'is_correct': False}
        ]
    },
    {
        'text': 'Which method is used to parse a JSON string in JavaScript?',
        'difficulty': 'medium',
        'options': [
            {'text': 'parseJSON()', 'is_correct': False},
            {'text': 'JSON.parse()', 'is_correct': True},
            {'text': 'JSON.stringify()', 'is_correct': False},
            {'text': 'convertJSON()', 'is_correct': False}
        ]
    }
]

class Command(BaseCommand):
    help = 'Populates the database with MCQ questions'

    def handle(self, *args, **kwargs):
        # Create or get subjects
        python_subject, created = Subject.objects.get_or_create(
            name='Python Programming',
            defaults={'description': 'Test your Python programming knowledge'}
        )
        
        web_subject, created = Subject.objects.get_or_create(
            name='Web Development',
            defaults={'description': 'Test your web development skills'}
        )

        # Transaction to ensure atomic insertion
        with transaction.atomic():
            # Clear existing questions for these subjects to avoid duplicates
            Question.objects.filter(subject__in=[python_subject, web_subject]).delete()

            # Add Python Questions
            self.add_questions(python_subject, PYTHON_QUESTIONS)
            
            # Add Web Development Questions
            self.add_questions(web_subject, WEB_DEVELOPMENT_QUESTIONS)

        self.stdout.write(self.style.SUCCESS('Successfully populated questions'))

    def add_questions(self, subject, questions_data):
        for q_data in questions_data:
            # Create question
            question = Question.objects.create(
                subject=subject,
                text=q_data['text'],
                difficulty=q_data['difficulty']
            )
            
            # Create options for the question
            for opt_data in q_data['options']:
                Option.objects.create(
                    question=question,
                    text=opt_data['text'],
                    is_correct=opt_data['is_correct']
                )