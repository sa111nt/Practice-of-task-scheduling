import os
import subprocess
import sys


# Konfiguracja
MY_ALBUM = "158740"
ALGORITHM = "algorytm_158740.py"


# Wszyscy studenci w grupie
STUDENTS = [
    "156007", "155890", "155909", "156027", "158740", "156020", "144678",
    "155886", "153918", "155805", "155937", "155895", "148080", "156143"
]


# Rozmiary instancji
SIZES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]


def run_for_all_instances(base_dir):
    """Uruchamia algorytm na wszystkich instancjach"""
    
    # Foldery IN i OUT w base_dir
    instances_dir = os.path.join(base_dir, "IN")
    output_dir = os.path.join(base_dir, "OUT")
    
    # Tworzymy folder OUT jeśli nie istnieje
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    
    for student in STUDENTS:
        for size in SIZES:
            # Formujemy nazwy plików
            instance_file = os.path.join(instances_dir, f"in_{student}_{size}.txt")
            output_file = os.path.join(output_dir, f"out_{MY_ALBUM}_{student}_{size}.txt")
            
            # Sprawdzamy istnienie instancji
            if not os.path.exists(instance_file):
                print(f"⚠ Pomijam {instance_file} (nie znaleziono)")
                continue
            
            # Obliczamy limit czasu
            time_limit = size / 10.0  # n/10 sekund
            
            print(f"Uruchamiam {student}_{size}... ", end='', flush=True)
            
            try:
                # Uruchamiamy algorytm
                result = subprocess.run(
                    [sys.executable, ALGORITHM, instance_file, output_file, str(time_limit)],
                    timeout=time_limit * 2,
                    capture_output=True,
                    text=True
                )
                
                # Odczytujemy wynik
                with open(output_file, 'r') as f:
                    tardy_count = int(f.readline().strip())
                
                results.append({
                    'student': student,
                    'size': size,
                    'tardy': tardy_count
                })
                
                print(f"✓ {tardy_count} spóźnionych zadań")
            
            except Exception as e:
                print(f"✗ BŁĄD: {e}")
                results.append({
                    'student': student,
                    'size': size,
                    'tardy': 'BŁĄD'
                })
    
    return results


def save_results_table(results, output_file="results_158740.txt"):
    """Zapisuje wyniki w formacie tabelarycznym do Excela"""
    with open(output_file, 'w') as f:
        f.write("Student\tSize\tTardy_Jobs\n")
        for r in results:
            f.write(f"{r['student']}\t{r['size']}\t{r['tardy']}\n")
    
    print(f"\n✓ Wyniki zapisane do {output_file}")


def main():
    # Domyślnie używamy folderu instances
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = "instances"
    
    instances_dir = os.path.join(base_dir, "IN")
    output_dir = os.path.join(base_dir, "OUT")
    
    print(f"Rozpoczynam przetwarzanie wsadowe...")
    print(f"Katalog bazowy: {base_dir}")
    print(f"Katalog instancji: {instances_dir}")
    print(f"Katalog wyników: {output_dir}")
    print(f"Łączna liczba plików do przetworzenia: {len(STUDENTS) * len(SIZES)}")
    print("-" * 60)
    
    results = run_for_all_instances(base_dir)
    save_results_table(results)
    
    print("-" * 60)
    print(f"✓ Zakończono: przetworzono {len(results)} plików")


if __name__ == "__main__":
    main()
