# Multi-Axial Stress Failure Analysis
import tkinter as tk
from tkinter import ttk, messagebox


def find_principal_stress(sigma_x, sigma_y, tau_xy):
    """Find principal stresses for plane stress."""
    average = (sigma_x + sigma_y) / 2
    radius = (((sigma_x - sigma_y) / 2) ** 2 + tau_xy ** 2) ** 0.5

    sigma_1 = average + radius
    sigma_2 = average - radius
    sigma_3 = 0

    return sigma_1, sigma_2, sigma_3


def calculate_failure(sigma_1, sigma_2, sigma_3, yield_strength, poisson):
    """Calculating equivalent stress and factor of safety for each theory."""

    # Rankine - Maximum Principal Stress Theory
    rankine = max(abs(sigma_1), abs(sigma_2), abs(sigma_3))

    # Tresca - Maximum Shear Stress Theory
    tresca = max(
        abs(sigma_1 - sigma_2),
        abs(sigma_2 - sigma_3),
        abs(sigma_3 - sigma_1)
    )

    # von Mises - Distortion Energy Theory
    von_mises = (
        0.5 * (
            (sigma_1 - sigma_2) ** 2
            + (sigma_2 - sigma_3) ** 2
            + (sigma_3 - sigma_1) ** 2
        )
    ) ** 0.5

    # Saint-Venant - Maximum Principal Strain Theory
    saint_venant = max(
        abs(sigma_1 - poisson * (sigma_2 + sigma_3)),
        abs(sigma_2 - poisson * (sigma_1 + sigma_3)),
        abs(sigma_3 - poisson * (sigma_1 + sigma_2))
    )

    # Haigh  - Maximum Strain Energy Theory
    haigh_value = (
        sigma_1**2 + sigma_2**2 + sigma_3**2
        - 2 * poisson * (
            sigma_1 * sigma_2 + sigma_2 * sigma_3 + sigma_3 * sigma_1
        )
    )
    haigh = max(0, haigh_value) ** 0.5

    names = ["Rankine", "Tresca", "von Mises", "Saint-Venant", "Haigh"]
    stresses = [rankine, tresca, von_mises, saint_venant, haigh]

    results = []
    for name, equivalent_stress in zip(names, stresses):
        if equivalent_stress == 0:
            fos = float("inf")
        else:
            fos = yield_strength / equivalent_stress

        status = "SAFE" if fos >= 1 else "FAILURE"
        results.append((name, equivalent_stress, fos, status))

    return results


def draw_graph(results, yield_strength):

    graph.delete("all")

    width = max(graph.winfo_width(), 800)
    height = max(graph.winfo_height(), 230)

    left, right = 65, width - 20
    top, bottom = 20, height - 40

    stresses = [row[1] for row in results]
    max_value = max(max(stresses), yield_strength, 1) * 1.2

    # Graph axes
    graph.create_line(left, top, left, bottom, width=2)
    graph.create_line(left, bottom, right, bottom, width=2)

    # Horizontal scale lines
    for i in range(6):
        y = bottom - i * (bottom - top) / 5
        value = max_value * i / 5
        graph.create_line(left, y, right, y, fill="lightgray")
        graph.create_text(left - 8, y, text=f"{value:.0f}", anchor="e")

    # Yield strength reference line
    yield_y = bottom - (yield_strength / max_value) * (bottom - top)
    graph.create_line(
        left, yield_y, right, yield_y,
        fill="red", width=2, dash=(5, 3)
    )
    graph.create_text(
        right - 5, yield_y - 10,
        text=f"Yield strength = {yield_strength:.1f} MPa",
        fill="red", anchor="e"
    )

    # Bars for each theory
    gap = (right - left) / len(results)
    bar_width = min(48, gap / 2)

    for i, row in enumerate(results):
        name, stress, fos, status = row

        center = left + gap * (i + 0.5)
        bar_height = (stress / max_value) * (bottom - top)

        x1 = center - bar_width / 2
        x2 = center + bar_width / 2
        y1 = bottom - bar_height

        bar_color = "steelblue" if status == "SAFE" else "orange"

        graph.create_rectangle(
            x1, y1, x2, bottom,
            fill=bar_color, outline=""
        )
        graph.create_text(center, y1 - 10, text=f"{stress:.1f}")
        graph.create_text(center, bottom + 15, text=name)


