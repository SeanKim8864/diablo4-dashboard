import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title='디아블로 IV 트렌드 대시보드', layout='wide')

dark_mode = st.toggle('다크모드', value=False)
plotly_template = 'plotly_dark' if dark_mode else 'plotly_white'

if dark_mode:
    theme_css = '''
    <style>
    :root {
      --bg: #0b1220;
      --card: #111827;
      --line: #243041;
      --text: #f9fafb;
      --muted: #94a3b8;
      --blue: #60a5fa;
      --red: #fb7185;
      --green: #34d399;
      --navy: #e5eefc;
      --soft-blue: #0f172a;
      --soft-red: #2a1220;
      --soft-green: #0f1f1a;
    }
    .stApp { background: var(--bg); color: var(--text); font-size: 11.2px; }
    .block-container { padding-top: 3.8rem; padding-bottom: 0.5rem; padding-left: 0.85rem; padding-right: 0.85rem; max-width: 96vw; }
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stMetric"] { background: linear-gradient(180deg, #111827 0%, #0f172a 100%); border: 1px solid var(--line); padding: 11px 13px; border-radius: 18px; box-shadow: 0 10px 22px rgba(0,0,0,0.28); }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: var(--muted) !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.36rem !important; font-weight: 700 !important; color: var(--text) !important; }
    h1 { color: var(--text); margin-bottom: 0.08rem; font-size: 1.18rem; font-weight: 700; }
    h2 { color: var(--text); margin-bottom: 0.12rem; font-size: 1.02rem; }
    h3 { color: var(--text); margin-bottom: 0.12rem; font-size: 0.9rem; }
    p, li, label, .stCaption, .stMarkdown { color: var(--text); font-size: 0.78rem; }
    div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; background: var(--card); }
    .small-note { color: var(--muted); font-size: 0.7rem; }
    .section-box { background: linear-gradient(180deg, #111827 0%, #0f172a 100%); border: 1px solid var(--line); border-radius: 18px; padding: 10px 12px 7px 12px; margin: 5px 0 10px 0; box-shadow: 0 10px 24px rgba(0,0,0,0.22); }
    .equal-card { min-height: 104px; }
    .section-label { color: var(--blue); font-size: 0.66rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 2px; }
    div[data-testid="stDataFrame"] [data-testid="stTable"] {
      background: #111827 !important;
      color: #f9fafb !important;
    }
    div[data-testid="stDataFrame"] th {
      background: #0f172a !important;
      color: #e5e7eb !important;
    }
    div[data-testid="stDataFrame"] td {
      background: #111827 !important;
      color: #f9fafb !important;
      border-color: #243041 !important;
    }
    </style>
    '''
    summary_bg = '#0f172a'
    summary_text = '#e5eefc'
else:
    theme_css = '''
    <style>
    :root {
      --bg: #f6f8fb;
      --card: #ffffff;
      --line: #e9eef5;
      --text: #191f28;
      --muted: #8b95a1;
      --blue: #3182f6;
      --red: #f04452;
      --green: #12b886;
      --navy: #243b53;
      --soft-blue: #eaf2ff;
      --soft-red: #fff1f3;
      --soft-green: #ecfdf3;
    }
    .stApp { background: var(--bg); color: var(--text); font-size: 11.2px; }
    .block-container { padding-top: 3.8rem; padding-bottom: 0.5rem; padding-left: 0.85rem; padding-right: 0.85rem; max-width: 96vw; }
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stMetric"] { background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%); border: 1px solid var(--line); padding: 11px 13px; border-radius: 18px; box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05); }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricLabel"] { font-size: 0.72rem !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.36rem !important; font-weight: 700 !important; }
    h1 { color: var(--text); margin-bottom: 0.08rem; font-size: 1.18rem; font-weight: 700; }
    h2 { color: var(--text); margin-bottom: 0.12rem; font-size: 1.02rem; }
    h3 { color: var(--text); margin-bottom: 0.12rem; font-size: 0.9rem; }
    p, li, label, .stCaption, .stMarkdown { color: var(--text); font-size: 0.78rem; }
    div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; background: var(--card); }
    .small-note { color: var(--muted); font-size: 0.7rem; }
    .section-box { background: linear-gradient(180deg, #ffffff 0%, #fcfdff 100%); border: 1px solid var(--line); border-radius: 18px; padding: 10px 12px 7px 12px; margin: 5px 0 10px 0; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04); }
    .equal-card { min-height: 104px; }
    .section-label { color: var(--blue); font-size: 0.66rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 2px; }
    </style>
    '''
    summary_bg = '#f8fbff'
    summary_text = '#243b53'

