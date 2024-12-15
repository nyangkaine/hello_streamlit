import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit 앱 제목
st.title("보험 DB 분석 streamlit 웹")  # 웹 애플리케이션의 제목을 설정합니다.

# CSV 파일 경로
cust_file_path = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/BGCON_CUST_DATA1_proceessed.csv"
claim_file_path = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/BGCON_CLAIM_DATA1_proceessed.csv"
cntt_file_path = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/BGCON_CNTT_DATA1_DUP_DELETE_proceessed.csv"

# 데이터 로드 함수
@st.cache_data
def load_data(file_path):
    """
    CSV 파일 경로를 입력받아 Pandas 데이터프레임으로 로드합니다.
    캐싱을 통해 데이터 로드 시간을 줄입니다.
    """
    try:
        data = pd.read_csv(file_path)  # CSV 파일 읽기
        return data
    except Exception as e:
        st.error(f"파일을 불러오는 중 오류가 발생했습니다: {e}")  # 파일 로드 오류 메시지 출력
        return None

# 데이터 불러오기
cust_data = load_data(cust_file_path)  # CUST 데이터 로드
claim_data = load_data(claim_file_path)  # CLAIM 데이터 로드
cntt_data = load_data(cntt_file_path)  # CNTT 데이터 로드

# 모든 데이터셋이 로드되었는지 확인
if cust_data is not None and claim_data is not None and cntt_data is not None:
    # 데이터셋 선택
    st.subheader("데이터셋 선택 및 미리보기")  # 사용자에게 데이터셋을 선택하도록 옵션 제공
    dataset_choice = st.selectbox(
        "어느 데이터셋을 분석하시겠습니까?",  # 데이터셋 선택 옵션
        ["CUST 데이터", "CLAIM 데이터", "CNTT 데이터"],  # 선택 가능한 데이터셋
        key="dataset_choice"
    )

    # 선택된 데이터셋에 따라 데이터 설정
    if dataset_choice == "CUST 데이터":
        data = cust_data
        numeric_columns = cust_data.select_dtypes(include=['float64', 'int64']).columns.tolist()  # 숫자형 컬럼
        categorical_columns = cust_data.select_dtypes(include=['object']).columns.tolist()  # 범주형 컬럼
    elif dataset_choice == "CLAIM 데이터":
        data = claim_data
        numeric_columns = claim_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        categorical_columns = claim_data.select_dtypes(include=['object']).columns.tolist()
    else:  # CNTT 데이터
        data = cntt_data
        numeric_columns = cntt_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        categorical_columns = cntt_data.select_dtypes(include=['object']).columns.tolist()

    # 데이터 미리보기
    st.write(f"**{dataset_choice} 미리보기:**")
    st.dataframe(data.head())  # 데이터프레임의 상위 5개 데이터 출력

    # 기초 통계 분석
    st.subheader("기초 통계 분석")
    if numeric_columns:
        st.write(data[numeric_columns].describe())  # 숫자형 데이터의 통계 정보 출력
    else:
        st.write("숫자형 컬럼이 없습니다.")  # 숫자형 데이터가 없을 경우 메시지 표시

    # 시각화
    st.subheader("시각화")
    chart_type = st.selectbox(
        "시각화 유형 선택",
        ["히스토그램", "상관관계 히트맵", "박스 플롯"],
        key="chart_type_all_data"
    )

    if chart_type == "히스토그램":
        # 히스토그램 시각화
        column = st.selectbox(
            "히스토그램을 그릴 컬럼 선택",
            numeric_columns,
            key="hist_column_all_data"
        )
        bins = st.slider("구간 수 선택 (bins)", min_value=5, max_value=50, value=20, key="bins_all_data")
        fig, ax = plt.subplots()
        ax.hist(data[column], bins=bins, color='skyblue', edgecolor='black')  # 히스토그램 생성
        ax.set_title(f"{column} 히스토그램")
        ax.set_xlabel(column)
        ax.set_ylabel("빈도")
        st.pyplot(fig)  # 시각화 출력

    elif chart_type == "상관관계 히트맵":
        # 상관관계 히트맵
        corr = data[numeric_columns].corr()  # 숫자형 데이터 간의 상관관계 계산
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)  # 히트맵 시각화
        ax.set_title("상관관계 히트맵")
        st.pyplot(fig)

    elif chart_type == "박스 플롯":
        # 박스 플롯 시각화
        column = st.selectbox(
            "박스 플롯을 그릴 컬럼 선택",
            numeric_columns,
            key="boxplot_column_all_data"
        )
        fig, ax = plt.subplots()
        sns.boxplot(y=data[column], ax=ax, color='lightblue')  # 박스 플롯 생성
        ax.set_title(f"{column} 박스 플롯")
        st.pyplot(fig)

    # 그룹별 데이터 분석
    st.subheader("그룹별 데이터 분석")
    if categorical_columns:
        # 범주형 데이터를 기준으로 그룹화
        group_col = st.selectbox(
            "그룹화 기준 컬럼 선택",
            categorical_columns,
            key="group_col_all_data"
        )
        agg_col = st.selectbox(
            "분석할 숫자형 컬럼 선택",
            numeric_columns,
            key="agg_col_all_data"
        )
        if st.button("그룹화 데이터 보기", key="group_button_all_data"):
            grouped_data = data.groupby(group_col)[agg_col].mean().reset_index()  # 그룹별 평균 계산
            st.write(grouped_data)
            fig, ax = plt.subplots()
            sns.barplot(data=grouped_data, x=group_col, y=agg_col, ax=ax, palette="viridis")  # 막대 그래프 생성
            ax.set_title(f"{group_col}별 {agg_col} 평균")
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            st.pyplot(fig)  # 시각화 출력
    else:
        st.write("범주형 컬럼이 없습니다.")  # 범주형 데이터가 없을 경우 메시지 표시

else:
    st.error("하나 이상의 데이터셋을 불러오지 못했습니다. 파일 경로를 확인하세요.")  # 데이터 로드 실패 메시지
