import os
from collections import deque

def readFile(file_path): # Lê os dados do arquivo de entrada
    with open(file_path, 'r') as file:
        lines = file.readlines()
        quantum = int(lines[0].strip())  # Lê o quantum da primeira linha
        processes = []  
        for line in lines[1:]:  # Lê os processos (chegada e duração)
            arrival, duration = map(int, line.strip().split())
            processes.append((arrival, duration))
    return quantum, processes

def writeFile(file_path, results): # Escreve os resultados em um arquivo de saída
    with open(file_path, 'w') as file:
        # Escreve os resultados com o formato de três casas decimais
        for result in results:
            file.write(' '.join(f"{x:.3f}".replace('.', ',') for x in result) + '\n')

def calculation(processes, start_times, end_times):
    n = len(processes)
    # Tempo de início - tempo de chegada
    response_times = [start_times[i] - processes[i][0] for i in range(n)]
    # O tempo de espera é igual ao tempo de resposta neste caso
    waiting_times = [response_times[i] for i in range(n)]
    # Tempo de término - tempo de chegada
    turnarounds = [end_times[i] - processes[i][0] for i in range(n)]

    avg_response = sum(response_times) / n
    avg_waiting = sum(waiting_times) / n
    avg_turnaround = sum(turnarounds) / n

    return avg_response, avg_waiting, avg_turnaround

def fifo(processes):
    processes.sort(key=lambda x: x[0])  # Ordena os processos por tempo de chegada
    current_time = 0
    start_times = []
    end_times = []

    for arrival, duration in processes:
        # Se o processo ainda não chegou, o tempo atual é ajustado
        if current_time < arrival:
            current_time = arrival
        start_times.append(current_time)  # Marca o tempo de início
        current_time += duration  # Atualiza o tempo atual
        end_times.append(current_time)  # Marca o tempo de término

    return calculation(processes, start_times, end_times)

def sjf(processes):
    processes.sort(key=lambda x: x[0])  # Ordena os processos por tempo de chegada
    current_time = 0
    start_times = [-1] * len(processes)
    end_times = [-1] * len(processes)
    completed = 0

    while completed < len(processes):
        # Seleciona os processos que já chegaram e não foram iniciados
        available = [(i, p) for i, p in enumerate(processes) if p[0] <= current_time and start_times[i] == -1]
        if available:
            # Seleciona o processo com menor duração
            idx, (arrival, duration) = min(available, key=lambda x: x[1][1])
            start_times[idx] = current_time  # Marca o início do processo
            current_time += duration  # Atualiza o tempo atual
            end_times[idx] = current_time  # Marca o término do processo
            completed += 1
        else:
            # Incrementa o tempo caso nenhum processo esteja pronto
            current_time += 1

    return calculation(processes, start_times, end_times)

def srt(processes):
    n = len(processes)
    current_time = 0
    completed = 0

    remaining_times = [p[1] for p in processes]  # Tempo restante de execução para cada processo
    start_times = [-1] * n  # Tempo de início dos processos
    end_times = [-1] * n  # Tempo de término dos processos
    completed_process = [False] * n  # Marca os processos concluídos

    while completed < n:
        available = [(i, remaining_times[i]) for i in range(n) if processes[i][0] <= current_time and not completed_process[i]]

        if available:
            # Escolhe o processo com o menor tempo restante
            idx = min(available, key=lambda x: x[1])[0]

            # Marca o tempo de início se for a primeira execução
            if start_times[idx] == -1:
                start_times[idx] = current_time

            # Executa o processo por 1 unidade de tempo
            remaining_times[idx] -= 1
            current_time += 1

            # Verifica se o processo foi concluído
            if remaining_times[idx] == 0:
                end_times[idx] = current_time
                completed_process[idx] = True
                completed += 1
        else:
            # Incrementa o tempo se nenhum processo estiver pronto
            current_time += 1

    return calculation(processes, start_times, end_times)

def round_robin(processes, quantum):
    n = len(processes)
    current_time = 0
    remaining_times = [p[1] for p in processes]  # Tempo restante de execução
    start_times = [-1] * n  # Tempo de início do processo
    end_times = [0] * n  # Tempo de término do processo
    queue = deque()  # Fila para controle dos processos

    # Adiciona processos que chegam no tempo 0
    for i, (arrival, _) in enumerate(processes):
        if arrival == 0:
            queue.append(i)

    added = [arrival == 0 for arrival, _ in processes]  # Processos já na fila

    while queue or any(rt > 0 for rt in remaining_times):
        if queue:
            idx = queue.popleft()  # Remove o próximo processo da fila
            arrival, duration = processes[idx]

            if start_times[idx] == -1:  # Define o tempo de início na primeira execução
                start_times[idx] = current_time

            # Executa o processo pelo quantum ou pelo tempo restante
            time_to_execute = min(quantum, remaining_times[idx])
            remaining_times[idx] -= time_to_execute
            current_time += time_to_execute

            # Adiciona novos processos que chegaram durante esta execução
            for i, (arrival_time, _) in enumerate(processes):
                if not added[i] and arrival_time <= current_time:
                    queue.append(i)
                    added[i] = True

            if remaining_times[idx] > 0:  # Se o processo ainda não terminou, volta para o final da fila
                queue.append(idx)
            else:
                end_times[idx] = current_time  # Marca o término do processo
        else:
            # Avança o tempo se não há processos prontos na fila
            current_time += 1
            for i, (arrival_time, _) in enumerate(processes):
                if not added[i] and arrival_time <= current_time:
                    queue.append(i)
                    added[i] = True

    return calculation(processes, start_times, end_times)

def processFile(input_dir):
    for i in range(1, 11):
        input_file = os.path.join(input_dir, f"TESTE-{i:02}.txt")
        output_file = os.path.join(input_dir, f"TESTE-{i:02}-RESULTADO.txt")

        quantum, processes = readFile(input_file)

        fifo_metrics = fifo(processes)
        sjf_metrics = sjf(processes)
        srt_metrics = srt(processes)
        rr_metrics = round_robin(processes, quantum)

        results = [fifo_metrics, sjf_metrics, srt_metrics, rr_metrics] # Formata os resultados finais
        writeFile(output_file, results)

if __name__ == "__main__":
    input_directory = "D:\\"  # Caminho
    processFile(input_directory)