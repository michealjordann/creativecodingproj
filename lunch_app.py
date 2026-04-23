import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import json
#AI helped us with incorporation of json and csv files which was like 5 lines of code total throughout
meals_csv = "meals.csv"
votes_json = "votes.json"
past_json = "history.json"
max_price = 5.00


def load_meals():
    meals = []
  # AI used for this if statement to help us make similar ones
    if os.path.exists(meals_csv):
        with open(meals_csv, newline="") as f:
            for row in csv.DictReader(f):
                meals.append(row)
    return meals

def save_meals(meals):
    if not meals:
        return
      # AI used here, also to help make other statements like this
    with open(meals_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=meals[0].keys())
        writer.writeheader()
        writer.writerows(meals)

def load_votes():
    if os.path.exists(votes_json):
        with open(votes_json) as f:
            return json.load(f)
    return {}

def save_votes(v):
    with open(votes_json, "w") as f:
        json.dump(v, f)

def load_past():
    if os.path.exists(past_json):
        with open(past_json) as f:
            return json.load(f)
    return []

def save_past(h):
    with open(past_json, "w") as f:
        json.dump(h, f)


def get_scores(meals, votes, past):
    scores = {}
    recent = past[-3:]
    top_votes = max(votes.values()) if votes else 1

    for meal in meals:
        name = meal["name"]

        if meal.get("available", "yes").lower() == "no":
            continue
#AI used here
        try:
            cost = float(meal.get("cost", 0))
        except ValueError:
            cost = 0
        if cost > max_price:
            continue

        score = 0
        breakdown = {}

        vote_count = votes.get(name, 0)
        pop_pts = int((vote_count / top_votes) * 40)
        score += pop_pts
        breakdown["Popularity (votes)"] = f"+{pop_pts}"
# AI only used to help with try and except statement
        try:
            nutrition = int(meal.get("nutrition", 5))
        except ValueError:
            nutrition = 5
        nut_pts = int((nutrition / 10) * 30)
        score += nut_pts
        breakdown["Nutrition score"] = f"+{nut_pts}"

        if meal.get("local_partner", "no").lower() == "yes":
            score += 15
            breakdown["Local biz bonus"] = "+15"
        else:
            breakdown["Local biz bonus"] = "+0"

        budget_pts = int(((max_price - cost) / max_price) * 10)
        score += budget_pts
        breakdown["Budget friendly"] = f"+{budget_pts}"

        penalty = recent.count(name) * 20
        score -= penalty
        breakdown["Repeat penalty"] = f"-{penalty}" if penalty > 0 else "0"

        scores[name] = {"score": score, "breakdown": breakdown, "votes": vote_count}

    return scores

# GUI (AI used a lot with this part, but not for making buttons, text or the actual window)
votes = load_votes()
already_voted = False

window = tk.Tk()
window.title("Emerald High Lunch System")
window.geometry("570x540")
window.configure(bg="#1a5276")

tk.Label(window, text="Emerald High Lunch System", font=("Helvetica", 16, "bold"), bg="#1a5276", fg="white").pack(pady=(12, 0))
tk.Label(window, text="smart lunch decisions for EHS  |  budget $5.00 max", font=("Helvetica", 9), bg="#1a5276", fg="#aed6f1").pack(pady=(0, 8))

notebook = ttk.Notebook(window)
notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

vote_tab    = tk.Frame(notebook, bg="white")
results_tab = tk.Frame(notebook, bg="white")
pick_tab    = tk.Frame(notebook, bg="white")
meals_tab   = tk.Frame(notebook, bg="white")

notebook.add(vote_tab,    text="  Vote  ")
notebook.add(results_tab, text="  Results  ")
notebook.add(pick_tab,    text="  Today's Pick  ")
notebook.add(meals_tab,   text="  Edit Meals  ")


tk.Label(vote_tab, text="What should we have for lunch?", font=("Helvetica", 12, "bold"), bg="white").pack(pady=10)

vote_var = tk.StringVar()
vote_frame = tk.Frame(vote_tab, bg="white")
vote_frame.pack()

def refresh_vote():
    for w in vote_frame.winfo_children():
        w.destroy()
    vote_var.set("")
    for meal in load_meals():
        if meal.get("available", "yes").lower() == "yes":
            tk.Radiobutton(vote_frame, text=f"{meal['name']}  —  {meal['vendor']}", variable=vote_var, value=meal["name"], bg="white", fg="black", font=("Helvetica", 11)).pack(anchor="w", pady=3, padx=20)

