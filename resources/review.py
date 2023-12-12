from email_validator import EmailNotValidError, validate_email
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error



class MovieReviewResource(Resource):
    # 영화 리뷰 화면
    @jwt_required()
    def get(self):

        movieId = request.args.get('movieId')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()
        
        try :
            connection = get_connection()
            query = '''select u.nickname, u.gender, r.rating
                        from movie m 
                        left join review r
                        on m.id = r.movieId
                        join user u
                        on r.userId = u.id
                        where m.id = %s
                        order by r.createdAt desc
                        limit '''+str(offset)+''', '''+str(limit)+''';'''
            record = (movieId, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list:
                result_list[i]['rating'] = str(row['rating'])
                i = i + 1

            cursor.close()
            connection.close()
        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 500
        
        return {"result":"success","items":result_list}, 200
    

    # 영화 리뷰 작성
    @jwt_required()
    def post(self):
        
        data = request.get_json()
        movieId = request.args.get('movieId')
        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''insert into review
                        (movieId, userId, rating, content)
                        values
                        (%s, %s, %s, %s)'''
            record = (movieId, user_id, data['rating'], data['content'] )

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()
        
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 500


        return {"result":"success"}, 200