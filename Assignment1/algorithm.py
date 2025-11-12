import sys
import time
import random

def read_instance(filename):
    """Wczytuje plik z instancją"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    
    # Wczytaj czasy wykonania i terminy (deadline'y)
    p = []
    d = []
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        p.append(int(parts[0]))
        d.append(int(parts[1]))
    
    # Wczytaj macierz przezbrojeń
    S = []
    for i in range(n + 1, 2 * n + 1):
        row = list(map(int, lines[i].strip().split()))
        S.append(row)
    
    return n, p, d, S

def calculate_tardy_jobs(sequence, p, d, S):
    """
    Oblicza liczbę spóźnionych zadań dla danej sekwencji
    sequence: lista numerów zadań (numeracja od 1)
    """
    n = len(sequence)
    current_time = 0
    tardy_count = 0
    
    for i in range(n):
        job = sequence[i] - 1  # Przelicz na indeksowanie od 0
        
        # Dodaj czas przezbrojenia
        if i > 0:
            prev_job = sequence[i-1] - 1
            current_time += S[prev_job][job]
        
        # Wykonaj zadanie
        current_time += p[job]
        
        # Sprawdź opóźnienie
        if current_time > d[job]:
            tardy_count += 1
    
    return tardy_count

def edd_heuristic(n, p, d):
    """Algorytm zachłanny: sortowanie według terminów (EDD - Earliest Due Date)"""
    jobs = list(range(1, n + 1))
    # Sortuj według terminów (indeksowanie od 0 dla d)
    jobs.sort(key=lambda j: d[j-1])
    return jobs

def local_search_2opt(sequence, p, d, S, time_limit, start_time):
    """Przeszukiwanie lokalne z zamianami 2-opt"""
    best_sequence = sequence[:]
    best_tardy = calculate_tardy_jobs(best_sequence, p, d, S)
    
    n = len(sequence)
    
    # Dostosuj max_iterations do dużych n
    if n <= 400:
        max_iterations = 10000  
    else:  # n > 400
        max_iterations = 1500  # Zmniejszone dla dużych
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        # Sprawdź czas na początku iteracji
        elapsed = time.time() - start_time
        if elapsed > time_limit * 0.85:  # Zostaw 15% zapasu
            break
        
        improved = False
        
        # Próbuj wszystkie możliwe zamiany 2-opt
        for i in range(len(sequence) - 1):
            # Dla dużych n sprawdzaj czas częściej
            if n > 400 and i % 50 == 0:
                elapsed = time.time() - start_time
                if elapsed > time_limit * 0.85:
                    return best_sequence, best_tardy
            
            for j in range(i + 1, len(sequence)):
                # Stwórz nową sekwencję z zamianą
                new_sequence = best_sequence[:]
                new_sequence[i], new_sequence[j] = new_sequence[j], new_sequence[i]
                
                new_tardy = calculate_tardy_jobs(new_sequence, p, d, S)
                
                if new_tardy < best_tardy:
                    best_sequence = new_sequence
                    best_tardy = new_tardy
                    improved = True
                    
                    # Jeśli znalazłeś optimum (0 opóźnień), wyjdź
                    if best_tardy == 0:
                        return best_sequence, best_tardy
        
        iterations += 1
    
    return best_sequence, best_tardy

def insertion_local_search(sequence, p, d, S, time_limit, start_time):
    """Przeszukiwanie lokalne z przesunięciami (insertion moves)"""
    best_sequence = sequence[:]
    best_tardy = calculate_tardy_jobs(best_sequence, p, d, S)
    
    n = len(sequence)
    
    # Dostosuj max_iterations do dużych n
    if n <= 400:
        max_iterations = 4000  
    else:  # n > 400
        max_iterations = 1000  # Zmniejszone dla dużych
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        # Sprawdź czas
        elapsed = time.time() - start_time
        if elapsed > time_limit * 0.95:  # Użyj do 95% czasu
            break
        
        improved = False
        
        # Próbuj przesunąć każde zadanie w inne miejsce
        for i in range(len(sequence)):
            # Dla dużych n sprawdzaj czas częściej
            if n > 400 and i % 30 == 0:
                elapsed = time.time() - start_time
                if elapsed > time_limit * 0.95:
                    return best_sequence, best_tardy
            
            for j in range(len(sequence)):
                if i == j:
                    continue
                
                # Stwórz nową sekwencję z przesunięciem
                new_sequence = best_sequence[:]
                job = new_sequence.pop(i)
                new_sequence.insert(j, job)
                
                new_tardy = calculate_tardy_jobs(new_sequence, p, d, S)
                
                if new_tardy < best_tardy:
                    best_sequence = new_sequence
                    best_tardy = new_tardy
                    improved = True
                    
                    if best_tardy == 0:
                        return best_sequence, best_tardy
        
        iterations += 1
    
    return best_sequence, best_tardy

def solve_instance(n, p, d, S, time_limit):
    """Główna funkcja rozwiązania"""
    start_time = time.time()
    
    # Rozwiązanie początkowe: heurystyka EDD
    initial_solution = edd_heuristic(n, p, d)
    initial_tardy = calculate_tardy_jobs(initial_solution, p, d, S)
    
    # Jeśli już optymalnie, zwróć
    if initial_tardy == 0:
        return initial_solution, initial_tardy
    
    # Przeszukiwanie lokalne 2-opt
    solution_2opt, tardy_2opt = local_search_2opt(
        initial_solution, p, d, S, time_limit, start_time
    )
    
    if tardy_2opt == 0:
        return solution_2opt, tardy_2opt
    
    # Przeszukiwanie lokalne z przesunięciami
    remaining_time = time_limit - (time.time() - start_time)
    if remaining_time > 0.1:
        solution_ins, tardy_ins = insertion_local_search(
            solution_2opt, p, d, S, time_limit, start_time
        )
        
        if tardy_ins < tardy_2opt:
            return solution_ins, tardy_ins
    
    return solution_2opt, tardy_2opt

def write_solution(filename, tardy_count, sequence):
    """Zapisuje rozwiązanie do pliku"""
    with open(filename, 'w') as f:
        f.write(f"{tardy_count}\n")
        f.write(" ".join(map(str, sequence)) + "\n")

def main():
    if len(sys.argv) != 4:
        print("Użycie: python algorithm_158740.py input_file output_file time_limit")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_limit = float(sys.argv[3])
    
    # Wczytaj instancję
    n, p, d, S = read_instance(input_file)
    
    # Rozwiąż
    solution, tardy_count = solve_instance(n, p, d, S, time_limit)
    
    # Zapisz rezultat
    write_solution(output_file, tardy_count, solution)
    
    print(f"Zrobione: {tardy_count} spóźnionych zadań")

if __name__ == "__main__":
    main()