st.markdown(theme_css, unsafe_allow_html=True)
if dark_mode:
    chart_layout = dict(
        paper_bgcolor='#111827',
        plot_bgcolor='#111827',
        font=dict(color='#f9fafb', size=11),
        xaxis=dict(gridcolor='#243041', zerolinecolor='#243041', linecolor='#243041', tickfont=dict(color='#cbd5e1')),
        yaxis=dict(gridcolor='#243041', zerolinecolor='#243041', linecolor='#243041', tickfont=dict(color='#cbd5e1')),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#e5e7eb')),
    )
else:
    chart_layout = dict(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(color='#191f28', size=11),
        xaxis=dict(gridcolor='#e5e7eb', zerolinecolor='#e5e7eb', linecolor='#d1d5db', tickfont=dict(color='#4b5563')),
        yaxis=dict(gridcolor='#e5e7eb', zerolinecolor='#e5e7eb', linecolor='#d1d5db', tickfont=dict(color='#4b5563')),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#374151')),
    )

header_left, header_right = st.columns([0.84, 0.16])
with header_left:
    st.title('디아블로 IV 트렌드 대시보드')
    st.caption('데이터 소스: Steam + Reddit | 공개 데이터만 사용 | 관측값과 추정값 분리 표기')
with header_right:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.caption('테마')
    st.write('다크' if dark_mode else '라이트')
st.markdown(f"<div class='section-box' style='padding:10px 14px;margin-top:4px;margin-bottom:12px;background:{summary_bg}'><span class='section-label' style='display:block;margin-bottom:4px'>EXECUTIVE SUMMARY</span><div style='font-size:0.88rem;color:{summary_text};line-height:1.45'>최근 14일 기준 Steam 리뷰와 Reddit 토론을 통합해 긍정/부정 흐름, 주요 이슈, 플레이타임별 만족도 차이를 한 화면에서 보는 요약 대시보드입니다.</div></div>", unsafe_allow_html=True)


