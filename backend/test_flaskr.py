import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

load_dotenv()
DB_PATH_TEST = os.getenv('DB_PATH_TEST')
DB_NAME_TEST = os.getenv('DB_NAME_TEST')


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME_TEST

        self.database_path = DB_PATH_TEST

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories_success(self):

        response = self.client().get('/categories')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_categories_failed(self):

        response = self.client().get('/categories/45')
        data = json.loads(response.data)

        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_success(self):

        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_invalid_page_number(self):
        response = self.client().get('/questions?page=100000')
        data = json.loads(response.data)

        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question_success(self):
        response = self.client().delete('/questions/4')
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 4)

    def test_delete_question_failed(self):
        response = self.client().delete('questions/2000')
        data = json.loads(response.data)

        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_search_question_success(self):
        response = self.client().post(
            'questions/search', json={"searchTerm": "bio"})
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_invalid_search_input(self):
        response = self.client().post(
            'questions/search', json={"searchTerm": "dummystring"})
        data = json.loads(response.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_create_question_success(self):
        question = {
            'question': 'another dummy question?',
            'difficulty': 1,
            'category': '3',
            'answer': 'another dummy answer',

        }

        response = self.client().post('/questions', json=question)
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_create_question_failed(self):
        question = {
            'question': 'another dummy question?',
            'difficulty': 1,
            'category': '3',
            'answer': 'another dummy answer',

        }

        response = self.client().post('/questions/45', json=question)
        data = json.loads(response.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "method not allowed")

    def test_get_questions_by_category_success(self):
        response = self.client().get('/categories/3/questions')
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_questions_by_category_failed(self):
        response = self.client().get('/categories/3000/questions')
        data = json.loads(response.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_get_next_quiz_question_success(self):
        request_params = {
            'previous_questions': [3, 7],
            'quiz_category': {
                'id': 4,
                'type': 'Science'
            }
        }

        response = self.client().post('/quizzes', json=request_params)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_next_quiz_question_failed(self):
        request_params = {
            'previous_questions': [3, 7],
            'quiz_category': {
                'id': 4,
                'type': 'Science'
            }
        }

        response = self.client().post('/quizzes')
        data = json.loads(response.data)

        self.assertEqual(data['success'], False)

        self.assertEqual(data['error'], 400)

        self.assertEqual(data['message'], "bad request")

    # """
    # TODO
    # Write at least one test for each test for successful operation and for expected errors.
    # """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
