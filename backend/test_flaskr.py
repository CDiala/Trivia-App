import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
    "student", "student", "localhost:5432", self.database_name
)

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

    # Test Get Categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    # Test Get Categories With Wrong Endpoint
    def test_404_get_categories(self):
        res = self.client().get('/categoriess')

        self.assertEqual(res.status_code, 404)

    # Test Get Questions Endpoint
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    # Test Get Questions With Wrong Endpoint
    def test_404_get_questions(self):
        res = self.client().get('/questionss')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    # Test Pagination Beyond valid Page
    def test_404_sent_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # Test Delete Question Endpoint
    def test_delete_question(self):
        res = self.client().delete('/questions/26')
        data = json.loads(res.data)
      
        question = Question.query.filter(Question.id == 26).one_or_none()
        self.assertEqual(question, None)
        self.assertEqual(data['success'], True)

    # Test Delete Question With Wrong ID
    def test_422_delete_question(self):
        res = self.client().delete('/questions/0')
        data = json.loads(res.data)
      
        question = Question.query.filter(Question.id == 0).one_or_none()
        self.assertEqual(question, None)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    # Test Post Question Endpoint
    def test_insert_question(self):
        res = self.client().post(
            '/questions', 
            json={
                'question': 'What program is this?', 
                'answer': 'ALX-T',
                'difficulty': 1,
                'category': 1
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()