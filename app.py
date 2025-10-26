from flask import Flask, render_template as ren, request, redirect, url_for, flash
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI 없이 백그라운드에서 실행
import matplotlib.pyplot as plt
import seaborn as sns
import os
import db

app = Flask(__name__)

app.secret_key = 'secret_key1234'

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

def create_distribution_chart():
    """전국 유가 분포 히스토그램 + KDE 생성"""
    # 전체 데이터 가져오기
    rows = db.get_all_rows()
    columns = ['고유번호', '지역', '상호', '주소', '상표', '셀프여부', 
                '고급휘발유', '휘발유', '경유', '실내등유']
    df = pd.DataFrame(rows, columns=columns)
    
    # 0 제외 (판매하지 않는 유종)
    df = df.replace(0, pd.NA)
    
    # 2x2 서브플롯 생성
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('전국 유가 분포 분석', fontsize=16, fontweight='bold')
    
    fuel_types = [
        ('고급휘발유', 'Premium Gasoline', axes[0, 0]),
        ('휘발유', 'Gasoline', axes[0, 1]),
        ('경유', 'Diesel', axes[1, 0]),
        ('실내등유', 'Kerosene', axes[1, 1])
    ]
    
    colors = ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0']
    
    for i, (fuel_kr, fuel_en, ax) in enumerate(fuel_types):
        data = df[fuel_kr].dropna()
        
        if len(data) > 0:
            # 히스토그램 + KDE
            sns.histplot(data, bins=50, kde=True, color=colors[i], 
                        alpha=0.6, edgecolor='black', ax=ax)
            
            # 통계 정보 추가
            mean_val = data.mean()
            median_val = data.median()
            
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'평균: {mean_val:.0f}원')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'중앙값: {median_val:.0f}원')
            
            ax.set_title(f'{fuel_kr} 가격 분포', fontsize=12, fontweight='bold')
            ax.set_xlabel('가격 (원)', fontsize=10)
            ax.set_ylabel('주유소 수', fontsize=10)
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 이미지 저장
    img_path = os.path.join('static', 'img', 'fuel_distribution.png')
    plt.savefig(img_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return img_path

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
    # URL 파라미터 받기
    keyword = request.args.get('keyword', '')
    column = request.args.get('column', 'gas_id')
    chart_type = request.args.get('chart_type', 'bar')
    
    # 히스토그램 이미지 생성 (없으면 생성)
    img_path = os.path.join('static', 'img', 'fuel_distribution.png')
    if not os.path.exists(img_path):
        create_distribution_chart()
    
    # db.py 메서드로 rows 가져오기 (검색 조건 반영)
    rows = db.get_all_rows(keyword=keyword, column=column)
    
    # rows를 DataFrame으로 변환
    columns = ['고유번호', '지역', '상호', '주소', '상표', '셀프여부', 
                '고급휘발유', '휘발유', '경유', '실내등유']
    df = pd.DataFrame(rows, columns=columns)
    
    # 유가 평균 계산을 위해 0을 결측치로 변환
    df = df.replace(0, pd.NA)
    
    brand_data = {
        "label": df['상표'].unique().tolist(),
        "value": df['상표'].value_counts().tolist(),
    }
    self_type_data = {
        "label": df['셀프여부'].unique().tolist(),
        "value": df['셀프여부'].value_counts().tolist(),
    }
    
    # 유종별 평균 가격
    price_data = {
        "label": ["고급휘발유", "휘발유", "경유", "실내등유"],
        "value": [
            round(df['고급휘발유'].mean(), 2),
            round(df['휘발유'].mean(), 2),
            round(df['경유'].mean(), 2),
            round(df['실내등유'].mean(), 2)
        ]
    }
    
    return ren('analysis.html', 
                keyword=keyword,
                column=column,
                chart_type=chart_type,
                brand_data=brand_data, 
                self_type_data=self_type_data, 
                price_data=price_data)

if __name__ == "__main__":
    app.run(debug=True)