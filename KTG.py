import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# Настройка страницы Streamlit
st.set_page_config(
    page_title="Расчет КТГ для горных предприятий",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Функция для расчета КТГ
def calculate_ktg(ktg_zakl: float, t_vosst_sist: float, t_vosst_nov_ishod: float) -> float:
    """
    Расчет КТГ после внедрения системы обслуживания РВД
    """
    if t_vosst_nov_ishod <= 0:
        raise ValueError("Исходное время восстановления должно быть больше 0")
    
    if not (0.01 <= ktg_zakl <= 1):
        raise ValueError("КТГ закладываемый должен быть в диапазоне от 0.01 до 1")
    
    # Расчет КТГ по формуле
    ktg_result = ktg_zakl * (t_vosst_sist / t_vosst_nov_ishod)
    
    # Ограничиваем КТГ диапазоном [0.01, 1]
    ktg_result = max(0.01, min(1, ktg_result))
    
    return ktg_result

# Создаем боковую панель для ввода параметров
with st.sidebar:
    st.title("⛏️ Параметры расчета")
    st.markdown("---")
    
    # Ввод КТГ_закл с использованием слайдера и числового поля
    st.subheader("1. КТГ_закл")
    ktg_zakl = st.slider(
        "КТГ закладываемый (в долях от 1)",
        min_value=0.01,
        max_value=1.0,
        value=0.05,
        step=0.01,
        help="Текущий коэффициент технической готовности"
    )
    
    # Ввод T_восст_сист
    st.subheader("2. T_восст_сист")
    t_vosst_sist = st.number_input(
        "Время восстановления после внедрения (часы)",
        min_value=0.1,
        max_value=48.0,
        value=2.0,
        step=0.5,
        help="Планируемое время восстановления после внедрения системы обслуживания"
    )
    
    # Диапазон для T_восст_нов_исход
    st.subheader("3. Диапазон анализа")
    t_min = st.number_input("Минимальное время восстановления (ч)", 
                           min_value=1, max_value=48, value=4, step=1)
    t_max = st.number_input("Максимальное время восстановления (ч)", 
                           min_value=1, max_value=48, value=24, step=1)
    
    st.markdown("---")
    
    # Кнопка для расчета
    calculate_button = st.button("🚀 Рассчитать КТГ", type="primary", use_container_width=True)
    st.markdown("---")
    
    # Информация о формуле
    st.subheader("📊 Формула расчета")
    st.latex(r"КТГ = КТГ_{закл} \times \frac{T_{восст.сист}}{T_{восст.нов.исход}}")
    st.markdown("---")
    
    # Быстрые настройки
    st.subheader("⚡ Быстрые настройки")
    preset_col1, preset_col2 = st.columns(2)
    
    with preset_col1:
        if st.button("Оптимистичный", use_container_width=True):
            st.session_state.ktg_zakl = 0.05
            st.session_state.t_vosst_sist = 1.5
            st.rerun()
    
    with preset_col2:
        if st.button("Реалистичный", use_container_width=True):
            st.session_state.ktg_zakl = 0.05
            st.session_state.t_vosst_sist = 2.0
            st.rerun()

# Основной контент
st.title("⛏️ Расчет КТГ после внедрения системы обслуживания РВД")
st.markdown("**КТГ** - Коэффициент Технической Готовности оборудования горных предприятий")
st.markdown("---")

# Инициализация состояния сессии
if 'ktg_zakl' not in st.session_state:
    st.session_state.ktg_zakl = 0.05
if 't_vosst_sist' not in st.session_state:
    st.session_state.t_vosst_sist = 2.0

# Используем значения из сессии
ktg_zakl = st.session_state.get('ktg_zakl', 0.05)
t_vosst_sist = st.session_state.get('t_vosst_sist', 2.0)

# Создаем вкладки
tab1, tab2, tab3, tab4 = st.tabs(["📈 График", "📊 Таблица данных", "📋 Анализ", "📥 Экспорт"])

# Функция для создания данных
def generate_data(ktg_zakl, t_vosst_sist, t_min, t_max):
    """Генерирует данные для анализа"""
    t_vosst_range = np.arange(t_min, t_max + 0.5, 0.5)
    ktg_values = [calculate_ktg(ktg_zakl, t_vosst_sist, t) for t in t_vosst_range]
    ktg_change_percent = [(ktg - ktg_zakl) / ktg_zakl * 100 for ktg in ktg_values]
    
    return t_vosst_range, ktg_values, ktg_change_percent

# Генерируем данные
t_vosst_range, ktg_values, ktg_change_percent = generate_data(ktg_zakl, t_vosst_sist, t_min, t_max)

# Вкладка 1: График
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Создаем интерактивный график с Plotly
        fig = go.Figure()
        
        # Основной график КТГ
        fig.add_trace(go.Scatter(
            x=t_vosst_range,
            y=ktg_values,
            mode='lines',
            name=f'КТГ (T_восст_сист = {t_vosst_sist} ч)',
            line=dict(color='blue', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 0, 255, 0.1)'
        ))
        
        # Линия КТГ = 1
        fig.add_hline(
            y=1,
            line_dash="dash",
            line_color="red",
            annotation_text="КТГ = 1 (максимум)",
            annotation_position="bottom right"
        )
        
        # Линия исходного КТГ
        fig.add_hline(
            y=ktg_zakl,
            line_dash="dash",
            line_color="green",
            annotation_text=f"КТГ_закл = {ktg_zakl}",
            annotation_position="top right"
        )
        
        # Настройки графика
        fig.update_layout(
            title=f'Зависимость КТГ от времени восстановления<br>КТГ_закл = {ktg_zakl}, T_восст_сист = {t_vosst_sist} ч',
            xaxis_title='T_восст_нов_исход, ч',
            yaxis_title='КТГ',
            hovermode='x unified',
            height=600,
            template='plotly_white',
            showlegend=True
        )
        
        fig.update_xaxes(range=[t_min, t_max])
        fig.update_yaxes(range=[0, 1.05])
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Ключевые метрики
        st.metric("КТГ_закл", f"{ktg_zakl:.3f}")
        st.metric("T_восст_сист", f"{t_vosst_sist:.1f} ч")
        
        # Текущие значения КТГ
        st.subheader("📌 Ключевые точки")
        
        key_points = [4, 8, 12, 16, 20, 24]
        for t in key_points:
            if t_min <= t <= t_max:
                idx = np.abs(t_vosst_range - t).argmin()
                ktg = ktg_values[idx]
                change = (ktg - ktg_zakl) / ktg_zakl * 100
                
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**{t} ч:**")
                with col_b:
                    st.markdown(f"`{ktg:.3f}`")
        
        # Индикатор эффективности
        st.subheader("📊 Эффективность")
        
        ktg_max = max(ktg_values)
        improvement = ((ktg_max - ktg_zakl) / ktg_zakl * 100) if ktg_zakl > 0 else 0
        
        if improvement > 50:
            st.success(f"Высокая эффективность: +{improvement:.1f}%")
        elif improvement > 20:
            st.info(f"Средняя эффективность: +{improvement:.1f}%")
        else:
            st.warning(f"Низкая эффективность: +{improvement:.1f}%")

# Вкладка 2: Таблица данных
with tab2:
    # Создаем DataFrame с данными
    data = {
        'T_восст_нов_исход (ч)': t_vosst_range,
        'КТГ': ktg_values,
        'Изменение КТГ, %': ktg_change_percent,
        'Статус': ['Улучшение' if x >= 0 else 'Ухудшение' for x in ktg_change_percent]
    }
    
    df = pd.DataFrame(data)
    df['КТГ'] = df['КТГ'].round(3)
    df['Изменение КТГ, %'] = df['Изменение КТГ, %'].round(2)
    
    # Отображаем таблицу
    st.subheader("📋 Таблица расчета КТГ")
    
    # Фильтры для таблицы
    col1, col2 = st.columns(2)
    with col1:
        show_rows = st.slider("Количество строк", 10, 100, 20)
    with col2:
        status_filter = st.multiselect(
            "Фильтр по статусу",
            ['Улучшение', 'Ухудшение'],
            default=['Улучшение', 'Ухудшение']
        )
    
    # Фильтрация данных
    filtered_df = df[df['Статус'].isin(status_filter)].head(show_rows)
    
    # Форматирование таблицы
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'КТГ': st.column_config.NumberColumn(
                format="%.3f"
            ),
            'Изменение КТГ, %': st.column_config.NumberColumn(
                format="%.2f",
                help="Изменение относительно КТГ_закл"
            ),
            'Статус': st.column_config.TextColumn(
                help="Улучшение или ухудшение КТГ"
            )
        }
    )
    
    # Статистика
    st.subheader("📊 Статистика")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Средний КТГ", f"{df['КТГ'].mean():.3f}")
    with col2:
        st.metric("Максимальный КТГ", f"{df['КТГ'].max():.3f}")
    with col3:
        st.metric("Минимальный КТГ", f"{df['КТГ'].min():.3f}")