def safe_read_csv(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def normalize_sentiment_label(x):
    if pd.isna(x):
        return '중립'
    x = str(x).lower().strip()
    if x in ['positive', 'pos', 'good', 'recommended', '긍정']:
        return '긍정'
    if x in ['negative', 'neg', 'bad', 'not_recommended', '부정']:
        return '부정'
    return '중립'


def sentiment_to_score(label: str) -> int:
    return 1 if label == '긍정' else -1 if label == '부정' else 0


def estimate_country(row):
    if pd.notna(row.get('country')) and str(row.get('country')).strip() != '':
        return row['country']
    lang = str(row.get('language', '')).lower()
    mapping = {
        'english': '미국/영국/영어권',
        'en': '미국/영국/영어권',
        'korean': '대한민국',
        'ko': '대한민국',
        'german': '독일',
        'de': '독일',
        'french': '프랑스',
        'fr': '프랑스',
        'spanish': '스페인/중남미',
        'es': '스페인/중남미',
        'japanese': '일본',
        'ja': '일본',
    }
    return mapping.get(lang, '미상')


def estimate_country_confidence(row):
    if pd.notna(row.get('country')) and str(row.get('country')).strip() != '':
        return '높음'
    if pd.notna(row.get('language')) and str(row.get('language')).strip() != '':
        return '낮음'
    return '낮음'


def playtime_bucket(hours):
    if pd.isna(hours):
        return '미상'
    if hours < 10:
        return '10시간 미만'
    if hours < 50:
        return '10~50시간'
    if hours < 100:
        return '50~100시간'
    if hours < 300:
        return '100~300시간'
    return '300시간 이상'


def localize_topic(topic):
    mapping = {
        'general': '일반 의견',
        'loot': '전리품',
        'balance': '밸런스',
        'season content': '시즌 콘텐츠',
        'progression': '성장',
        'build diversity': '빌드 다양성',
        'bugs': '버그',
        'performance': '성능',
        'rewards': '보상',
        'endgame': '엔드게임',
        'monetization': '과금',
    }
    return mapping.get(str(topic).strip().lower(), topic)


def render_topic_summary_table(df: pd.DataFrame, dark_mode: bool):
    if df.empty:
        st.info('토픽 데이터 없음')
        return
    table = df[['topic', 'frequency', 'avg_sentiment', 'trend_direction']].head(8).copy()
    table['topic'] = table['topic'].apply(localize_topic)
    table['avg_sentiment'] = table['avg_sentiment'].map(lambda x: f'{x:.3f}')
    table.columns = ['토픽', '빈도', '평균 감성', '추세']
    bg = '#111827' if dark_mode else '#ffffff'
    head = '#0f172a' if dark_mode else '#f8fafc'
    text = '#f9fafb' if dark_mode else '#191f28'
    muted = '#cbd5e1' if dark_mode else '#475569'
    border = '#243041' if dark_mode else '#e5e7eb'
    rows = ''.join([
        '<tr>' + ''.join([f"<td style=\'padding:10px 12px;border-bottom:1px solid {border};color:{text};font-size:12px\'>{val}</td>" for val in row]) + '</tr>'
        for row in table.itertuples(index=False, name=None)
    ])
    html = f"""
    <div style='border:1px solid {border};border-radius:14px;overflow:hidden;background:{bg}'>
      <table style='width:100%;border-collapse:collapse'>
        <thead>
          <tr style='background:{head}'>
            <th style='text-align:left;padding:10px 12px;color:{muted};font-size:12px;border-bottom:1px solid {border}'>토픽</th>
            <th style='text-align:left;padding:10px 12px;color:{muted};font-size:12px;border-bottom:1px solid {border}'>빈도</th>
            <th style='text-align:left;padding:10px 12px;color:{muted};font-size:12px;border-bottom:1px solid {border}'>평균 감성</th>
            <th style='text-align:left;padding:10px 12px;color:{muted};font-size:12px;border-bottom:1px solid {border}'>추세</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


steam = safe_read_csv('data/steam_reviews.csv')
reddit_posts = safe_read_csv('data/reddit_posts.csv')
reddit_comments = safe_read_csv('data/reddit_comments.csv')

if steam.empty:
    steam = pd.DataFrame({
        'review_id': [1, 2, 3, 4, 5, 6],
        'timestamp': pd.date_range(end=datetime.today(), periods=6).astype(str),
        'sentiment': ['positive', 'negative', 'negative', 'positive', 'neutral', 'positive'],
        'language': ['english', 'korean', 'english', 'german', 'english', 'japanese'],
        'country': [None, None, 'US', None, 'UK', None],
        'playtime_hours': [5, 25, 80, 140, 350, 45],
        'helpful_votes': [11, 4, 9, 15, 23, 6],
        'recommendation': ['recommended', 'not_recommended', 'not_recommended', 'recommended', 'recommended', 'recommended'],
        'source': ['Steam'] * 6,
    })

if reddit_posts.empty:
    reddit_posts = pd.DataFrame({
        'post_id': [101, 102, 103, 104],
        'timestamp': pd.date_range(end=datetime.today(), periods=4).astype(str),
        'sentiment': ['negative', 'positive', 'negative', 'neutral'],
        'language': ['english', 'english', 'korean', 'english'],
        'country': [None, None, None, None],
        'score': [120, 90, 55, 20],
        'comment_count': [45, 30, 12, 5],
        'topic': ['밸런스', '전리품', '성능', '엔드게임'],
        'source': ['Reddit'] * 4,
    })

if reddit_comments.empty:
    reddit_comments = pd.DataFrame({
        'comment_id': [201, 202, 203, 204, 205],
        'timestamp': pd.date_range(end=datetime.today(), periods=5).astype(str),
        'sentiment': ['negative', 'negative', 'positive', 'neutral', 'negative'],
        'language': ['english', 'english', 'korean', 'english', 'japanese'],
        'country': [None, None, None, None, None],
        'score': [10, 7, 5, 2, 3],
        'topic': ['밸런스', '버그', '보상', '빌드 다양성', '성능'],
        'source': ['Reddit'] * 5,
    })

for df in [steam, reddit_posts, reddit_comments]:
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True).dt.tz_convert(None)
    df['sentiment'] = df['sentiment'].apply(normalize_sentiment_label)
    df['sentiment_score'] = df['sentiment'].apply(sentiment_to_score)
    df['country_estimated'] = df.apply(estimate_country, axis=1)
    df['country_confidence'] = df.apply(estimate_country_confidence, axis=1)

steam['playtime_bucket'] = steam['playtime_hours'].apply(playtime_bucket)
reddit_posts['discussion_type'] = '게시글'
reddit_comments['discussion_type'] = '댓글'
reddit = pd.concat([reddit_posts, reddit_comments], ignore_index=True, sort=False)

selected_source = '통합'
today = datetime.today()
default_start = today - timedelta(days=14)
start_date = pd.to_datetime(default_start.date())
end_date = pd.to_datetime(today.date()) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
selected_country = '전체'
selected_sentiment = '전체'
selected_playtime = '전체'
selected_topic = '전체'

steam_f = steam[(steam['timestamp'] >= start_date) & (steam['timestamp'] <= end_date)].copy()
reddit_f = reddit[(reddit['timestamp'] >= start_date) & (reddit['timestamp'] <= end_date)].copy()

if selected_country != '전체':
    steam_f = steam_f[steam_f['country_estimated'] == selected_country]
    reddit_f = reddit_f[reddit_f['country_estimated'] == selected_country]
if selected_sentiment != '전체':
    steam_f = steam_f[steam_f['sentiment'] == selected_sentiment]
    reddit_f = reddit_f[reddit_f['sentiment'] == selected_sentiment]
if selected_playtime != '전체':
    steam_f = steam_f[steam_f['playtime_bucket'] == selected_playtime]
if selected_topic != '전체' and 'topic' in reddit_f.columns:
    reddit_f = reddit_f[reddit_f['topic'] == selected_topic]

combined_df = steam_f.copy() if selected_source == 'Steam' else reddit_f.copy() if selected_source == 'Reddit' else pd.concat([steam_f, reddit_f], ignore_index=True, sort=False)

total_mentions = len(combined_df)
positive_mentions = len(combined_df[combined_df['sentiment'] == '긍정'])
negative_mentions = len(combined_df[combined_df['sentiment'] == '부정'])
satisfaction_rate = (positive_mentions / total_mentions * 100) if total_mentions else 0
negative_rate = (negative_mentions / total_mentions * 100) if total_mentions else 0
avg_sentiment = combined_df['sentiment_score'].mean() if total_mentions else 0
topic_growth = '없음'
if 'topic' in reddit_f.columns and not reddit_f.empty:
    topic_growth = localize_topic(reddit_f['topic'].value_counts().index[0])

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric('전체 언급량', f'{total_mentions:,}')
k2.metric('긍정 비율', f'{satisfaction_rate:.1f}%')
k3.metric('부정 비율', f'{negative_rate:.1f}%')
k4.metric('긍부정 격차', f'{(satisfaction_rate - negative_rate):.1f}%p')
k5.metric('주요 이슈', topic_growth if topic_growth != '없음' else '일반 의견')

top_left, top_right = st.columns([1, 1], gap='large')

with top_left:
    st.markdown("<div class='section-box equal-card'><div class='section-label'>Overview</div><h3>핵심 인사이트</h3><div class='small-note'>핵심만 짧게 요약</div></div>", unsafe_allow_html=True)
    for text in [
        f'긍정 비율은 **{satisfaction_rate:.1f}%**.',
        f'부정 비율은 **{negative_rate:.1f}%**.',
        f'주요 이슈는 **{topic_growth if topic_growth != "없음" else "일반 의견"}**.',
    ]:
        st.markdown(f'- {text}')

with top_right:
    st.markdown("<div class='section-box equal-card'><div class='section-label'>Actions</div><h3>추천 액션</h3><div class='small-note'>바로 실행할 포인트</div></div>", unsafe_allow_html=True)
    for text in [
        '부정 이슈 우선 점검',
        '플레이타임별 불만 구간 확인',
        'Reddit 급증 토픽 조기 모니터링',
    ]:
        st.markdown(f'- {text}')

country_frames = []
if selected_source in ['통합', 'Steam'] and not steam_f.empty:
    steam_country = steam_f.groupby('country_estimated').agg(sample_size=('review_id', 'count'), positive=('sentiment', lambda x: (x == '긍정').sum()), confidence=('country_confidence', lambda x: x.mode().iloc[0] if len(x.mode()) else '낮음')).reset_index()
    steam_country['satisfaction_rate'] = steam_country['positive'] / steam_country['sample_size'] * 100
    steam_country['source'] = 'Steam'
    country_frames.append(steam_country)
if selected_source in ['통합', 'Reddit'] and not reddit_f.empty:
    reddit_country = reddit_f.groupby('country_estimated').agg(sample_size=('sentiment', 'count'), positive=('sentiment', lambda x: (x == '긍정').sum()), confidence=('country_confidence', lambda x: x.mode().iloc[0] if len(x.mode()) else '낮음')).reset_index()
    reddit_country['satisfaction_rate'] = reddit_country['positive'] / reddit_country['sample_size'] * 100
    reddit_country['source'] = 'Reddit'
    country_frames.append(reddit_country)


def daily_counts(df, label):
    if df.empty:
        return pd.DataFrame(columns=['date', label])
    out = df.copy()
    out['date'] = out['timestamp'].dt.date
    return out.groupby('date').size().reset_index(name=label)

steam_daily = daily_counts(steam_f, 'steam_review_volume')
reddit_daily = daily_counts(reddit_f, 'reddit_discussion_volume')
if not combined_df.empty:
    tmp = combined_df.copy()
    tmp['date'] = tmp['timestamp'].dt.date
    sentiment_daily = tmp.groupby('date')['sentiment_score'].mean().reset_index(name='sentiment_score')
else:
    sentiment_daily = pd.DataFrame(columns=['date', 'sentiment_score'])
trend_df = pd.DataFrame({'date': pd.date_range(start=start_date, end=end_date, freq='D').date})
for piece in [steam_daily, reddit_daily, sentiment_daily]:
    trend_df = trend_df.merge(piece, on='date', how='left')
trend_df = trend_df.fillna(0)

if 'topic' in reddit_f.columns and not reddit_f.empty:
    topic_table = reddit_f.groupby('topic').agg(frequency=('topic', 'count'), avg_sentiment=('sentiment_score', 'mean'), engagement=('score', 'mean')).reset_index().sort_values('frequency', ascending=False)
    q75 = topic_table['frequency'].quantile(0.75)
    q25 = topic_table['frequency'].quantile(0.25)
    topic_table['trend_direction'] = topic_table['frequency'].apply(lambda f: '상승' if f >= q75 else '하락' if f <= q25 else '유지')
else:
    topic_table = pd.DataFrame(columns=['topic', 'frequency', 'avg_sentiment', 'engagement', 'trend_direction'])

if not steam_f.empty:
    playtime_df = steam_f.groupby('playtime_bucket').agg(sample_size=('review_id', 'count'), positive=('sentiment', lambda x: (x == '긍정').sum())).reset_index()
    playtime_df['satisfaction_rate'] = playtime_df['positive'] / playtime_df['sample_size'] * 100
else:
    playtime_df = pd.DataFrame(columns=['playtime_bucket', 'sample_size', 'positive', 'satisfaction_rate'])

row1_left, row1_right = st.columns([1.0, 1.0], gap='large')
with row1_left:
    st.markdown("<div class='section-box'><div class='section-label'>Country</div><h3>주요 국가별 만족도</h3>", unsafe_allow_html=True)
    if country_frames:
        country_df = pd.concat(country_frames, ignore_index=True).sort_values('sample_size', ascending=False).head(10)
        fig_country = px.bar(country_df, x='satisfaction_rate', y='country_estimated', color='source', orientation='h', text='sample_size', title=None, height=345, custom_data=['sample_size', 'confidence'], color_discrete_map={'Steam':'#3182f6','Reddit':'#f04452'}, template=plotly_template)
        fig_country.update_layout(margin=dict(l=10, r=10, t=10, b=10), yaxis_title='국가', xaxis_title='만족도(%)', legend_title='소스', **chart_layout)
        fig_country.update_traces(hovertemplate='국가: %{y}<br>만족도: %{x:.1f}%<br>소스: %{fullData.name}<br>표본 수: %{customdata[0]}<br>신뢰도: %{customdata[1]}<extra></extra>')
        st.plotly_chart(fig_country, width='stretch')
    else:
        st.info('국가별 데이터 없음')
    st.markdown("<div class='small-note'>국가 정보는 직접 관측되지 않는 경우 공개 메타데이터와 언어 신호를 바탕으로 추정됩니다.</div></div>", unsafe_allow_html=True)

with row1_right:
    st.markdown("<div class='section-box'><div class='section-label'>Behavior</div><h3>최근 14일 이용 행태</h3>", unsafe_allow_html=True)
    fig_vol = px.line(trend_df, x='date', y=['steam_review_volume', 'reddit_discussion_volume'], height=345, color_discrete_sequence=['#3182f6','#f04452'], template=plotly_template)
    fig_vol.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title='날짜', yaxis_title='건수', legend_title='지표', **chart_layout)
    fig_vol.for_each_trace(lambda t: t.update(name='Steam 리뷰 수' if t.name == 'steam_review_volume' else 'Reddit 토론 수'))
    fig_vol.update_traces(hovertemplate='날짜: %{x}<br>%{fullData.name}: %{y:.0f}건<extra></extra>')
    st.plotly_chart(fig_vol, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

row2_left, row2_mid, row2_right = st.columns([1.0, 1.0, 0.95], gap='large')
with row2_left:
    st.markdown("<div class='section-box'><div class='section-label'>Sentiment</div><h3>긍정/부정 추이</h3>", unsafe_allow_html=True)
    sentiment_share_df = pd.DataFrame({'date': trend_df['date']})
    if not combined_df.empty:
        tmp2 = combined_df.copy()
        tmp2['date'] = tmp2['timestamp'].dt.date
        pos_daily = tmp2.groupby('date')['sentiment'].apply(lambda x: (x == '긍정').mean() * 100).reset_index(name='긍정 비율')
        neg_daily = tmp2.groupby('date')['sentiment'].apply(lambda x: (x == '부정').mean() * 100).reset_index(name='부정 비율')
        sentiment_share_df = sentiment_share_df.merge(pos_daily, on='date', how='left').merge(neg_daily, on='date', how='left').fillna(0)
    else:
        sentiment_share_df['긍정 비율'] = 0
        sentiment_share_df['부정 비율'] = 0
    fig_sent = px.line(sentiment_share_df, x='date', y=['긍정 비율', '부정 비율'], height=295, color_discrete_sequence=['#12b886','#f04452'], template=plotly_template)
    fig_sent.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title='날짜', yaxis_title='비율(%)', legend_title='지표', **chart_layout)
    fig_sent.update_traces(hovertemplate='날짜: %{x}<br>%{fullData.name}: %{y:.1f}%<extra></extra>')
    st.plotly_chart(fig_sent, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

with row2_mid:
    st.markdown("<div class='section-box'><div class='section-label'>Playtime</div><h3>플레이타임별 만족도</h3>", unsafe_allow_html=True)
    if not playtime_df.empty:
        fig_play = px.bar(playtime_df, x='playtime_bucket', y='satisfaction_rate', text='sample_size', height=295, custom_data=['sample_size', 'positive'], color_discrete_sequence=['#3182f6'], template=plotly_template)
        fig_play.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title='플레이타임 구간', yaxis_title='만족도(%)', **chart_layout)
        fig_play.update_traces(hovertemplate='플레이타임: %{x}<br>만족도: %{y:.1f}%<br>표본 수: %{customdata[0]}<br>긍정 수: %{customdata[1]}<extra></extra>')
        st.plotly_chart(fig_play, width='stretch')
    else:
        st.info('플레이타임 데이터 없음')
    st.markdown('</div>', unsafe_allow_html=True)

with row2_right:
    st.markdown("<div class='section-box'><div class='section-label'>Topics</div><h3>핵심 토픽 요약</h3>", unsafe_allow_html=True)
    if not topic_table.empty:
        render_topic_summary_table(topic_table, dark_mode)
    else:
        st.info('토픽 데이터 없음')
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div class='section-box'><div class='section-label'>Topic Detail</div><h3>토픽 트렌드 상세</h3>", unsafe_allow_html=True)
if not topic_table.empty:
    detail_left, detail_right = st.columns([1.0, 1.0], gap='large')
    with detail_left:
        topic_chart = topic_table.head(10).copy()
        topic_chart['topic'] = topic_chart['topic'].apply(localize_topic)
        fig_topic_freq = px.bar(topic_chart, x='topic', y='frequency', color='avg_sentiment', title=None, height=265, custom_data=['avg_sentiment', 'engagement', 'trend_direction'], template=plotly_template)
        fig_topic_freq.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title='토픽', yaxis_title='빈도', **chart_layout)
        fig_topic_freq.update_traces(hovertemplate='토픽: %{x}<br>빈도: %{y}<br>평균 감성: %{customdata[0]:.2f}<br>평균 참여도: %{customdata[1]:.1f}<br>추세: %{customdata[2]}<extra></extra>')
        st.plotly_chart(fig_topic_freq, width='stretch')
    with detail_right:
        fig_topic_sent = px.bar(topic_chart, x='topic', y='avg_sentiment', color='trend_direction', title=None, height=265, custom_data=['frequency', 'engagement'], template=plotly_template)
        fig_topic_sent.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title='토픽', yaxis_title='평균 감성', **chart_layout)
        fig_topic_sent.update_traces(hovertemplate='토픽: %{x}<br>평균 감성: %{y:.2f}<br>추세: %{fullData.name}<br>빈도: %{customdata[0]}<br>평균 참여도: %{customdata[1]:.1f}<extra></extra>')
        st.plotly_chart(fig_topic_sent, width='stretch')
else:
    st.info('토픽 데이터가 아직 충분하지 않아 키워드 트렌드를 표시할 수 없습니다.')
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('## 방법론')
st.markdown('''
- **긍정/부정 분류**: 현재 MVP는 각 항목을 긍정 / 중립 / 부정으로 단순 분류해 사용합니다.
- **긍정 비율**: 전체 항목 중 긍정으로 분류된 항목 비중입니다.
- **부정 비율**: 전체 항목 중 부정으로 분류된 항목 비중입니다.
- **키워드/토픽 추출**: 현재 MVP는 사전 분류된 토픽 필드를 사용하며, 이후 n-gram 및 클러스터링으로 고도화할 수 있습니다.
- **국가 추정 로직**: 국가가 직접 관측되지 않는 경우 공개 메타데이터와 언어 신호를 기반으로 추정합니다.
- **데이터 한계**: Steam과 Reddit은 전체 디아블로 IV 유저를 완전히 대표하지 않으며, 국가 값은 일부 추정치이고, 통합 참여도는 방향성 참고용입니다.
''')
