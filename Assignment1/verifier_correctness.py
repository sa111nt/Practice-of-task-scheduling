import sys


def read_instance(filename):
    """Wczytuje plik z instancją"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    
    p = []
    d = []
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        p.append(int(parts[0]))
        d.append(int(parts[1]))
    
    S = []
    for i in range(n + 1, 2 * n + 1):
        row = list(map(int, lines[i].strip().split()))
        S.append(row)
    
    return n, p, d, S


def read_solution(filename):
    """Wczytuje plik z rozwiązaniem"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    reported_tardy = int(lines[0].strip())
    sequence = list(map(int, lines[1].strip().split()))
    
    return reported_tardy, sequence


def verify_solution(n, p, d, S, reported_tardy, sequence):
    """Sprawdza poprawność rozwiązania"""
    errors = []
    
    # Sprawdzenie 1: Wszystkie zadania występują dokładnie raz
    if len(sequence) != n:
        errors.append(f"BŁĄD: Długość sekwencji {len(sequence)} != {n}")
        return False, errors, None
    
    if set(sequence) != set(range(1, n + 1)):
        errors.append(f"BŁĄD: Nieprawidłowe zadania w sekwencji")
        return False, errors, None
    
    if len(sequence) != len(set(sequence)):
        errors.append(f"BŁĄD: Duplikaty zadań w sekwencji")
        return False, errors, None
    
    # Sprawdzenie 2: Obliczamy faktyczną liczbę spóźnień
    current_time = 0
    actual_tardy = 0
    
    for i in range(n):
        job = sequence[i] - 1  # Indeksowanie od 0
        
        # Dodaj czas przezbrojenia
        if i > 0:
            prev_job = sequence[i-1] - 1
            current_time += S[prev_job][job]
        
        # Wykonaj zadanie
        current_time += p[job]
        
        # Sprawdź spóźnienie
        if current_time > d[job]:
            actual_tardy += 1
    
    # Sprawdzenie 3: Porównaj z podaną wartością
    if actual_tardy != reported_tardy:
        errors.append(f"BŁĄD: Zadeklarowano spóźnionych={reported_tardy}, faktycznie={actual_tardy}")
        return False, errors, actual_tardy
    
    return True, [], actual_tardy


def main():
    if len(sys.argv) != 3:
        print("Użycie: python verifier_correctness.py plik_instancji plik_rozwiazania")
        sys.exit(1)
    
    instance_file = sys.argv[1]
    solution_file = sys.argv[2]
    
    try:
        # Wczytaj dane
        n, p, d, S = read_instance(instance_file)
        reported_tardy, sequence = read_solution(solution_file)
        
        # Sprawdź rozwiązanie
        is_valid, errors, actual_tardy = verify_solution(
            n, p, d, S, reported_tardy, sequence
        )
        
        if is_valid:
            print(f"✓ POPRAWNE: {actual_tardy} spóźnionych zadań")
            sys.exit(0)
        else:
            print("✗ NIEPOPRAWNE:")
            for error in errors:
                print(f"  {error}")
            if actual_tardy is not None:
                print(f"  Faktyczna liczba spóźnionych: {actual_tardy}")
            sys.exit(1)
    
    except Exception as e:
        print(f"✗ BŁĄD: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