# Вкладка 3: Анализ
with tab3:
    st.header("📊 Детальный анализ эффективности")
    
    # Анализ эффективности
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Анализ КТГ")
        
        # Находим точку, где КТГ достигает 1
        ktg_array = np.array(ktg_values)
        ktg_reaches_1 = any(ktg_array >= 0.999)
        
        if ktg_reaches_1:
            idx_1 = np.where(ktg_array >= 0.999)[0][0]
            t_at_1 = t_vosst_range[idx_1]
            st.success(f"✅ **КТГ достигает 1** при T ≤ {t_at_1:.1f} ч")
        else:
            st.warning(f"⚠️ **Максимальный КТГ**: {max(ktg_values):.3f} (не достигает 1)")
        
        # Диапазон изменения
        st.info(f"📊 **Диапазон КТГ**: {min(ktg_values):.3f} - {max(ktg_values):.3f}")
        
        # Анализ эффективности по времени
        st.subheader("⏱️ Анализ по времени")
        
        analysis_times = {
            "Критическое": t_min,
            "Среднее": (t_min + t_max) / 2,
            "Максимальное": t_max
        }
        
        for name, time in analysis_times.items():
            ktg = calculate_ktg(ktg_zakl, t_vosst_sist, time)
            change = (ktg - ktg_zakl) / ktg_zakl * 100
            st.write(f"**{name} время ({time:.1f} ч)**: КТГ = {ktg:.3f} ({change:+.1f}%)")
    
    with col2:
        st.subheader("🎯 Рекомендации")
        
        # Оценка текущей ситуации
        if ktg_zakl < 0.3:
            st.error("**Критическая ситуация** - требуется срочное внедрение системы")
            st.write("""
            - Внедрить систему обслуживания в приоритетном порядке
            - Увеличить штат обслуживающего персонала
            - Создать запасные части на складе
            """)
        elif ktg_zakl < 0.6:
            st.warning("**Требуется улучшение** - система будет эффективна")
            st.write("""
            - Плановое внедрение системы обслуживания
            - Обучение персонала
            - Оптимизация логистики запасных частей
            """)
        else:
            st.success("**Стабильная ситуация** - система повысит надежность")
            st.write("""
            - Фокус на профилактическом обслуживании
            - Оптимизация существующих процессов
            - Внедрение системы мониторинга
            """)
        
        # Рекомендации по времени восстановления
        if t_vosst_sist < 1:
            st.success(f"**Отличный показатель**: {t_vosst_sist} ч - система высокоэффективна")
        elif t_vosst_sist < 3:
            st.info(f"**Хороший показатель**: {t_vosst_sist} ч - система эффективна")
        else:
            st.warning(f"**Требуется оптимизация**: {t_vosst_sist} ч - рассмотреть варианты сокращения времени")
    
    # Дополнительный график - тепловая карта
    st.subheader("🔥 Тепловая карта зависимости КТГ")
    
    # Создаем сетку значений
    t_sist_range = np.arange(1, 6, 0.5)
    t_ishod_range = np.arange(t_min, t_max + 1, 1)
    
    heatmap_data = []
    for t_sist in t_sist_range:
        row = []
        for t_ishod in t_ishod_range:
            ktg = calculate_ktg(ktg_zakl, t_sist, t_ishod)
            row.append(ktg)
        heatmap_data.append(row)
    
    # Создаем тепловую карту
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=t_ishod_range,
        y=t_sist_range,
        colorscale='RdYlGn',
        zmin=0,
        zmax=1,
        colorbar=dict(title="КТГ")
    ))
    
    fig_heatmap.update_layout(
        title="Зависимость КТГ от времени восстановления (до/после)",
        xaxis_title="T_восст_нов_исход, ч",
        yaxis_title="T_восст_сист, ч",
        height=400
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Вкладка 4: Экспорт
with tab4:
    st.header("📥 Экспорт результатов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Экспорт данных")
        
        # Создаем DataFrame для экспорта
        export_df = pd.DataFrame({
            'КТГ_закл': [ktg_zakl],
            'T_восст_сист_ч': [t_vosst_sist],
            'T_восст_мин_ч': [t_min],
            'T_восст_макс_ч': [t_max],
            'Средний_КТГ': [np.mean(ktg_values)],
            'Максимальный_КТГ': [np.max(ktg_values)],
            'Минимальный_КТГ': [np.min(ktg_values)],
            'Улучшение_макс_%': [((np.max(ktg_values) - ktg_zakl) / ktg_zakl * 100) if ktg_zakl > 0 else 0]
        })
        
        # Кнопки для экспорта
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Скачать сводку (CSV)",
            data=csv,
            file_name=f"ктг_сводка_ktg{ktg_zakl}_tsist{t_vosst_sist}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Экспорт полных данных
        full_data = pd.DataFrame({
            'T_восст_нов_исход_ч': t_vosst_range,
            'КТГ': ktg_values,
            'Изменение_КТГ_%': ktg_change_percent
        })
        
        csv_full = full_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Скачать полные данные (CSV)",
            data=csv_full,
            file_name=f"ктг_полные_данные_ktg{ktg_zakl}_tsist{t_vosst_sist}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.subheader("🖼️ Экспорт графиков")
        
        # Создаем Matplotlib график для экспорта
        fig_matplotlib, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(t_vosst_range, ktg_values, 'b-', linewidth=2)
        ax.axhline(y=1, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=ktg_zakl, color='green', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.fill_between(t_vosst_range, ktg_values, alpha=0.2, color='blue')
        
        ax.set_xlabel('T_восст_нов_исход, ч', fontsize=12)
        ax.set_ylabel('КТГ', fontsize=12)
        ax.set_title(f'КТГ = {ktg_zakl} × {t_vosst_sist} / T_восст_нов_исход', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([t_min, t_max])
        ax.set_ylim([0, 1.05])
        
        plt.tight_layout()
        
        # Сохраняем в BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig_matplotlib)
        
        # Кнопка для скачивания графика
        st.download_button(
            label="📷 Скачать график (PNG)",
            data=img_buffer,
            file_name=f"ктг_график_ktg{ktg_zakl}_tsist{t_vosst_sist}.png",
            mime="image/png",
            use_container_width=True
        )
    
    # Отчет
    st.subheader("📋 Сгенерировать отчет")
    
    report_text = f"""
    # Отчет по расчету КТГ
    ## Параметры расчета:
    - КТГ_закл: {ktg_zakl}
    - T_восст_сист: {t_vosst_sist} ч
    - Диапазон анализа: {t_min} - {t_max} ч
    
    ## Результаты:
    - Средний КТГ: {np.mean(ktg_values):.3f}
    - Максимальный КТГ: {np.max(ktg_values):.3f}
    - Минимальный КТГ: {np.min(ktg_values):.3f}
    - Максимальное улучшение: {((np.max(ktg_values) - ktg_zakl) / ktg_zakl * 100):.1f}%
    
    ## Рекомендации:
    """
    
    if ktg_zakl < 0.3:
        report_text += "Требуется срочное внедрение системы обслуживания РВД."
    elif ktg_zakl < 0.6:
        report_text += "Рекомендуется плановое внедрение системы обслуживания."
    else:
        report_text += "Система обслуживания повысит надежность оборудования."
    
    # Кнопка для скачивания отчета
    st.download_button(
        label="📄 Скачать отчет (TXT)",
        data=report_text,
        file_name=f"ктг_отчет_ktg{ktg_zakl}_tsist{t_vosst_sist}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Информация в подвале
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Расчет коэффициента технической готовности (КТГ) для горных предприятий</p>
    <p>Формула: КТГ = КТГ_закл × T_восст_сист / T_восст_нов_исход</p>
</div>
""", unsafe_allow_html=True)

# Автоматический расчет при изменении параметров
if calculate_button or 'auto_calculate' in st.session_state:
    st.session_state.auto_calculate = True
    st.rerun()