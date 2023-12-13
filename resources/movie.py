from email_validator import EmailNotValidError, validate_email
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error


class MovieResource(Resource):
    # 영화 정보 보여주기
    @jwt_required()
    def get(self):

        order = request.args.get('order')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''select m.id, m.title, 
                        count(r.id) reviewCnt, avg(r.rating) avgRating, 
                        if(f.id is null ,0 ,1) isFavorite
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        left join favorite f
                        on m.id = f.movieId and f.userId = %s
                        group by m.id
                        order by '''+order+''' desc
                        limit '''+str(offset)+''', '''+str(limit)+''';'''
            record = (user_id,)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list:
                result_list[i]['reviewCnt'] = str(row['reviewCnt'])   
                result_list[i]['avgRating'] = float(row['avgRating'])
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
    

class MovieListResource(Resource):
    # 영화 상세정보 화면
    @jwt_required(optional=True)
    def get(self, movie_id):
        
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query='''select m.*, avg(r.rating) as rating_avg, 
                    count(r.rating) as review_count
                    from movie m
                    left join review r
                    on m.id = r.movieId
                    where m.id = %s;'''
            record =(movie_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list:
                result_list[i]['year'] = row['year'].isoformat()
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['rating_avg'] = float(row['rating_avg'])
                i = i + 1 

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 500

        # 영화 상세정보는 result_list의 첫번째 데이터다
        # result_list[0]

        return {"error":"success","movieInfo":result_list[0]}


class MovieSearchResource(Resource):
    # 영화 검색하기
    @jwt_required(optional=True)
    def get(self):
        
        keyword = request.args.get('keyword')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''select m.id, m.title, m.summary, count(r.id) reviewCnt, 
                        ifnull(avg(r.rating), 0) avgRating
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        where m.title like '%'''+keyword+'''%' or m.summary like '%'''+keyword+'''%'
                        group by m.id
                        limit '''+offset+''', '''+limit+''';'''
            

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list:
                result_list[i]['avgRating'] = float(row['avgRating'])
                i = i + 1 

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
    
