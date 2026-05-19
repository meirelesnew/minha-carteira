"""
executar_ia.py — Muth v2 para GitHub Actions
Roda automaticamente a cada 6 horas e atualiza o Firebase.
"""

import yfinance as yf
import numpy as np
import pandas as pd
import requests
import warnings
import os
import sys

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import RobustScaler
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES
# ============================================================
FIREBASE_PROJECT = 'carteira-01'
FIREBASE_API_KEY = 'AIzaSyAJyTeir6U4_AnqDuBzuKQ0ODIiihgpz4c'

ATIVOS = [
    'MXRF11.SA', 'GARE11.SA',
    'ITSA4.SA',  'BBAS3.SA', 'BBSE3.SA',
    'EGIE3.SA',  'TAEE11.SA','KLBN4.SA', 'WEGE3.SA'
]

JANELA        = 20
THRESHOLD     = 0.53
ALVO_MIN_ALTA = 0.002
EPOCAS_MAX    = 150
BATCH_SIZE    = 16
PERIODO_DADOS = '2y'
FEATURES      = ['Variacao','MM_ratio','Vol_norm','Volatilidade','RSI','Momentum10','Momentum5']

# ============================================================
# FUNÇÕES
# ============================================================

def calcular_indicadores(df):
    df = df.copy()
    df['Variacao']     = df['Close'].pct_change()
    df['MM5']          = df['Close'].rolling(5).mean()
    df['MM20']         = df['Close'].rolling(20).mean()
    df['MM_ratio']     = (df['MM5'] / df['MM20']) - 1
    df['Vol_norm']     = df['Volume'] / df['Volume'].rolling(20).mean()
    df['Volatilidade'] = df['Variacao'].rolling(10).std()
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['RSI']          = (100 - (100 / (1 + (gain / (loss + 1e-10))))) / 100
    df['Momentum10']   = df['Close'].pct_change(10)
    df['Momentum5']    = df['Close'].pct_change(5)
    df['Alvo']         = np.where(df['Variacao'].shift(-1) > ALVO_MIN_ALTA, 1, 0)
    return df.dropna()


def treinar_e_prever(ticker):
    nome = ticker.replace('.SA', '')
    print(f'\n📊 Processando {nome}...')

    try:
        df_raw = yf.download(ticker, period=PERIODO_DADOS, interval='1d',
                             progress=False, auto_adjust=True)
        if df_raw.empty or len(df_raw) < 100:
            print(f'   ⚠️  Dados insuficientes para {nome}')
            return None

        if isinstance(df_raw.columns, pd.MultiIndex):
            df_raw.columns = df_raw.columns.get_level_values(0)

        df = df_raw[['Close', 'Volume']].copy()
        df['Volume'] = df['Volume'].astype(float)
        print(f'   Dados: {len(df)} dias ({df.index[0].date()} → {df.index[-1].date()})')

    except Exception as e:
        print(f'   ❌ Erro ao baixar {nome}: {e}')
        return None

    df = calcular_indicadores(df)
    if len(df) < 60:
        print(f'   ⚠️  Poucas amostras para {nome}')
        return None

    scaler   = RobustScaler()
    X_scaled = scaler.fit_transform(df[FEATURES].values)
    y_raw    = df['Alvo'].values

    X, y = [], []
    for i in range(len(X_scaled) - JANELA):
        X.append(X_scaled[i:i+JANELA])
        y.append(y_raw[i+JANELA])
    X, y = np.array(X), np.array(y)

    n_tr  = int(len(X) * 0.80)
    n_pos = y[:n_tr].sum()
    n_neg = n_tr - n_pos
    cw    = {0: 1.0, 1: max(1.0, float(n_neg) / (float(n_pos) + 1e-10))}

    model = models.Sequential([
        layers.Input(shape=(JANELA, len(FEATURES))),
        layers.LSTM(64, return_sequences=True),
        layers.Dropout(0.25),
        layers.LSTM(32),
        layers.Dropout(0.20),
        layers.Dense(16, activation='relu'),
        layers.Dense(1,  activation='sigmoid')
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=12,
                      restore_best_weights=True, verbose=0),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                          patience=6, min_lr=1e-6, verbose=0)
    ]
    hist = model.fit(
        X[:n_tr], y[:n_tr],
        epochs=EPOCAS_MAX,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        class_weight=cw,
        callbacks=callbacks,
        verbose=0
    )
    epocas = len(hist.history['loss'])

    _, acc   = model.evaluate(X[n_tr:], y[n_tr:], verbose=0)
    ultimos  = X_scaled[-JANELA:].reshape(1, JANELA, len(FEATURES))
    prob     = float(model.predict(ultimos, verbose=0)[0][0])
    chance   = round(prob * 100, 2)
    sinal    = 'COMPRAR' if prob > THRESHOLD else 'AGUARDAR'
    acuracia = round(acc * 100, 1)

    print(f'   Épocas: {epocas} | Acurácia: {acuracia}% | Chance alta: {chance}% → {sinal}')
    return {
        'ativo':        nome,
        'chance_subir': chance,
        'sinal':        sinal,
        'acuracia':     acuracia,
        'epocas':       epocas,
        'data_analise': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'modelo':       'LSTM-v2 (64→32→16)',
        'janela_dias':  JANELA,
        'features':     ','.join(FEATURES)
    }