def submit_vote():
    global already_voted
    if already_voted:
        messagebox.showwarning("Already voted!", "You already voted today!")
        return
    choice = vote_var.get()
    if not choice:
        messagebox.showwarning("Oops", "Pick a meal first!")
        return
    votes[choice] = votes.get(choice, 0) + 1
    save_votes(votes)
    already_voted = True
    refresh_results()
    messagebox.showinfo("Voted!", f"You voted for {choice}!")
    vote_var.set("")

tk.Button(vote_tab, text="Submit Vote", command=submit_vote, bg="#1a5276", fg="black", font=("Helvetica", 10), padx=8, pady=4, relief="flat", highlightbackground="#1a5276").pack(pady=12)


tk.Label(results_tab, text="Current Standings:", font=("Helvetica", 12, "bold"), bg="white").pack(pady=10)

results_list = tk.Listbox(results_tab, width=50, height=12, font=("Helvetica", 11))
results_list.pack(padx=10)

def refresh_results():
    results_list.delete(0, tk.END)
    current_votes = load_votes()
    sorted_votes = sorted(current_votes.items(), key=lambda x: x[1], reverse=True)
    if not sorted_votes:
        results_list.insert(tk.END, "  No votes yet!")
        return
    for meal, count in sorted_votes:
        results_list.insert(tk.END, f"  {meal}: {count} vote{'s' if count != 1 else ''}")

tk.Button(results_tab, text="Refresh", command=refresh_results, bg="#1a5276", fg="white", font=("Helvetica", 10), padx=8, pady=4, relief="flat").pack(pady=6)


tk.Label(pick_tab, text="Today's Lunch Decision", font=("Helvetica", 12, "bold"), bg="white").pack(pady=8)
tk.Label(pick_tab, text="scores: votes (40pts) + nutrition (30pts) + local biz (15pts) + budget (10pts) - repeats", font=("Helvetica", 8), bg="white", fg="gray", wraplength=500).pack()

pick_result_label = tk.Label(pick_tab, text="", font=("Helvetica", 14, "bold"), bg="white", fg="#1a5276", wraplength=480)
pick_result_label.pack(pady=8)

breakdown_frame = tk.Frame(pick_tab, bg="white")
breakdown_frame.pack(padx=20, fill="x")

history_label = tk.Label(pick_tab, text="", font=("Helvetica", 9), bg="white", fg="gray")
history_label.pack(pady=(8, 0))

