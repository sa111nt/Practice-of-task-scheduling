import sys
import time
import subprocess


def main():
    if len(sys.argv) != 5:
        print("Użycie: python verifier_time.py algorytm instancja wynik limit_czasu")
        sys.exit(1)
    
    algorithm = sys.argv[1]
    instance = sys.argv[2]
    output = sys.argv[3]
    time_limit = float(sys.argv[4])
    
    # Uruchamiamy algorytm i mierzymy czas
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, algorithm, instance, output, str(time_limit)],
            timeout=time_limit * 1.5,  # Dajemy 50% zapasu na zakończenie
            capture_output=True,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"Czas wykonania: {elapsed_time:.3f} sekund")
        print(f"Limit czasu: {time_limit:.3f} sekund")
        
        if elapsed_time > time_limit:
            print(f"✗ PRZEKROCZONO LIMIT CZASU o {elapsed_time - time_limit:.3f} s")
            sys.exit(1)
        else:
            print(f"✓ CZAS W PORZĄDKU (margines: {time_limit - elapsed_time:.3f} s)")
            sys.exit(0)
    
    except subprocess.TimeoutExpired:
        print(f"✗ PRZEKROCZENIE LIMITU (hard limit: {time_limit * 1.5:.3f} s)")
        sys.exit(1)
    except Exception as e:
        print(f"✗ BŁĄD: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