def salvar_no_firebase(resultado):
    if resultado is None:
        return False

    url = (
        f'https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}'
        f'/databases/(default)/documents/previsoes_carteira/{resultado["ativo"]}'
        f'?key={FIREBASE_API_KEY}'
    )
    payload = {
        'fields': {
            'ativo':         {'stringValue':  resultado['ativo']},
            'chance_subir':  {'doubleValue':  resultado['chance_subir']},
            'sinal':         {'stringValue':  resultado['sinal']},
            'acuracia':      {'doubleValue':  resultado['acuracia']},
            'epocas':        {'integerValue': str(resultado['epocas'])},
            'data_analise':  {'stringValue':  resultado['data_analise']},
            'modelo':        {'stringValue':  resultado['modelo']},
            'janela_dias':   {'integerValue': str(resultado['janela_dias'])},
            'features':      {'stringValue':  resultado['features']},
        }
    }
    try:
        resp = requests.patch(url, json=payload, timeout=15)
        return resp.status_code in [200, 201]
    except Exception as e:
        print(f'   ❌ Erro Firebase: {e}')
        return False


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
print('=' * 55)
print('🧠 MUTH v2 — GitHub Actions')
print(f'   Início: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
print('=' * 55)

resultados = []
salvos = 0
erros  = 0

for ticker in ATIVOS:
    resultado = treinar_e_prever(ticker)
    if resultado:
        resultados.append(resultado)
        ok = salvar_no_firebase(resultado)
        if ok:
            salvos += 1
            print(f'   💾 Salvo no Firebase!')
        else:
            erros += 1
            print(f'   ⚠️  Erro ao salvar no Firebase')
    else:
        erros += 1

# Relatório final
print()
print('=' * 55)
print('📋 RELATÓRIO FINAL — MUTH v2')
print('=' * 55)
print(f"{'Ativo':<10} {'Chance':>8} {'Sinal':<12} {'Acurácia':>10}")
print('-' * 44)
for r in sorted(resultados, key=lambda x: x['chance_subir'], reverse=True):
    emoji = '▲' if r['sinal'] == 'COMPRAR' else '●'
    print(f"{r['ativo']:<10} {r['chance_subir']:>7.1f}%  {emoji} {r['sinal']:<10} {r['acuracia']:>8.1f}%")

print()
comprar  = [r for r in resultados if r['sinal'] == 'COMPRAR']
aguardar = [r for r in resultados if r['sinal'] == 'AGUARDAR']
print(f'✅ COMPRAR  ({len(comprar)}):  {", ".join([r["ativo"] for r in comprar])}')
print(f'● AGUARDAR ({len(aguardar)}): {", ".join([r["ativo"] for r in aguardar])}')
print()
print(f'Firebase: {salvos} salvos, {erros} erros')
print(f'Fim: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
print()
print('🌐 Vitrine: https://carteira-01.web.app')

# Sair com erro se nenhum ativo foi processado
if salvos == 0:
    print('❌ Nenhum ativo salvo — verificar logs acima')
    sys.exit(1)
