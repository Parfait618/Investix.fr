from flask import Flask, render_template, redirect, url_for, request, session
import random
import numpy as np

app = Flask(__name__)
app.secret_key = "cle_super_secrete_pour_session"

# Liste fictive d'actions
ACTIONS = ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION5']

def generer_marche():
    """Génère des données de marché fictives avec prix, variation et volume."""
    marche = {}
    for action in ACTIONS:
        prix = round(random.uniform(10, 100), 2)
        variation = round(random.uniform(-5, 5), 2)
        volume = random.randint(1000, 100000)
        marche[action] = {'prix': prix, 'variation': variation, 'volume': volume}
    return marche

def strategie_simple(marche, portefeuille, solde):
    """Stratégie très simple : achète si variation < -1%, vend si > 2%."""
    actions_a_acheter = {}
    actions_a_vendre = {}

    for action, data in marche.items():
        prix = data['prix']
        var = data['variation']
        quantite_possedee = portefeuille.get(action, 0)

        if var < -1 and solde >= prix * 1:  # achète 1 action si baisse > 1%
            actions_a_acheter[action] = 1
        elif var > 2 and quantite_possedee > 0:  # vend toutes les actions si hausse > 2%
            actions_a_vendre[action] = quantite_possedee

    return actions_a_acheter, actions_a_vendre

@app.route("/")
def index():
    if "solde" not in session:
        # Solde initial 10 000 €
        session['solde'] = 10000.0
        session['portefeuille'] = {}
        session['cycle'] = 0
        session['historique'] = []

    return redirect(url_for('simulation'))

@app.route("/simulation", methods=['GET', 'POST'])
def simulation():
    solde = session.get('solde', 10000.0)
    portefeuille = session.get('portefeuille', {})
    cycle = session.get('cycle', 0)
    historique = session.get('historique', [])

    marche = generer_marche()

    achats, ventes = strategie_simple(marche, portefeuille, solde)

    # Exécuter ventes
    for action, quantite in ventes.items():
        prix = marche[action]['prix']
        solde += prix * quantite
        portefeuille[action] = portefeuille.get(action, 0) - quantite
        if portefeuille[action] <= 0:
            del portefeuille[action]
        historique.append(f"Vente : {quantite} x {action} à {prix}€")

    # Exécuter achats
    for action, quantite in achats.items():
        prix = marche[action]['prix']
        cout = prix * quantite
        if solde >= cout:
            solde -= cout
            portefeuille[action] = portefeuille.get(action, 0) + quantite
            historique.append(f"Achat : {quantite} x {action} à {prix}€")

    cycle += 1

    session['solde'] = round(solde, 2)
    session['portefeuille'] = portefeuille
    session['cycle'] = cycle
    session['historique'] = historique[-10:]  # garder les 10 dernières actions

    return render_template("simulation.html", 
                           cycle=cycle, 
                           solde=round(solde, 2), 
                           portefeuille=portefeuille, 
                           marche=marche, 
                           historique=historique[-10:])

if __name__ == "__main__":
    app.run(debug=True)
