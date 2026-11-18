"""
apriori_model.py
================
Discovers association rules between products using a simplified Apriori approach.
Also provides next-item prediction using a first-order Markov chain built from
per-user purchase sequences.

How it works (plain English):
  1. Read every transaction (basket) from the CSV.
  2. Count how often each item and each pair of items appear.
  3. If a pair appears often enough (min_support), check how reliable
     the rule "A → B" is (confidence = how often B appears given A).
  4. Store rules with lift > 1 (lift means the pair appears more than by chance).
  5. Expose helpers so Flask can ask "what goes with Milk?" or "give me bundles".

Markov-chain next-item prediction:
  - Build per-user ordered purchase history (sorted by transaction ID).
  - Count how often item B follows item A across all user histories.
  - predict_next(items_bought) returns the most likely next items.
"""

import pandas as pd
from itertools import combinations
from collections import defaultdict


class AprioriModel:
    def __init__(self, data_path: str):
        self.data_path     = data_path
        self.rules         = pd.DataFrame()
        self.all_items     = set()
        # Markov transition table: {item_a: {item_b: count}}
        self._transitions  = defaultdict(lambda: defaultdict(int))
        self._item_totals  = defaultdict(int)   # how many times item_a was seen as "from"
        self._run()
        self._build_markov()

    # ── Private helpers ────────────────────────────────────────────────────────

    def _load_transactions(self) -> list:
        """Read CSV and return a list of frozensets (one per row)."""
        df = pd.read_csv(self.data_path)
        col = {c.lower(): c for c in df.columns}.get("items", df.columns[0])
        return df[col].apply(
            lambda x: frozenset(
                i.strip() for i in str(x).split(",")
                if i.strip() and i.strip().lower() != "nan"
            )
        ).tolist()

    def _get_thresholds(self, n: int):
        """Use looser thresholds for large datasets so we still get useful rules."""
        if n > 5000:
            return 0.005, 0.05
        return 0.01, 0.10

    def _run(self):
        """Full pipeline: load → count → filter → generate rules."""
        try:
            transactions = self._load_transactions()
            n = len(transactions)
            min_sup, min_conf = self._get_thresholds(n)

            item_counts: dict = defaultdict(int)
            for t in transactions:
                for item in t:
                    item_counts[frozenset([item])] += 1
                    self.all_items.add(item)

            pair_counts: dict = defaultdict(int)
            for t in transactions:
                for pair in combinations(sorted(t), 2):
                    pair_counts[frozenset(pair)] += 1

            rules_list = []
            for pair, pair_count in pair_counts.items():
                support_ab = pair_count / n
                if support_ab < min_sup:
                    continue

                a, b = list(pair)
                sup_a = item_counts[frozenset([a])] / n
                sup_b = item_counts[frozenset([b])] / n
                lift  = support_ab / (sup_a * sup_b) if (sup_a * sup_b) > 0 else 0

                conf_a = support_ab / sup_a if sup_a > 0 else 0
                if conf_a >= min_conf:
                    rules_list.append({
                        "antecedents": frozenset([a]),
                        "consequents": frozenset([b]),
                        "support":     support_ab,
                        "confidence":  conf_a,
                        "lift":        lift,
                    })

                conf_b = support_ab / sup_b if sup_b > 0 else 0
                if conf_b >= min_conf:
                    rules_list.append({
                        "antecedents": frozenset([b]),
                        "consequents": frozenset([a]),
                        "support":     support_ab,
                        "confidence":  conf_b,
                        "lift":        lift,
                    })

            self.rules = (
                pd.DataFrame(rules_list).sort_values("lift", ascending=False)
                if rules_list else pd.DataFrame()
            )

        except Exception as e:
            print(f"[Apriori] Error during analysis: {e}")
            self.rules = pd.DataFrame()

    def _build_markov(self):
        """
        Build a first-order Markov transition table from per-user purchase sequences.

        For each user, sort their transactions by TransactionID and treat the list
        of items bought across transactions as an ordered sequence.  For every
        consecutive pair (item_a → item_b) we increment the transition counter.

        If no UserID / TransactionID columns are found we fall back to using
        within-basket item ordering (alphabetical), which is a weaker signal but
        still better than nothing.
        """
        try:
            df      = pd.read_csv(self.data_path)
            col_map = {c.lower(): c for c in df.columns}

            items_col  = col_map.get("items", df.columns[0])
            user_col   = col_map.get("userid") or col_map.get("user_id") or col_map.get("user")
            tx_id_col  = col_map.get("transactionid") or col_map.get("transaction_id") or col_map.get("txid")

            # Clean items column → list of item strings
            df["_items_list"] = df[items_col].apply(
                lambda x: [i.strip() for i in str(x).split(",")
                            if i.strip() and i.strip().lower() != "nan"]
            )

            if user_col and tx_id_col:
                # Best path: use real per-user ordered transaction history
                df_sorted = df.sort_values([user_col, tx_id_col])
                for uid, grp in df_sorted.groupby(user_col):
                    # Flatten all items bought by this user in order of purchase
                    history = [item for items in grp["_items_list"] for item in items]
                    for a, b in zip(history, history[1:]):
                        self._transitions[a][b] += 1
                        self._item_totals[a] += 1
            else:
                # Fallback: within-basket consecutive pairs (alphabetical order)
                for items in df["_items_list"]:
                    for a, b in zip(items, items[1:]):
                        self._transitions[a][b] += 1
                        self._item_totals[a] += 1

            print(f"[Markov] Transition table built: {len(self._transitions)} source items")

        except Exception as e:
            print(f"[Markov] Error building transition table: {e}")

    # ── Public API ─────────────────────────────────────────────────────────────

    def recommend(self, item: str) -> list:
        """Return items that are frequently bought with `item`."""
        if self.rules.empty:
            return []
        item = item.strip()
        result = set()
        for _, row in self.rules.iterrows():
            if item in row["antecedents"]:
                result.update(row["consequents"])
        return sorted(result)

    def get_bundles(self, n: int = 5) -> list:
        """Return top-n unique product bundles (pairs with highest lift)."""
        if self.rules.empty:
            return []
        seen, bundles = set(), []
        for _, row in self.rules.iterrows():
            bundle = tuple(sorted(row["antecedents"] | row["consequents"]))
            if bundle not in seen:
                seen.add(bundle)
                bundles.append(list(bundle))
            if len(bundles) >= n:
                break
        return bundles

    def get_top_rules_chart_data(self, top_n: int = 8) -> dict:
        """Return label / confidence / lift lists for the chart."""
        if self.rules.empty:
            return {"labels": [], "confidence": [], "lift": []}
        top = self.rules.head(top_n)
        labels = [
            f"{list(r.antecedents)[0][:10]}→{list(r.consequents)[0][:10]}"
            for _, r in top.iterrows()
        ]
        return {
            "labels":     labels,
            "confidence": [round(float(c), 3) for c in top["confidence"]],
            "lift":       [round(float(l), 3) for l in top["lift"]],
        }

    def predict_next(self, purchased_items: list, top_n: int = 5) -> list:
        """
        Predict the most likely next item(s) a user will buy, given their
        purchase history (list of item names).

        Strategy (layered):
          1. Markov chain: for each item already bought, look up what tends to
             follow it and accumulate weighted scores.  Weight = transition
             probability (count / total outgoing from that item).  More-recently
             purchased items get a 2× recency boost.
          2. If the Markov table is empty or gives no results, fall back to
             Apriori co-occurrence rules (confidence-weighted).
          3. Filter out items the user already owns.

        Returns a list of (item, probability_pct, source_label) tuples, e.g.:
          [("Bread", 38.5, "Sequence Pattern"), ("Milk", 22.1, "Co-occurrence"), …]
        """
        if not purchased_items:
            return []

        bought_set  = {i.strip() for i in purchased_items}
        scores: dict = {}
        source: dict = {}

        # ── Layer 1: Markov transitions ────────────────────────────────────────
        n_items = len(purchased_items)
        for rank, item in enumerate(reversed(purchased_items)):
            item = item.strip()
            if item not in self._transitions:
                continue
            total_out = self._item_totals.get(item, 1)
            recency_w = 2.0 if rank == 0 else 1.0   # boost the most recent item
            for next_item, count in self._transitions[item].items():
                if next_item in bought_set:
                    continue
                prob = (count / total_out) * recency_w
                scores[next_item]  = scores.get(next_item, 0) + prob
                source[next_item]  = "Sequence Pattern"

        # ── Layer 2: Apriori rules fallback / boost ────────────────────────────
        if not scores and not self.rules.empty:
            for item in purchased_items:
                item = item.strip()
                for _, row in self.rules.iterrows():
                    if item in row["antecedents"]:
                        for c in row["consequents"]:
                            if c in bought_set:
                                continue
                            scores[c]  = scores.get(c, 0) + float(row["confidence"])
                            source[c]  = "Co-occurrence Rule"

        if not scores:
            return []

        # Normalise to percentage
        total = sum(scores.values())
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result = []
        for item, score in ranked:
            pct = round((score / total) * 100, 1)
            result.append({
                "item":   item,
                "pct":    pct,
                "source": source.get(item, "Pattern"),
            })
        return result
