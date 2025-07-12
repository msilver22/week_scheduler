from ortools.sat.python import cp_model
import numpy as np

def pianifica_turni(disponibilità, lavoratori_minimi_per_slot=2):
    num_lavoratori = len(disponibilità)
    num_slot = len(disponibilità[0])

    model = cp_model.CpModel()

    # Variabili: x[i,j] = 1 se lavoratore i lavora nello slot j
    x = {}
    for i in range(num_lavoratori):
        for j in range(num_slot):
            if disponibilità[i][j]:
                x[i, j] = model.NewBoolVar(f"x[{i},{j}]")

    # Penalità se uno slot ha meno del minimo richiesto
    penalità_slot = []
    for j in range(num_slot):
        lavoratori_presenti = [x[i, j] for i in range(num_lavoratori) if (i, j) in x]
        count_presenti = model.NewIntVar(0, num_lavoratori, f"presenti_slot_{j}")
        model.Add(count_presenti == sum(lavoratori_presenti))
        deficit = model.NewIntVar(0, lavoratori_minimi_per_slot, f"deficit_slot_{j}")
        model.Add(deficit == lavoratori_minimi_per_slot - count_presenti)
        penalità_slot.append(deficit)

    # Turni assegnati per lavoratore
    turni_lavoratore = []
    for i in range(num_lavoratori):
        assegnati = [x[i, j] for j in range(num_slot) if (i, j) in x]
        turni = model.NewIntVar(0, num_slot, f"turni_{i}")
        model.Add(turni == sum(assegnati))
        turni_lavoratore.append(turni)

    # Minimizza squilibrio tra max e min turni
    max_turni = model.NewIntVar(0, num_slot, "max_turni")
    min_turni = model.NewIntVar(0, num_slot, "min_turni")
    for t in turni_lavoratore:
        model.Add(t <= max_turni)
        model.Add(t >= min_turni)

    bilanciamento = model.NewIntVar(0, num_slot, "bilanciamento")
    model.Add(bilanciamento == max_turni - min_turni)

    # Obiettivo: bilanciare i turni e coprire i turni
    model.Minimize(bilanciamento + sum(penalità_slot))

    # Risolvi
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        calendario = [[] for _ in range(num_slot)]
        for i in range(num_lavoratori):
            for j in range(num_slot):
                if (i, j) in x and solver.Value(x[i, j]):
                    calendario[j].append(i)

        # Report riepilogo
        print("\n📊 Turni assegnati per lavoratore:")
        for i in range(num_lavoratori):
            print(f"  Lavoratore {i}: {solver.Value(turni_lavoratore[i])} turni")

        print("\n⚠️ Slot sotto copertura minima:")
        for j, p in enumerate(penalità_slot):
            if solver.Value(p) > 0:
                print(f"  Slot {j}: solo {lavoratori_minimi_per_slot - solver.Value(p)} lavoratori")

        return calendario
    else:
        print("❌ Nessuna soluzione trovata.")
        return None

# Visualizzazione calendario leggibile (3 turni x 6 giorni)
def stampa_calendario(calendario, turni_per_giorno=3, giorni=6):
    nomi_turni = ["Mattina", "Pomeriggio", "Sera"]
    nomi_giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"]

    for giorno in range(giorni):
        print(f"\n📅 {nomi_giorni[giorno]}")
        for t in range(turni_per_giorno):
            slot_index = giorno * turni_per_giorno + t
            lavoratori = calendario[slot_index]
            turno = nomi_turni[t]
            print(f"  🕒 {turno:<10}: {lavoratori}")



import random

# --- Crea disponibilità casuale per 10 lavoratori e 18 slot --- #
#random.seed(42)
disponibilità = [[random.randint(0,1) for _ in range(18)] for _ in range(10)]

# --- 3 turni al giorno x 6 giorni = 18 slot (slot 0–17) --- #
#disponibilità = [
#    # Lavoratore 0 – solo primi 3 giorni (slot 0-8)
#    [1]*9 + [0]*9,
#    # Lavoratore 1 – solo primi 3 giorni
#    [1]*9 + [0]*9,
#    # Lavoratore 2 – solo primi 3 giorni
#    [1]*9 + [0]*9,
#    # Lavoratore 3 – solo pomeriggio e sera
#    [0,1,1]*6,
#    # Lavoratore 4 – solo pomeriggio e sera
#    [0,1,1]*6,
#    # Lavoratore 5 – solo pomeriggio e sera
#    [0,1,1]*6,
#    # Lavoratore 6 – solo mattina
#    [1,0,0]*6,
#    # Lavoratore 7 – solo venerdì e sabato (ultimi 6 slot)
#    [0]*12 + [1]*6,
#    # Lavoratore 8 – sempre disponibile
#    [1]*18,
#    # Lavoratore 9 – giorni alterni (lun, mer, ven)
#    [1,1,1, 0,0,0, 1,1,1, 0,0,0, 1,1,1, 0,0,0]
#]


print("Disponibilità:\n", disponibilità)

calendario = pianifica_turni(disponibilità)
stampa_calendario(calendario, turni_per_giorno=3, giorni=6)