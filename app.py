from flask import Flask, render_template as ren, request, redirect, url_for, flash
import pandas as pd
import db

app = Flask(__name__)

app.secret_key = 'secret_key1234'

@app.route('/')
def index():
    return ren('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """유가 정보 데이터베이스에 저장"""
    if request.method == 'POST':
        file = request.files['file']
        df = pd.read_csv(file, encoding="utf-8-sig")
        
        #필수 칼럼명 인증
        required_columns = ['고유번호', '지역', '상호', '주소', '상표', '셀프여부', '고급휘발유', '휘발유', '경유', '실내등유']
        
        if list(df.columns) != required_columns:
            flash('필수 칼럼이 누락되었습니다. 다시 확인해주세요.')
            return redirect(url_for('upload'))
        
        #결측치 제거
        df = df.dropna(axis=0)
        df = df.reset_index(drop=True)  # 인덱스 재설정
        
        for i in range(len(df)):
            gas_id = df.loc[i, '고유번호']
            region = df.loc[i, '지역']
            name = df.loc[i, '상호']
            address = df.loc[i, '주소']
            brand = df.loc[i, '상표']
            self_type = df.loc[i, '셀프여부']
            premium_gasoline = int(df.loc[i, '고급휘발유'])
            gasoline = int(df.loc[i, '휘발유'])
            diesel = int(df.loc[i, '경유'])
            kerosene = int(df.loc[i, '실내등유'])
            
            try:
                data = [gas_id, region, name, address, brand, self_type, 
                        premium_gasoline, gasoline, diesel, kerosene]
                db.insert_data(data)
            except Exception as e:
                flash(f'데이터 저장 중 오류 발생: {e}')
                return redirect(url_for('upload'))
        flash('데이터가 성공적으로 저장되었습니다.')
        return redirect(url_for('index'))
    return ren('upload.html')

@app.route('/list')
def data_list():
    # URL 파라미터 받기
    sort_by = request.args.get('sort', 'gas_id')
    order = request.args.get('order', 'asc')
    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', '')
    column = request.args.get('column', 'gas_id')
    per_page = 20
    
    # 데이터 조회
    data = db.get_data(sort_by=sort_by, order=order, page=page, per_page=per_page, 
                        keyword=keyword, column=column)
    
    # 전체 페이지 수 계산
    total_count = db.get_total_count(keyword=keyword, column=column, sort_by=sort_by)
    total_pages = (total_count + per_page - 1) // per_page
    
    return ren('list.html', 
                data=data, 
                sort_by=sort_by, 
                order=order, 
                page=page, 
                total_pages=total_pages,
                total_count=total_count,
                keyword=keyword,
                column=column)

@app.route('/analysis')
def analysis():
    # db.py 메서드로 rows 가져오기
    rows = db.get_all_rows()
    
    # rows를 DataFrame으로 변환
    columns = ['고유번호', '지역', '상호', '주소', '상표', '셀프여부', 
                '고급휘발유', '휘발유', '경유', '실내등유']
    df = pd.DataFrame(rows, columns=columns)
    brand_data = {
        "label": df['상표'].unique().tolist(),
        "value": df['상표'].value_counts().tolist(),
    }
    self_type_data = {
        "label": df['셀프여부'].unique().tolist(),
        "value": df['셀프여부'].value_counts().tolist(),
    }
    
    return ren('analysis.html', brand_data=brand_data, self_type_data=self_type_data)

if __name__ == "__main__":
    app.run(debug=True)