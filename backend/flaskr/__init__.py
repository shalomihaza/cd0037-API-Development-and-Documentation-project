import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, ordered_questions):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in ordered_questions]
    current_questions = questions[start:end]

    return current_questions


def to_dict(items):
    obj = {}
    for item in items:
        obj[item.id] = item.type

    return obj


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            # print('categories', categories)
            # print('categories_obj', to_dict(categories))

            return jsonify(
                {
                    "success": True,
                    "categories": to_dict(categories),

                }
            ), 200

        except:
            abort(404)
    # """
    # @TODO:
    # Create an endpoint to handle GET requests for questions,
    # including pagination (every 10 questions).
    # This endpoint should return a list of questions,
    # number of total questions, current category, categories.

    # TEST: At this point, when you start the application
    # you should see questions and categories generated,
    # ten questions per page and pagination at the bottom of the screen for three pages.
    # Clicking on the page numbers should update the questions.
    # """

    @app.route('/questions')
    def get_questions():

        ordered_questions = Question.query.order_by(Question.id).all()
        ordered_categories = Category.query.order_by(Category.id).all()
        current_questions = paginate_questions(request, ordered_questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(ordered_questions),
                "current_category": ordered_categories[0].type,
                "categories": to_dict(ordered_categories),

            }
        ), 200
    # """

    # @TODO:
    # Create an endpoint to DELETE question using a question ID.

    # TEST: When you click the trash icon next to a question, the question will be removed.
    # This removal will persist in the database and when you refresh the page.
    # """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(422)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                }
            ), 200

        except:
            abort(422)

    # """

    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.

    # TEST: When you submit a question on the "Add" tab,
    # the form will clear and the question will appear at the end of the last page
    # of the questions list in the "List" tab.
    # """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        question_string = body.get("question", '')
        answer = body.get("answer", '')
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        if ((question_string == '') or (answer is '')):
            # print('no question/answer')
            abort(405)

            return
        else:
            try:

                question = Question(question=question_string, answer=answer,
                                    category=category, difficulty=difficulty)
                question.insert()

                ordered_questions = Question.query.order_by(Question.id).all()

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "total_questions": len(ordered_questions),
                    }
                )

            except:
                abort(405)
    # """
    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.

    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # """
    @app.route('/questions/search', methods=['POST'])
    def search():

        search_term = request.json.get('searchTerm', '')

        if search_term == '':
            abort(422)
        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

        if len(questions) == 0:
            abort(404)

        current_questions = paginate_questions(request, questions)

        return jsonify(
            {
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'current_category': questions[0].category,
            }
        )

    # """
    # @TODO:
    # Create a GET endpoint to get questions based on category.

    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.
    # """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter(
                Question.category == category_id).all()

            category = Category.query.filter(
                Category.id == category_id).one_or_none()

            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category.type
            })

        except:
            abort(404)
    # """
    # @TODO:
    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.

    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.
    # """
    @app.route('/quizzes', methods=['POST'])
    def get_next_quiz_question():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')

            if ((quiz_category is None) or (previous_questions is None)):
                abort(400)

            if (quiz_category['id'] == 0):
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.category == quiz_category['id']).all()

            next_question = random.choice(questions)

            while True:
                if next_question.id in previous_questions:
                    next_question = random.choice(questions)
                else:
                    break

            return jsonify({
                'success': True,
                'question': next_question.format(),
            })
        except:
            abort(400)

    @ app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404,
                    "message": "resource not found"}),
            404,
        )

    @ app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                    "message": "unprocessable"}),
            422,
        )

    @ app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @ app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({"success": False, "error": 405,
                    "message": "method not allowed"}),
            405,
        )

    return app
