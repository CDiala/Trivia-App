from crypt import methods
from distutils.command.build import build
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Code to implement pagination
def paginate_resource(request, selections):
    page = request.args.get("page", 1, type=int)
    page_start = (page - 1) * QUESTIONS_PER_PAGE
    page_end = page_start + QUESTIONS_PER_PAGE

    data = [selection.format() for selection in selections]
    current_data = data[page_start:page_end]

    return current_data

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # CORS Setup
    cors = CORS(app, resources={r'*': {'origins': '*'}})

    # Set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 
            'Content-Type, Authorization'
            )
        response.headers.add(
            'Access-Control-Allow-Methods', 
            'GET, POST, PATCH, DELETE, OPTIONS'
            )
        return response

    # Build category list
    def build_categories():
        try: 
            categories = Category.query.order_by(Category.id).all()
            category_list = {}
            for category in categories:
                category_list[category.id] = category.type
                
            return category_list
        except:
            abort(404)

    # Categories
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            formatted_category_list = build_categories()

            return jsonify({
                'success': True,
                'categories': formatted_category_list
            })
        except:
            abort(404)

    # Get Questions
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        paginated_questions = paginate_resource(request, questions)
        categories = build_categories()
        current_category = request.args.get('category', 1, type=int)

        if len(paginated_questions) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'categories': categories,
                'questions': paginated_questions,
                'current_category': current_category,
                'total_questions': len(questions)
            })

    # Delete Question
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(422)
        else:
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_resource(request, selection)

            return jsonify({
                "success": True,
                'deleted': question_id,
                'current_questions': current_questions
            })

    # Search unique question / Create new question
    @app.route('/questions', methods=['POST'])
    def insert_question():
        body = request.get_json()
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)

        if search:
            filtered_questions = Question.query.order_by(Question.id).filter(
                Question.question.ilike("%{}%".format(search))
            )

            current_questions = paginate_resource(request, filtered_questions)

            return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(Question.query.all()),
            'currentCategory': 'History'
            })
        else:
            question = Question(
                question=new_question, 
                answer=new_answer, 
                category=new_category, 
                difficulty=new_difficulty
                )

            question.insert()
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_resource(request, questions)

            return jsonify({
                'success': True,
                'total_questions': len(questions),
                'questions': current_questions
            })

    # Get categorized questions
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_categorized_questions(category_id):
        try:
            filtered_questions = Question.query.filter(
                Question.category == category_id).all()
            paginated_questions = paginate_resource(request, filtered_questions)

            return jsonify({
                'questions': paginated_questions,
                'totalQuestions': len(filtered_questions),
                'currentCategory': Category.query.get(category_id).type
            })

        except:
            abort(404)

    # Quiz endpoint
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()
        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)
        try:
            if quiz_category['id'] == 0:
                questions = Question.query.order_by(Question.id).all()
            else:
                questions = Question.query.order_by(Question.id).filter(
                    Question.category == quiz_category['id']).all()
            
            unanswered_questions = []

            for question in questions:
                if question.question not in previous_questions:
                    unanswered_questions.append(question)

            random_index = random.randrange(len(unanswered_questions))
            next_question = unanswered_questions[random_index]
            return jsonify({
                'success': True,
                'question': next_question.format()
            })
        except:
            abort(422)

    # Not-found error handler
    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False, 
            "error": 404, 
            "message": "resource not found"
        }), 404
        
    # Unprocesable error handler
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422, 
            "message": "Unprocessable Entity"
        }), 422

    return app
