import matplotlib
matplotlib.use('Agg')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
import json
from . import quantum_specialist 
from django.core.files.base import ContentFile
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt
import numpy as np

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

def generate_chart(results_list):
    df = pd.DataFrame(results_list)
    anomaly_count = df['quantum'].value_counts().to_dict().get('ANOMALY DETECTED (Real QML)', 0)
    normal_count = len(df) - anomaly_count
    
    counts = [normal_count, anomaly_count]
    labels = ['Normal', 'Anomaly']
    colors = ['#007acc', '#dc3545']

    plt.figure(figsize=(6, 6))
    plt.pie(counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'color': 'white'})
    plt.title('Quantum Scan Results Distribution', color='white')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    plt.close()
    
    encoded_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{encoded_img}'


@login_required
def analyze_log(request):
    results = {}
    total_anomalies = 0
    total_scanned = 0
    chart_url = None
    results_list = []
    ai_explanation = None 

    if request.method == 'POST' and 'log_file' in request.FILES:
        is_file_upload = True
        log_file = request.FILES['log_file']
        log_content = log_file.read().decode('utf-8')
        log_entries = log_content.splitlines()

        
        for line_num, log_input in enumerate(log_entries, 1):
            log_input = log_input.strip()
            if not log_input: continue

            ollama_verdict = None
            quantum_verdict = None
            is_anomaly = False
            total_scanned += 1

            prompt = f"You are a cybersecurity analyst. Analyze this log entry and respond with ONLY the word 'Normal' or 'Suspicious'. Log: \"{log_input}\""
            
            try:
                response = requests.post(OLLAMA_API_URL, json={"model": "llama3:8b", "prompt": prompt, "stream": False}, timeout=10)
                ollama_verdict = response.json().get('response', 'Error').strip().replace('"', '')

                if ollama_verdict.strip().lower() == "suspicious":
                    quantum_verdict = quantum_specialist.run_quantum_scan(log_input)
                    
                    if 'ANOMALY' in quantum_verdict:
                        is_anomaly = True
                        total_anomalies += 1
                        
            except Exception as e:
                ollama_verdict = f"Ollama Error: {e}"

            results[line_num] = {
                'log_entry': log_input,
                'ollama': ollama_verdict,
                'quantum': quantum_verdict,
                'is_anomaly': is_anomaly
            }
            results_list.append({'quantum': quantum_verdict})
        
        if total_anomalies > 0:
            chart_url = generate_chart(results_list)
            
            summary_prompt = f"""
            A bulk log file analysis just finished. Total logs scanned: {total_scanned}. Total ANOMALIES found by the quantum model: {total_anomalies}.
            Write a brief, high-level, single-paragraph summary for the security analyst, describing the potential scope of the incident based on the high anomaly count.
            """
            summary_response = requests.post(OLLAMA_API_URL, json={"model": "llama3:8b", "prompt": summary_prompt, "stream": False}, timeout=30)
            ai_explanation = summary_response.json().get('response', 'AI Summary Failed.')
        
        elif total_scanned > 0:
            chart_url = generate_chart(results_list)

    context = {
        'results': results,
        'total_scanned': total_scanned,
        'total_anomalies': total_anomalies,
        'chart_url': chart_url,
        'ai_explanation': ai_explanation 
    }
    return render(request, 'index.html', context)