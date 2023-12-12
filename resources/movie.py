from email_validator import EmailNotValidError, validate_email
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error


class MovieResource(Resource):
    # 영화 정보 보여주기
    def get(self):

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try:
            connection = get_connection()
            query = '''select m.title, 
                        count(r.movieId) as review_cnt, 
                        ifnull(avg(r.rating), 0) as rating_avg
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        group by m.id
                        order by review_cnt desc
                        limit '''+str(offset)+''', '''+str(limit)+''';'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list:
                result_list[i]['review_cnt'] = str(row['review_cnt'])   
                result_list[i]['rating_avg'] = str(row['rating_avg'])
                i = i + 1

            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 500
        
        return {"result":"success", 
                "items":result_list, 
                "count":len(result_list)}, 200
    
# 영화 상세정보 화면
class MovieListResource(Resource):
    def get(self, movie_id):
        try :
            connection = get_connection()
            query='''select m.title, m.summary, 
                    m.year, m.attendance, avg(r.rating) as rating_avg
                    from movie m
                    join review r
                    on m.id = r.movieId
                    where m.id = %s;'''
            record =(movie_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list:
                result_list[i]['year'] = row['year'].isoformat()
                result_list[i]['rating_avg'] = str(row['rating_avg'])
                i = i + 1 

            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 500


        return {"error":"success","items":result_list[0]}


#영화 검색하기  
class MovieSearchResource(Resource):
    def post(self):
        
        data = request.get_json()

        try :
            connection = get_connection()
            query = '''select m.title, count(m.id) as review_cnt, 
                        ifnull(avg(r.rating), 0) as rationg_avg
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        where title like %s
                        group by m.id;'''
            record = (data['search'], )

            cursor = connection.cursor()
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 500

        
        return {"result":"success", 
                "items":result_list, 
                "count": len(result_list)}, 200