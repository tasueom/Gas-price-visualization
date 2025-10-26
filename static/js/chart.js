// 차트 객체 저장 변수
let brandChart = null;
let selfTypeChart = null;
let priceChart = null;

// 파이 차트 표시 함수
function showPieChart() {
    // 검색란 보이기
    const searchForm = document.getElementById('search-form');
    if (searchForm) searchForm.style.display = 'block';
    
    // 차트 컨테이너 전환
    document.getElementById('pie-chart-container').style.display = 'flex';
    document.getElementById('bar-chart-container').style.display = 'none';
    document.getElementById('distribution-chart-container').style.display = 'none';
    
    // hidden input 업데이트
    const chartTypeInput = document.getElementById('chart-type-input');
    if (chartTypeInput) chartTypeInput.value = 'pie';
    
    // 브랜드 차트가 없으면 생성
    if (!brandChart) {
        const brandCtx = document.getElementById('brand-chart').getContext('2d');
        brandChart = new Chart(brandCtx, {
            type: 'pie',
            data: {
                labels: brandData.label,
                datasets: [{
                    label: '브랜드 지점 수',
                    data: brandData.value,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.parsed;
                                const percent = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value}개 (${percent}%)`;
                            }
                        }
                    }
                }
            }
        });
    } else {
        // 차트가 이미 있으면 애니메이션 다시 실행
        brandChart.reset();
        brandChart.update();
    }
    
    // 셀프여부 차트가 없으면 생성
    if (!selfTypeChart) {
        const selfTypeCtx = document.getElementById('self-type-chart').getContext('2d');
        selfTypeChart = new Chart(selfTypeCtx, {
            type: 'pie',
            data: {
                labels: selfTypeData.label,
                datasets: [{
                    label: '지점 수',
                    data: selfTypeData.value,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.parsed;
                                const percent = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value}개 (${percent}%)`;
                            }
                        }
                    }
                }
            }
        });
    } else {
        // 차트가 이미 있으면 애니메이션 다시 실행
        selfTypeChart.reset();
        selfTypeChart.update();
    }
}

// 막대 차트 표시 함수
function showBarChart() {
    // 검색란 보이기
    const searchForm = document.getElementById('search-form');
    if (searchForm) searchForm.style.display = 'block';
    
    // 차트 컨테이너 전환
    document.getElementById('pie-chart-container').style.display = 'none';
    document.getElementById('bar-chart-container').style.display = 'flex';
    document.getElementById('distribution-chart-container').style.display = 'none';
    
    // hidden input 업데이트
    const chartTypeInput = document.getElementById('chart-type-input');
    if (chartTypeInput) chartTypeInput.value = 'bar';
    
    // 차트가 없으면 생성
    if (!priceChart) {
        const priceCtx = document.getElementById('price-chart').getContext('2d');
        priceChart = new Chart(priceCtx, {
            type: 'bar',
            data: {
                labels: priceData.label,
                datasets: [{
                    label: '유가 평균',
                    data: priceData.value,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',   // 고급휘발유 - 빨강
                        'rgba(54, 162, 235, 0.7)',   // 휘발유 - 파랑
                        'rgba(255, 206, 86, 0.7)',   // 경유 - 노랑
                        'rgba(75, 192, 192, 0.7)'    // 실내등유 - 청록
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                return `${context.label}: ${value}원`;
                            }
                        }
                    }
                }
            }
        });
    } else {
        // 차트가 이미 있으면 애니메이션 다시 실행
        priceChart.reset();
        priceChart.update();
    }
}

// 기타 분석 (히스토그램) 표시 함수
function showDistributionChart() {
    // 검색란 숨기기
    const searchForm = document.getElementById('search-form');
    if (searchForm) searchForm.style.display = 'none';
    
    // 다른 차트들 숨기기
    document.getElementById('pie-chart-container').style.display = 'none';
    document.getElementById('bar-chart-container').style.display = 'none';
    
    // 히스토그램 표시
    document.getElementById('distribution-chart-container').style.display = 'flex';
}

// 페이지 로드 시 차트 표시 (URL 파라미터에 따라)
window.addEventListener('DOMContentLoaded', function() {
    if (currentChartType === 'bar') {
        showBarChart();
    } else {
        showPieChart();
    }
});