def run_decision():
    scores = get_scores(load_meals(), load_votes(), load_past())

    for w in breakdown_frame.winfo_children():
        w.destroy()

    if not scores:
        pick_result_label.config(text="No meals available or all over budget :(")
        return

    winner = max(scores, key=lambda x: scores[x]["score"])
    pick_result_label.config(text=f"Today's Pick:  {winner}")

    tk.Label(breakdown_frame, text="Score breakdown for winner:", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w")
    for factor, pts in scores[winner]["breakdown"].items():
        tk.Label(breakdown_frame, text=f"     {factor}: {pts} pts", font=("Helvetica", 10), bg="white").pack(anchor="w")
    tk.Label(breakdown_frame, text=f"     TOTAL: {scores[winner]['score']} pts", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w", pady=(4, 0))

    tk.Label(breakdown_frame, text="\nAll eligible meals:", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w")
    for name, data in sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True):
        tk.Label(breakdown_frame, text=f"     {name}: {data['score']} pts  ({data['votes']} votes)", font=("Helvetica", 10), bg="white").pack(anchor="w")

    recent = load_past()[-5:]
    history_label.config(text=f"Recent picks: {' → '.join(recent)}" if recent else "Recent picks: none yet")

def confirm_pick():
    global already_voted
    scores = get_scores(load_meals(), load_votes(), load_past())
    if not scores:
        messagebox.showwarning("No meals", "No eligible meals to pick!")
        return
    winner = max(scores, key=lambda x: scores[x]["score"])
    if messagebox.askyesno("Confirm?", f"Serve '{winner}' today and reset votes for tomorrow?"):
        past = load_past()
        past.append(winner)
        save_past(past)
        save_votes({})
        votes.clear()
        already_voted = False
        refresh_results()
        run_decision()
        messagebox.showinfo("Done!", f"{winner} is today's lunch!\nVotes have been reset.")

btn_frame = tk.Frame(pick_tab, bg="white")
btn_frame.pack(pady=8)
tk.Button(btn_frame, text="Run Decision Engine", command=run_decision, bg="#1a5276", fg="white", font=("Helvetica", 10), padx=8, pady=4, relief="flat").grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Confirm & Reset Votes", command=confirm_pick, bg="#1a5276", fg="white", font=("Helvetica", 10), padx=8, pady=4, relief="flat").grid(row=0, column=1, padx=5)


tk.Label(meals_tab, text="Manage Meals:", font=("Helvetica", 12, "bold"), bg="white").pack(pady=8)

meals_list = tk.Listbox(meals_tab, width=58, height=6, font=("Helvetica", 10))
meals_list.pack(padx=10)
tk.Label(meals_tab, text="NS = nutrition score  |  scroll to see all meals", font=("Helvetica", 8), bg="white", fg="gray").pack()

def refresh_meals_list():
    meals_list.delete(0, tk.END)
    for m in load_meals():
        avail = "ON " if m.get("available", "yes").lower() == "yes" else "OFF"
        local = "[local]" if m.get("local_partner", "no").lower() == "yes" else ""
        meals_list.insert(tk.END, f"  [{avail}]  {m['name']} — {m['vendor']}  NS:{m.get('nutrition','?')}  ${m.get('cost','?')}  {local}")

tk.Label(meals_tab, text="Add new meal:", font=("Helvetica", 10, "bold"), bg="white").pack(pady=(8, 0))

form = tk.Frame(meals_tab, bg="white")
form.pack(pady=6)

tk.Label(form, text="Name:", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=3)
tk.Label(form, text="Vendor:", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=0, column=1, padx=3)
tk.Label(form, text="NS (1-10):", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=3)
tk.Label(form, text="Cost ($):", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=0, column=3, padx=3)

name_entry      = tk.Entry(form, width=14)
vendor_entry    = tk.Entry(form, width=14)
nutrition_entry = tk.Entry(form, width=6)
cost_entry      = tk.Entry(form, width=6)

name_entry.grid(row=1, column=0, padx=3)
vendor_entry.grid(row=1, column=1, padx=3)
nutrition_entry.grid(row=1, column=2, padx=3)
cost_entry.grid(row=1, column=3, padx=3)

def add_meal():
    name   = name_entry.get().strip()
    vendor = vendor_entry.get().strip()
    if not name or not vendor:
        messagebox.showwarning("Missing info", "Need at least a name and vendor!")
        return
    is_local = messagebox.askyesno("Local partner?", f"Is '{vendor}' a local business partner?")
    current = load_meals()
    current.append({
        "name": name,
        "vendor": vendor,
        "nutrition": nutrition_entry.get().strip() or "5",
        "cost": cost_entry.get().strip() or "4.00",
        "local_partner": "yes" if is_local else "no",
        "available": "yes"
    })
    save_meals(current)
    name_entry.delete(0, tk.END)
    vendor_entry.delete(0, tk.END)
    nutrition_entry.delete(0, tk.END)
    cost_entry.delete(0, tk.END)
    refresh_meals_list()
    refresh_vote()

def toggle_available():
    sel = meals_list.curselection()
    if not sel:
        messagebox.showwarning("Select one", "Click a meal in the list first!")
        return
    current = load_meals()
    m = current[sel[0]]
    m["available"] = "no" if m.get("available", "yes").lower() == "yes" else "yes"
    save_meals(current)
    refresh_meals_list()
    refresh_vote()

def delete_meal():
    sel = meals_list.curselection()
    if not sel:
        messagebox.showwarning("Select one", "Click a meal to delete!")
        return
    current = load_meals()
    name = current[sel[0]]["name"]
    if messagebox.askyesno("Delete?", f"Delete '{name}'?"):
        current.pop(sel[0])
        save_meals(current)
        refresh_meals_list()
        refresh_vote()

meal_btns = tk.Frame(meals_tab, bg="white")
meal_btns.pack(pady=4)
tk.Button(meal_btns, text="Add Meal", command=add_meal, bg="#1a5276", fg="white", font=("Helvetica", 10), padx=8, pady=4, relief="flat").grid(row=0, column=0, padx=4)
tk.Button(meal_btns, text="Toggle Available", command=toggle_available, bg="#1a5276", fg="white", font=("Helvetica", 10), padx=8, pady=4, relief="flat").grid(row=0, column=1, padx=4)
tk.Button(meal_btns, text="Delete Meal", command=delete_meal, bg="#1a5276", fg="white", font=("Helvetica", 10), padx=8, pady=4, relief="flat").grid(row=0, column=2, padx=4)


refresh_vote()
refresh_results()
refresh_meals_list()

window.mainloop()
