import random
import os

STUDENT_ID = "158740"

#out_nm-albumu-programu_nr-albumu-instancji_rozmiar.txt
def generate_and_save_instance(n, output_dir="instances"):
    random.seed(n)  # dla powtarzalności

    # Generacja pj (czasy wykonania: 1-100)
    p = [random.randint(1, 100) for _ in range(n)]

    # Generacja dj (deadliny)
    total_time = sum(p)
    max_deadline = int(total_time * 0.7)
    d = [random.randint(p[i], max(p[i] + 1, max_deadline)) for i in range(n)]

    # Generacja Sij (macierz przezbrojenia)
    S = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0)
            elif random.random() < 0.1:  # 10% bez przezbrojenia
                row.append(0)
            else:
                row.append(random.randint(1, 50))
        S.append(row)

    # Zapis do pliku
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"in_{STUDENT_ID}_{n}.txt")

    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        for i in range(n):
            f.write(f"{p[i]} {d[i]}\n")
        for row in S:
            f.write(" ".join(map(str, row)) + "\n")

    print(f"✓ Wygenerowano: {filename}")


if __name__ == "__main__":
    print("Generator instancji 1|Sij|ΣUj\n")
    sizes = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]

    for n in sizes:
        generate_and_save_instance(n)

    print(f"\nGotowe! Wszystkie pliki w folderze 'instances/'")