def calculate():
    """Read all five values entered by the user and calculate results."""
    try:
        # Read values from the input boxes
        sigma_x = float(entry_x.get())
        sigma_y = float(entry_y.get())
        tau_xy = float(entry_tau.get())
        yield_strength = float(entry_yield.get())
        poisson = float(entry_poisson.get())

        if yield_strength <= 0:
            raise ValueError("Yield strength must be greater than zero.")

        if not 0 <= poisson <= 0.5:
            raise ValueError("Poisson ratio must be between 0 and 0.5.")

    except ValueError as error:
        messagebox.showerror(
            "Input error",
            "Please enter a valid number in every input box.\n\n" + str(error)
        )
        return

    # Calculate principal stresses
    sigma_1, sigma_2, sigma_3 = find_principal_stress(
        sigma_x, sigma_y, tau_xy
    )

    # Calculate all failure theories
    results = calculate_failure(
        sigma_1, sigma_2, sigma_3, yield_strength, poisson
    )

    principal_label.config(
        text=f"Principal stresses: sigma 1 = {sigma_1:.2f} MPa   "
             f"sigma 2 = {sigma_2:.2f} MPa   sigma 3 = {sigma_3:.2f} MPa"
    )

    # Clear the previous table
    for item in result_table.get_children():
        result_table.delete(item)

    # Display the new results
    for name, stress, fos, status in results:
        fos_text = "Infinity" if fos == float("inf") else f"{fos:.3f}"
        result_table.insert(
            "", "end",
            values=(name, f"{stress:.2f}", fos_text, status)
        )

    # Find the theory with the lowest factor of safety
    governing = min(results, key=lambda row: row[2])
    name, stress, fos, status = governing
    fos_text = "Infinity" if fos == float("inf") else f"{fos:.3f}"

    final_label.config(
        text=f"Governing theory: {name} | FOS: {fos_text} | Result: {status}"
    )

    # Update graph using the user's current inputs
    draw_graph(results, yield_strength)


def clear_all():
    """Clear all input boxes and old results."""
    for box in input_boxes:
        box.delete(0, tk.END)

    for item in result_table.get_children():
        result_table.delete(item)

    principal_label.config(text="Principal stresses will appear here.")
    final_label.config(text="Governing theory will appear here.")
    graph.delete("all")


# ---------------- Main window ----------------

window = tk.Tk()
window.title("Multi-Axial Stress Failure Analysis")
window.geometry("960x790")
window.minsize(820, 680)

tk.Label(
    window,
    text="MULTI-AXIAL STRESS FAILURE ANALYSIS",
    font=("Arial", 17, "bold")
).pack(pady=12)

tk.Label(
    window,
    text="Enter your own stress and material values below (stress unit: MPa)"
).pack()

# Input boxes are empty so the user must enter every value.
input_frame = tk.LabelFrame(
    window, text="Enter Input Values", padx=12, pady=12
)
input_frame.pack(fill="x", padx=20, pady=12)

tk.Label(input_frame, text="Normal stress X (sigma_x)").grid(
    row=0, column=0, padx=8, pady=8, sticky="w"
)
entry_x = tk.Entry(input_frame, width=20)
entry_x.grid(row=0, column=1, padx=8, pady=8)

tk.Label(input_frame, text="Normal stress Y (sigma_y)").grid(
    row=0, column=2, padx=8, pady=8, sticky="w"
)
entry_y = tk.Entry(input_frame, width=20)
entry_y.grid(row=0, column=3, padx=8, pady=8)

tk.Label(input_frame, text="Shear stress (tau_xy)").grid(
    row=1, column=0, padx=8, pady=8, sticky="w"
)
entry_tau = tk.Entry(input_frame, width=20)
entry_tau.grid(row=1, column=1, padx=8, pady=8)

tk.Label(input_frame, text="Yield strength (Sy)").grid(
    row=1, column=2, padx=8, pady=8, sticky="w"
)
entry_yield = tk.Entry(input_frame, width=20)
entry_yield.grid(row=1, column=3, padx=8, pady=8)

tk.Label(input_frame, text="Poisson ratio").grid(
    row=2, column=0, padx=8, pady=8, sticky="w"
)
entry_poisson = tk.Entry(input_frame, width=20)
entry_poisson.grid(row=2, column=1, padx=8, pady=8)

input_boxes = [entry_x, entry_y, entry_tau, entry_yield, entry_poisson]

# Buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=5)

tk.Button(
    button_frame, text="Calculate",
    command=calculate, width=15
).pack(side="left", padx=6)

tk.Button(
    button_frame, text="Clear All",
    command=clear_all, width=15
).pack(side="left", padx=6)

# Principal stresses
principal_label = tk.Label(
    window, text="Principal stresses will appear here.",
    font=("Arial", 10, "bold")
)
principal_label.pack(pady=8)

# Results table
table_frame = tk.LabelFrame(
    window, text="Failure Theory Results", padx=8, pady=8
)
table_frame.pack(fill="x", padx=20, pady=8)

result_table = ttk.Treeview(
    table_frame,
    columns=("theory", "stress", "fos", "status"),
    show="headings",
    height=6
)

result_table.heading("theory", text="Failure Theory")
result_table.heading("stress", text="Equivalent Stress (MPa)")
result_table.heading("fos", text="Factor of Safety")
result_table.heading("status", text="Status")

result_table.column("theory", width=230)
result_table.column("stress", width=190, anchor="center")
result_table.column("fos", width=150, anchor="center")
result_table.column("status", width=120, anchor="center")
result_table.pack(fill="x")

final_label = tk.Label(
    window, text="Governing theory will appear here.",
    font=("Arial", 11, "bold")
)
final_label.pack(pady=8)

# Graph area
graph_frame = tk.LabelFrame(
    window, text="Equivalent Stress Graph", padx=8, pady=8
)
graph_frame.pack(fill="both", expand=True, padx=20, pady=8)

graph = tk.Canvas(
    graph_frame, height=220, bg="white",
    highlightthickness=1, highlightbackground="gray"
)
graph.pack(fill="both", expand=True)

tk.Label(
    window,
    text="Blue bar = Safe | Orange bar = Failure | Red dashed line = Yield strength"
).pack(pady=(0, 8))

window.mainloop()
